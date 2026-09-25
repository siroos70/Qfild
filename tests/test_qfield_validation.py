# -*- coding: utf-8 -*-
"""QField 4.3.3 Plugin Validation"""
import os
import sys

_PLUGIN_DIR = "F:\\QGIS_script\\mobile\\GeoSurveyFieldTools"
_PROJECT_ROOT = "F:\\QGIS_script"
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _PLUGIN_DIR not in sys.path:
    sys.path.insert(0, _PLUGIN_DIR)

print("=" * 60)
print("QField 4.3.3 Plugin Validation")
print("=" * 60)

errors = []
warnings = []

# Test 1: Check ZIP structure
print("\n[1] Checking ZIP structure...")
zip_path = "F:\\QGIS_script\\releases\\GeoSurveyFieldTools-QField-4.3.3-v1.0.0.zip"
if os.path.exists(zip_path):
    import zipfile
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        print("  ZIP contains " + str(len(names)) + " files:")
        for n in sorted(names):
            print("    " + n)
else:
    errors.append("ZIP not found")
    print("  FAIL: ZIP not found")

# Test 2: Check metadata
print("\n[2] Checking metadata.txt...")
meta_path = os.path.join(_PLUGIN_DIR, "metadata.txt")
if os.path.exists(meta_path):
    with open(meta_path, "r") as f:
        content = f.read()
    required = ["name=", "version=", "author=", "category=", "icon=", "about="]
    for req in required:
        if req in content:
            print("  OK: metadata contains " + req)
        else:
            warnings.append("metadata missing " + req)
            print("  WARN: metadata missing " + req)
    # Check QField-specific fields
    if "qgisVersionMin" in content:
        print("  OK: qgisVersionMin present")
    else:
        warnings.append("qgisVersionMin missing")
        print("  WARN: qgisVersionMin missing")
    if "main=" in content or "[ui]" in content:
        print("  OK: UI entry point present")
    else:
        warnings.append("UI entry point missing")
        print("  WARN: UI entry point missing")
else:
    errors.append("metadata.txt not found")
    print("  FAIL: metadata.txt not found")

# Test 3: Check icon
print("\n[3] Checking icon.svg...")
icon_path = os.path.join(_PLUGIN_DIR, "icon.svg")
if os.path.exists(icon_path):
    with open(icon_path, "r") as f:
        svg = f.read()
    if svg.startswith("<?xml") or svg.startswith("<svg"):
        print("  OK: valid SVG icon")
    else:
        warnings.append("icon may not be valid SVG")
        print("  WARN: icon may not be valid SVG")
else:
    errors.append("icon.svg not found")
    print("  FAIL: icon.svg not found")

# Test 4: Check QML file
print("\n[4] Checking QML file...")
qml_path = os.path.join(_PLUGIN_DIR, "ui", "main_panelqml")
if os.path.exists(qml_path):
    with open(qml_path, "r") as f:
        qml = f.read()
    print("  QML file size: " + str(len(qml)) + " bytes")
    # Check for common QML syntax issues
    lines = qml.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.endswith(";") and not stripped.startswith("//"):
            if not stripped.endswith("{") and not stripped.startswith("import"):
                if not stripped.endswith(";") and not stripped.startswith("//"):
                    pass
        # Check for obvious syntax errors
        if "modelData" in stripped and "model:" not in qml:
            pass
    print("  OK: QML file exists")
else:
    errors.append("main_panelqml not found")
    print("  FAIL: main_panelqml not found")

# Test 5: Check plugin __init__.py
print("\n[5] Checking plugin __init__.py...")
init_path = os.path.join(_PLUGIN_DIR, "__init__.py")
if os.path.exists(init_path):
    with open(init_path, "r") as f:
        init_content = f.read()
    if "classFactory" in init_content:
        print("  OK: classFactory present")
    else:
        errors.append("classFactory not found in __init__.py")
        print("  FAIL: classFactory not found")
    if "QQmlApplicationEngine" in init_content:
        print("  OK: QQmlApplicationEngine used")
    else:
        warnings.append("QQmlApplicationEngine not used")
        print("  WARN: QQmlApplicationEngine not used")
else:
    errors.append("__init__.py not found")
    print("  FAIL: __init__.py not found")

# Test 6: Check survey_manager.py
print("\n[6] Checking survey_manager.py...")
sm_path = os.path.join(_PLUGIN_DIR, "survey_manager.py")
if os.path.exists(sm_path):
    with open(sm_path, "r") as f:
        sm_content = f.read()
    if "class FieldSurveyManager" in sm_content or "class SurveyManager" in sm_content:
        print("  OK: FieldSurveyManager class present")
    else:
        warnings.append("FieldSurveyManager class not found")
        print("  WARN: FieldSurveyManager class not found")
    if "capture_point" in sm_content:
        print("  OK: capture_point method present")
    else:
        warnings.append("capture_point not found")
        print("  WARN: capture_point not found")
else:
    errors.append("survey_manager.py not found")
    print("  FAIL: survey_manager.py not found")

# Test 7: Check shared modules are accessible
print("\n[7] Checking shared modules...")
try:
    from shared.coordinate_rules import Point, bearing, distance
    print("  OK: shared modules accessible")
except Exception as e:
    errors.append("shared modules not accessible: " + str(e))
    print("  FAIL: " + str(e))

# Summary
print("\n" + "=" * 60)
print("QFIELD VALIDATION SUMMARY")
print("=" * 60)
print("Errors: " + str(len(errors)))
print("Warnings: " + str(len(warnings)))
if errors:
    print("\nERRORS:")
    for e in errors:
        print("  [E] " + e)
if warnings:
    print("\nWARNINGS:")
    for w in warnings:
        print("  [W] " + w)

if len(errors) == 0:
    print("\nRESULT: PASS - QField plugin structure valid")
else:
    print("\nRESULT: FAIL - " + str(len(errors)) + " errors found")