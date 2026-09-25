# -*- coding: utf-8 -*-
"""QC Dialog for GeoSurvey Desktop"""
import os
import sys

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout,
    QTabWidget, QWidget, QTextEdit
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont

from qc_engine import QCEngine, QCStatus


class QCDialog(QDialog):
    """QC engine dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeoSurvey - QC Engine")
        self.setFixedSize(600, 500)
        self._engine = QCEngine()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget(self)
        layout.addWidget(tabs)

        tab1 = QWidget()
        tabs.addTab(tab1, "GNSS QC")
        form1 = QFormLayout(tab1)
        self.qc_accuracy = QDoubleSpinBox()
        self.qc_accuracy.setRange(0, 100)
        self.qc_accuracy.setDecimals(3)
        self.qc_accuracy.setValue(0.045)
        self.qc_hdop = QDoubleSpinBox()
        self.qc_hdop.setRange(0.5, 50)
        self.qc_hdop.setDecimals(2)
        self.qc_hdop.setValue(1.2)
        self.qc_satellites = QDoubleSpinBox()
        self.qc_satellites.setRange(0, 100)
        self.qc_satellites.setValue(12)
        self.qc_fix = QComboBox()
        self.qc_fix.addItems(["RTK FIXED", "RTK FLOAT", "GPS", "DGPS", "NONE"])
        form1.addRow("Accuracy (m):", self.qc_accuracy)
        form1.addRow("HDOP:", self.qc_hdop)
        form1.addRow("Satellites:", self.qc_satellites)
        form1.addRow("Fix Type:", self.qc_fix)
        btn1 = QPushButton("Run QC")
        btn1.clicked.connect(self._run_gnss_qc)
        form1.addRow(btn1)

        group = QGroupBox("QC Result")
        layout.addWidget(group)
        v = QVBoxLayout(group)
        self.qc_result = QTextEdit()
        self.qc_result.setReadOnly(True)
        self.qc_result.setFont(QFont("Consolas", 9))
        v.addWidget(self.qc_result)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _run_gnss_qc(self):
        results = self._engine.run_gnss_qc(
            accuracy=self.qc_accuracy.value(),
            hdop=self.qc_hdop.value(),
            fix_type=self.qc_fix.currentText(),
            satellite_count=int(self.qc_satellites.value())
        )
        text = ""
        for r in results:
            text += "[" + r.status.value + "] " + r.check_id + ": " + r.message + "\n"
        self.qc_result.setPlainText(text)