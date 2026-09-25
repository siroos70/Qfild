# -*- coding: utf-8 -*-
"""Plugin for QField 4.3.3"""
import os
import sys

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.PyQt.QtCore import QCoreApplication, QObject
from qgis.PyQt.QtQml import QQmlApplicationEngine


class GeoSurveyFieldToolsPlugin(QObject):
    """QField Plugin implementation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._engine = None
        self._main_window = None
        self._survey_manager = None
        self._init_modules()

    def _init_modules(self):
        try:
            from .survey_manager import FieldSurveyManager
            self._survey_manager = FieldSurveyManager()
        except Exception as e:
            print("FieldSurveyManager init failed: " + str(e))

    def initGui(self):
        """Initialize plugin GUI for QField."""
        try:
            self._engine = QQmlApplicationEngine()
            qml_file = os.path.join(_PLUGIN_DIR, "ui", "main_panelqml")
            self._engine.load(qml_file)
            roots = self._engine.rootObjects()
            self._main_window = roots[0] if roots else None
        except Exception as e:
            print("GUI init failed: " + str(e))

    def unload(self):
        """Cleanup."""
        if self._engine:
            self._engine.deleteLater()
            self._engine = None

    def get_survey_manager(self):
        return self._survey_manager


def classFactory(iface=None):
    """Plugin factory."""
    return GeoSurveyFieldToolsPlugin()