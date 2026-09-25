# -*- coding: utf-8 -*-
"""Settings Dialog for GeoSurvey Desktop"""
import os
import sys

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout,
    QTabWidget, QWidget, QCheckBox, QSpinBox
)
from qgis.PyQt.QtCore import Qt

from settings_manager import SettingsManager


class SettingsDialog(QDialog):
    """Settings dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeoSurvey - Settings")
        self.setFixedSize(500, 450)
        self._settings = SettingsManager()
        self._settings.load()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget(self)
        layout.addWidget(tabs)

        tab1 = QWidget()
        tabs.addTab(tab1, "General")
        form1 = QFormLayout(tab1)
        self.coord_mode = QComboBox()
        self.coord_mode.addItems(["XY", "LatLon", "XYZ"])
        self.coord_mode.setCurrentText(self._settings.get("coordinate_display_mode", "XY"))
        form1.addRow("Coordinate Display:", self.coord_mode)

        self.default_crs = QComboBox()
        self.default_crs.addItems([
            "EPSG:32639", "EPSG:32640", "EPSG:4326", "EPSG:32739"
        ])
        self.default_crs.setCurrentText(self._settings.get("default_crs", "EPSG:32639"))
        form1.addRow("Default CRS:", self.default_crs)

        self.language = QComboBox()
        self.language.addItems(["English", "فارسی"])
        form1.addRow("Language:", self.language)

        self.show_grid = QCheckBox("Show grid")
        self.show_grid.setChecked(self._settings.get("show_grid", True))
        form1.addRow(self.show_grid)

        tab2 = QWidget()
        tabs.addTab(tab2, "Accuracy")
        form2 = QFormLayout(tab2)
        self.max_accuracy = QDoubleSpinBox()
        self.max_accuracy.setRange(0.001, 100)
        self.max_accuracy.setDecimals(3)
        self.max_accuracy.setValue(self._settings.get("default_accuracy_threshold", 0.05))
        form2.addRow("Max Accuracy (m):", self.max_accuracy)

        self.max_hdop = QDoubleSpinBox()
        self.max_hdop.setRange(0.5, 50)
        self.max_hdop.setDecimals(2)
        self.max_hdop.setValue(self._settings.get("default_hdop_threshold", 1.5))
        form2.addRow("Max HDOP:", self.max_hdop)

        self.min_satellites = QSpinBox()
        self.min_satellites.setRange(3, 20)
        self.min_satellites.setValue(self._settings.get("default_min_satellites", 4))
        form2.addRow("Min Satellites:", self.min_satellites)

        btns = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btns.addWidget(save_btn)
        btns.addWidget(reset_btn)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

    def _save(self):
        self._settings.set("coordinate_display_mode", self.coord_mode.currentText())
        self._settings.set("default_crs", self.default_crs.currentText())
        self._settings.set("default_accuracy_threshold", self.max_accuracy.value())
        self._settings.set("default_hdop_threshold", self.max_hdop.value())
        self._settings.set("default_min_satellites", self.min_satellites.value())
        self._settings.set("show_grid", self.show_grid.isChecked())
        self._settings.save()

    def _reset(self):
        self._settings.reset()
        self._setup_ui()