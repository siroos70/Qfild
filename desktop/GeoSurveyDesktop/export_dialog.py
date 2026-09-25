# -*- coding: utf-8 -*-
"""Export Dialog for GeoSurvey Desktop"""
import os
import sys

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QComboBox, QGroupBox, QHBoxLayout, QFileDialog,
    QCheckBox, QProgressBar
)
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject

from import_export import ImportExportManager


class ExportDialog(QDialog):
    """Export data dialog."""

    def __init__(self, parent=None, iface=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("GeoSurvey - Export Data")
        self.setFixedSize(500, 400)
        self._manager = ImportExportManager(iface)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.layer_combo = QComboBox()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            self.layer_combo.addItem(layer.name(), layer)
        form.addRow("Layer:", self.layer_combo)

        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Output file path")
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self._browse)
        row = QHBoxLayout()
        row.addWidget(self.output_path)
        row.addWidget(btn_browse)
        form.addRow("Output:", row)

        self.format_combo = QComboBox()
        self.format_combo.addItems(self._manager.SUPPORTED_EXPORT)
        form.addRow("Format:", self.format_combo)

        layout.addLayout(form)

        btn_export = QPushButton("Export")
        btn_export.clicked.connect(self._export)
        layout.addWidget(btn_export)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _browse(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All files (*)")
        if path:
            self.output_path.setText(path)

    def _export(self):
        layer = self.layer_combo.currentData()
        path = self.output_path.text()
        fmt = self.format_combo.currentText()
        if layer and path:
            ok = self._manager.export_layer(layer, path, fmt)
            self.progress.setValue(100 if ok else 0)