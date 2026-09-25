# -*- coding: utf-8 -*-
"""
GeoSurveyDesktop QGIS Plugin
Enterprise Survey & GIS Control Center for QGIS Desktop 4.2.1
"""
import os
import sys

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QMenu, QAction
from qgis.core import QgsApplication
from qgis.gui import QgsMessageBar
import qgis.utils


class GeoSurveyDesktopPlugin:
    """QGIS Plugin implementation class."""

    def __init__(self, iface):
        self.iface = iface
        self.menu = QMenu("GeoSurvey", self.iface.mainWindow())
        self.actions = []
        self._dock = None
        self._cogo_engine = None
        self._qc_engine = None
        self._survey_manager = None
        self._init_modules()

    def _init_modules(self):
        try:
            from cogo_engine import COGOEngine
            self._cogo_engine = COGOEngine()
        except Exception as e:
            self._log_error("COGO engine init failed: " + str(e))

        try:
            from qc_engine import QCEngine
            self._qc_engine = QCEngine()
        except Exception as e:
            self._log_error("QC engine init failed: " + str(e))

        try:
            from survey_manager import SurveyManager
            self._survey_manager = SurveyManager(self.iface)
        except Exception as e:
            self._log_error("Survey manager init failed: " + str(e))

    def _log_error(self, message):
        try:
            self.iface.messageBar().pushMessage(
                "GeoSurvey", message, QgsMessageBar.WARNING, 5
            )
        except Exception:
            pass

    def initGui(self):
        """Initialize the plugin GUI."""
        try:
            self.survey_action = QAction(
                QCoreApplication.translate("GeoSurvey", "GeoSurvey Survey"),
                self.iface.mainWindow()
            )
            self.survey_action.setCheckable(True)
            self.survey_action.triggered.connect(self.toggle_dock)

            self.cogo_action = QAction(
                QCoreApplication.translate("GeoSurvey", "COGO Calculator"),
                self.iface.mainWindow()
            )
            self.cogo_action.triggered.connect(self.open_cogo)

            self.qc_action = QAction(
                QCoreApplication.translate("GeoSurvey", "QC Engine"),
                self.iface.mainWindow()
            )
            self.qc_action.triggered.connect(self.open_qc)

            self.job_action = QAction(
                QCoreApplication.translate("GeoSurvey", "Job Manager"),
                self.iface.mainWindow()
            )
            self.job_action.triggered.connect(self.open_job_manager)

            self.import_action = QAction(
                QCoreApplication.translate("GeoSurvey", "Import Data"),
                self.iface.mainWindow()
            )
            self.import_action.triggered.connect(self.open_import)

            self.export_action = QAction(
                QCoreApplication.translate("GeoSurvey", "Export Data"),
                self.iface.mainWindow()
            )
            self.export_action.triggered.connect(self.open_export)

            self.settings_action = QAction(
                QCoreApplication.translate("GeoSurvey", "Settings"),
                self.iface.mainWindow()
            )
            self.settings_action.triggered.connect(self.open_settings)

            self.iface.addPluginToMenu("GeoSurvey", self.survey_action)
            self.iface.addPluginToMenu("GeoSurvey", self.cogo_action)
            self.iface.addPluginToMenu("GeoSurvey", self.qc_action)
            self.iface.addPluginToMenu("GeoSurvey", self.job_action)
            self.iface.addPluginToMenu("GeoSurvey", self.import_action)
            self.iface.addPluginToMenu("GeoSurvey", self.export_action)
            self.iface.addPluginToMenu("GeoSurvey", self.settings_action)

            self.iface.addPluginToolBar(self.survey_action)
        except Exception as e:
            self._log_error("GUI init failed: " + str(e))

    def unload(self):
        """Remove the plugin menu items and toolbar icons."""
        try:
            for action in [self.survey_action, self.cogo_action, self.qc_action,
                           self.job_action, self.import_action, self.export_action,
                           self.settings_action]:
                try:
                    self.iface.removePluginMenuAction("GeoSurvey", action)
                    self.iface.removeToolBarIcon(action)
                except Exception:
                    pass
        except Exception:
            pass

        if self._dock:
            try:
                self.iface.removeDockWidget(self._dock)
            except Exception:
                pass

    def toggle_dock(self):
        """Toggle the main survey dock widget."""
        if self._dock is None:
            try:
                from survey_dock import SurveyDock
                self._dock = SurveyDock(self.iface, self.iface.mainWindow())
            except Exception as e:
                self._log_error("Failed to create dock: " + str(e))
                return

        if self._dock.isVisible():
            self._dock.hide()
        else:
            self._dock.show()
            self._dock.raise_()

    def open_cogo(self):
        from cogo_dialog import COGODialog
        dlg = COGODialog(self.iface.mainWindow())
        dlg.exec()

    def open_qc(self):
        from qc_dialog import QCDialog
        dlg = QCDialog(self.iface.mainWindow())
        dlg.exec()

    def open_job_manager(self):
        from job_dialog import JobDialog
        dlg = JobDialog(self.iface.mainWindow())
        dlg.exec()

    def open_import(self):
        from import_dialog import ImportDialog
        dlg = ImportDialog(self.iface.mainWindow())
        dlg.exec()

    def open_export(self):
        from export_dialog import ExportDialog
        dlg = ExportDialog(self.iface.mainWindow())
        dlg.exec()

    def open_settings(self):
        from settings_dialog import SettingsDialog
        dlg = SettingsDialog(self.iface.mainWindow())
        dlg.exec()


def classFactory(iface):
    """Plugin class factory."""
    return GeoSurveyDesktopPlugin(iface)