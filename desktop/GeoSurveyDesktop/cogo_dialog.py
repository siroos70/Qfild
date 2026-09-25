# -*- coding: utf-8 -*-
"""COGO Dialog for GeoSurvey Desktop"""
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

from cogo_engine import COGOEngine
from shared.coordinate_rules import Point, format_bearing, format_distance


class COGODialog(QDialog):
    """COGO calculator dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeoSurvey - COGO Calculator")
        self.setFixedSize(700, 600)
        self._engine = COGOEngine()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget(self)
        layout.addWidget(tabs)

        tab1 = QWidget()
        tabs.addTab(tab1, "Bearing + Distance")
        form1 = QFormLayout(tab1)
        self.ox = QDoubleSpinBox()
        self.ox.setRange(-1e9, 1e9)
        self.ox.setDecimals(3)
        self.ox.setValue(500000.0)
        self.oy = QDoubleSpinBox()
        self.oy.setRange(-1e9, 1e9)
        self.oy.setDecimals(3)
        self.oy.setValue(3000000.0)
        self.cogo_bearing = QDoubleSpinBox()
        self.cogo_bearing.setRange(0, 360)
        self.cogo_bearing.setDecimals(4)
        self.cogo_bearing.setValue(35.3361)
        self.cogo_distance = QDoubleSpinBox()
        self.cogo_distance.setRange(0, 1e9)
        self.cogo_distance.setDecimals(3)
        self.cogo_distance.setValue(25.450)
        form1.addRow("Origin X:", self.ox)
        form1.addRow("Origin Y:", self.oy)
        form1.addRow("Bearing (deg):", self.cogo_bearing)
        form1.addRow("Distance (m):", self.cogo_distance)
        btn1 = QPushButton("Compute Point")
        btn1.clicked.connect(self._compute_point_from_bearing_distance)
        form1.addRow(btn1)

        tab2 = QWidget()
        tabs.addTab(tab2, "Bearing from Points")
        form2 = QFormLayout(tab2)
        self.p1x = QDoubleSpinBox()
        self.p1x.setRange(-1e9, 1e9)
        self.p1x.setDecimals(3)
        self.p1x.setValue(500000.0)
        self.p1y = QDoubleSpinBox()
        self.p1y.setRange(-1e9, 1e9)
        self.p1y.setDecimals(3)
        self.p1y.setValue(3000000.0)
        self.p2x = QDoubleSpinBox()
        self.p2x.setRange(-1e9, 1e9)
        self.p2x.setDecimals(3)
        self.p2x.setValue(500021.0)
        self.p2y = QDoubleSpinBox()
        self.p2y.setRange(-1e9, 1e9)
        self.p2y.setDecimals(3)
        self.p2y.setValue(3000025.0)
        form2.addRow("Point 1 X:", self.p1x)
        form2.addRow("Point 1 Y:", self.p1y)
        form2.addRow("Point 2 X:", self.p2x)
        form2.addRow("Point 2 Y:", self.p2y)
        btn2 = QPushButton("Compute Bearing + Distance")
        btn2.clicked.connect(self._compute_bearing_distance)
        form2.addRow(btn2)

        group = QGroupBox("Result")
        layout.addWidget(group)
        v = QVBoxLayout(group)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 9))
        v.addWidget(self.result_text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _compute_point_from_bearing_distance(self):
        origin = Point(self.ox.value(), self.oy.value())
        result = self._engine.compute_point_from_bearing_distance(
            origin, self.cogo_bearing.value(), self.cogo_distance.value())
        if result.success and result.point:
            text = "Origin: (" + str(origin.x) + ", " + str(origin.y) + ")\n"
            text += "Bearing: " + format_bearing(result.bearing) + "\n"
            text += "Distance: " + format_distance(result.distance) + "\n"
            text += "Result Point: (" + str(result.point.x) + ", " + str(result.point.y) + ")\n"
            self.result_text.setPlainText(text)
        else:
            self.result_text.setPlainText("Error: " + str(result.error))

    def _compute_bearing_distance(self):
        p1 = Point(self.p1x.value(), self.p1y.value())
        p2 = Point(self.p2x.value(), self.p2y.value())
        result = self._engine.compute_bearing_distance(p1, p2)
        if result.success:
            text = "Point 1: (" + str(p1.x) + ", " + str(p1.y) + ")\n"
            text += "Point 2: (" + str(p2.x) + ", " + str(p2.y) + ")\n"
            text += "Bearing: " + format_bearing(result.bearing) + "\n"
            text += "Distance: " + format_distance(result.distance) + "\n"
            self.result_text.setPlainText(text)
        else:
            self.result_text.setPlainText("Error: " + str(result.error))