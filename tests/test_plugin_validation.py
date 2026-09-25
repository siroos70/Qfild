import os
import sys
import traceback

_PLUGIN_DIR = "F:\\QGIS_script\\desktop\\GeoSurveyDesktop"
_PROJECT_ROOT = "F:\\QGIS_script"
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _PLUGIN_DIR not in sys.path:
    sys.path.insert(0, _PLUGIN_DIR)

print("=" * 60)
print("QGIS 4.2.1 Plugin Validation Test")
print("=" * 60)

errors = []
warnings = []

# Test 1: Import all modules
print("\n[1] Importing all plugin modules...")
modules = [
    "cogo_engine", "qc_engine", "survey_manager", "job_manager",
    "import_export", "settings_manager", "cogo_dialog", "qc_dialog",
    "job_dialog", "import_dialog", "export_dialog", "settings_dialog",
    "survey_dock"
]
for mod_name in modules:
    try:
        mod = __import__(mod_name)
        print("  OK: " + mod_name)
    except Exception as e:
        errors.append("Import " + mod_name + " failed: " + str(e))
        print("  FAIL: " + mod_name + " - " + str(e))

# Test 2: Check metadata
print("\n[2] Checking metadata.txt...")
meta_path = os.path.join(_PLUGIN_DIR, "metadata.txt")
if os.path.exists(meta_path):
    with open(meta_path, "r") as f:
        content = f.read()
    required = ["name=", "version=", "qgisMinimumVersion=", "author=", "category=", "icon=", "about="]
    for req in required:
        if req in content:
            print("  OK: metadata contains " + req)
        else:
            warnings.append("metadata missing " + req)
            print("  WARN: metadata missing " + req)
else:
    errors.append("metadata.txt not found")
    print("  FAIL: metadata.txt not found")

# Test 3: Check icon
print("\n[3] Checking icon...")
icon_path = os.path.join(_PLUGIN_DIR, "icons", "survey_icon.svg")
if os.path.exists(icon_path):
    with open(icon_path, "r") as f:
        svg = f.read()
    if svg.startswith("<?xml") or svg.startswith("<svg"):
        print("  OK: valid SVG icon")
    else:
        warnings.append("icon may not be valid SVG")
        print("  WARN: icon may not be valid SVG")
else:
    errors.append("icon not found")
    print("  FAIL: icon not found")

# Test 4: Check class factory
print("\n[4] Checking class factory...")
try:
    import __init__ as plugin_init
    if hasattr(plugin_init, "classFactory"):
        print("  OK: classFactory exists")
    else:
        errors.append("classFactory not found")
        print("  FAIL: classFactory not found")
except Exception as e:
    errors.append("plugin __init__ import failed: " + str(e))
    print("  FAIL: " + str(e))

# Test 5: Check COGO engine
print("\n[5] Testing COGO engine...")
try:
    from cogo_engine import COGOEngine
    engine = COGOEngine()
    from shared.coordinate_rules import Point
    result = engine.compute_point_from_bearing_distance(Point(500000, 3000000), 35.3361, 25.450)
    if result.success:
        print("  OK: COGO bearing+distance works")
    else:
        errors.append("COGO bearing+distance failed")
        print("  FAIL: COGO bearing+distance failed")
except Exception as e:
    errors.append("COGO engine test failed: " + str(e))
    print("  FAIL: " + str(e))

# Test 6: Check QC engine
print("\n[6] Testing QC engine...")
try:
    from qc_engine import QCEngine
    qc = QCEngine()
    results = qc.run_gnss_qc(accuracy=0.045, hdop=1.2, fix_type="RTK FIXED",
                              satellite_count=12)
    if results:
        print("  OK: QC GNSS check works (" + str(len(results)) + " results)")
    else:
        warnings.append("QC returned no results")
        print("  WARN: QC returned no results")
except Exception as e:
    errors.append("QC engine test failed: " + str(e))
    print("  FAIL: " + str(e))

# Test 7: Check survey manager
print("\n[7] Testing SurveyManager...")
try:
    from survey_manager import SurveyManager
    class FakeIface:
        def activeLayer(self):
            return None
    sm = SurveyManager(FakeIface())
    layer = sm.create_survey_layer("TestLayer", "Point", "EPSG:32639")
    if layer is not None:
        print("  OK: Survey layer creation works")
    else:
        warnings.append("Survey layer creation returned None")
        print("  WARN: Survey layer creation returned None")
except Exception as e:
    errors.append("SurveyManager test failed: " + str(e))
    print("  FAIL: " + str(e))

# Test 8: Check job manager
print("\n[8] Testing JobManager...")
try:
    from job_manager import JobManager
    jm = JobManager()
    job = jm.create_job("TestJob", "TestProject", "TestArea", "EPSG:32639")
    if job.id:
        print("  OK: Job creation works (ID: " + job.id + ")")
    else:
        errors.append("Job creation failed")
        print("  FAIL: Job creation failed")
except Exception as e:
    errors.append("JobManager test failed: " + str(e))
    print("  FAIL: " + str(e))

# Test 9: Check import/export
print("\n[9] Testing ImportExport...")
try:
    from import_export import ImportExportManager
    class FakeIface2:
        def legendInterface(self):
            return None
    iem = ImportExportManager(FakeIface2())
    print("  OK: ImportExportManager instantiable")
except Exception as e:
    errors.append("ImportExport test failed: " + str(e))
    print("  FAIL: " + str(e))

# Test 10: Check settings
print("\n[10] Testing SettingsManager...")
try:
    from settings_manager import SettingsManager
    sm2 = SettingsManager()
    val = sm2.get("default_crs")
    if val:
        print("  OK: Settings works (default_crs=" + str(val) + ")")
    else:
        warnings.append("Settings returned None")
        print("  WARN: Settings returned None")
except Exception as e:
    errors.append("Settings test failed: " + str(e))
    print("  FAIL: " + str(e))

# Summary
print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
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
    print("\nRESULT: PASS - All critical checks passed")
else:
    print("\nRESULT: FAIL - " + str(len(errors)) + " errors found")