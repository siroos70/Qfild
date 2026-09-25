# -*- coding: utf-8 -*-
"""Settings for GeoSurvey Desktop"""
import os, sys, json
from typing import Dict, Any

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsSettings


DEFAULT_SETTINGS = {
    "coordinate_display_mode": "XY",
    "default_crs": "EPSG:32639",
    "default_accuracy_threshold": 0.05,
    "default_hdop_threshold": 1.5,
    "default_min_satellites": 4,
    "auto_save_interval": 300,
    "language": "fa",
    "show_grid": True,
    "show_crosshair": True,
    "survey_layer_color": "#FFB300",
    "survey_layer_name": "Survey_Points",
    "log_level": "INFO",
    "enable_audit": True,
    "offline_mode": False,
    "sync_endpoint": "",
    "sync_token": "",
}


class SettingsManager:
    """Settings manager for GeoSurvey Desktop."""

    def __init__(self):
        self._settings = DEFAULT_SETTINGS.copy()
        self._qsettings = QgsSettings()

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def set(self, key, value):
        self._settings[key] = value
        self._qsettings.setValue(f"GeoSurveyDesktop/{key}", value)

    def save(self):
        for key, value in self._settings.items():
            self._qsettings.setValue(f"GeoSurveyDesktop/{key}", value)

    def load(self):
        for key in DEFAULT_SETTINGS:
            val = self._qsettings.value(f"GeoSurveyDesktop/{key}", DEFAULT_SETTINGS[key])
            self._settings[key] = val

    def reset(self):
        self._settings = DEFAULT_SETTINGS.copy()

    def get_all(self):
        return self._settings.copy()

    def get_accuracy_rules(self):
        return {
            "max_accuracy": self.get("default_accuracy_threshold", 0.05),
            "max_hdop": self.get("default_hdop_threshold", 1.5),
            "min_satellites": self.get("default_min_satellites", 4),
        }