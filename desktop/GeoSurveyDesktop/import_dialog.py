# -*- coding: utf-8 -*-
"""Import Dialog for GeoSurvey Desktop"""
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

from import_export import ImportExportManager


class ImportDialog(QDialog):
    """Import data dialog."""

    def __init__(self, parent=None, iface=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("GeoSurvey - Import Data")
        self.setFixedSize(500, 400)
        self._manager = ImportExportManager(iface)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("Select file to import")
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self._browse)
        row = QHBoxLayout()
        row.addWidget(self.file_path)
        row.addWidget(btn_browse)
        form.addRow("File:", row)

        self.format_combo = QComboBox()
        self.format_combo.addItems(self._manager.SUPPORTED_IMPORT)
        form.addRow("Format:", self.format_combo)

        self.layer_name = QLineEdit()
        self.layer_name.setPlaceholderText("Layer name (optional)")
        form.addRow("Layer Name:", self.layer_name)

        self.add_to_project = QCheckBox("Add to current project")
        self.add_to_project.setChecked(True)
        form.addRow(self.add_to_project)

        layout.addLayout(form)

        btn_import = QPushButton("Import")
        btn_import.clicked.connect(self._import)
        layout.addWidget(btn_import)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "",
            "All supported (*.shp *.gpkg *.geojson *.csv *.kml *.kmz *.gpx *.dxf *.tif *.tiff *.img);;All files (*)"
        )
        if path:
            self.file_path.setText(path)

    def _import(self):
        path = self.file_path.text()
        if not path:
            return
        layer = self._manager.import_layer(path, self.layer_name.text())
        if layer:
            self.progress.setValue(100)
        else:
            self.progress.setValue(0)