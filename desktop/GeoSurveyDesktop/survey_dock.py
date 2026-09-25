# -*- coding: utf-8 -*-
"""Survey Dock Widget for GeoSurvey Desktop"""
import os
import sys

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QToolBar, QButtonGroup,
    QGroupBox, QFormLayout, QLineEdit, QPushButton, QLabel,
    QTableWidget, QHeaderView, QTextEdit, QTabWidget
)
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QFont

from survey_manager import SurveyManager
from job_manager import JobManager
from cogo_engine import COGOEngine
from qc_engine import QCEngine
from shared.coordinate_rules import Point, format_bearing, format_distance, format_area
from shared.specifications.geometry_engine import Line


class SurveyDock(QDockWidget):
    """Main survey dock widget for QGIS Desktop."""

    def __init__(self, iface, parent=None):
        super().__init__("GeoSurvey Survey", parent)
        self.iface = iface
        self._survey = SurveyManager(iface)
        self._jobs = JobManager()
        self._cogo = COGOEngine()
        self._qc = QCEngine()
        self._setup_ui()
        self._setup_timer()

    def _setup_ui(self):
        widget = QWidget()
        self.setWidget(widget)
        layout = QVBoxLayout(widget)

        toolbar = QToolBar("Survey Tools")
        layout.addWidget(toolbar)

        self.btn_capture_point = QPushButton("Capture Point")
        self.btn_capture_point.setCheckable(True)
        self.btn_capture_line = QPushButton("Capture Line")
        self.btn_capture_line.setCheckable(True)
        self.btn_capture_polygon = QPushButton("Capture Polygon")
        self.btn_capture_polygon.setCheckable(True)

        toolbar.addWidget(self.btn_capture_point)
        toolbar.addWidget(self.btn_capture_line)
        toolbar.addWidget(self.btn_capture_polygon)

        group_coord = QGroupBox("Current Position")
        layout.addWidget(group_coord)
        form_coord = QFormLayout(group_coord)
        self.label_x = QLabel("--")
        self.label_y = QLabel("--")
        self.label_z = QLabel("--")
        self.label_bearing = QLabel("--")
        self.label_distance = QLabel("--")
        form_coord.addRow("X:", self.label_x)
        form_coord.addRow("Y:", self.label_y)
        form_coord.addRow("Z:", self.label_z)
        form_coord.addRow("Bearing:", self.label_bearing)
        form_coord.addRow("Distance:", self.label_distance)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        tab_survey = QWidget()
        tabs.addTab(tab_survey, "Survey")
        v_survey = QVBoxLayout(tab_survey)
        self.text_survey = QTextEdit()
        self.text_survey.setReadOnly(True)
        self.text_survey.setFont(QFont("Consolas", 9))
        v_survey.addWidget(self.text_survey)

        tab_qc = QWidget()
        tabs.addTab(tab_qc, "QC")
        v_qc = QVBoxLayout(tab_qc)
        self.text_qc = QTextEdit()
        self.text_qc.setReadOnly(True)
        self.text_qc.setFont(QFont("Consolas", 9))
        v_qc.addWidget(self.text_qc)

        tab_jobs = QWidget()
        tabs.addTab(tab_jobs, "Jobs")
        v_jobs = QVBoxLayout(tab_jobs)
        self.table_jobs = QTableWidget()
        self.table_jobs.setColumnCount(4)
        self.table_jobs.setHorizontalHeaderLabels(["ID", "Name", "Project", "Status"])
        self.table_jobs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v_jobs.addWidget(self.table_jobs)

    def _setup_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_display)
        self._timer.start(1000)

    def _update_display(self):
        pass

    def update_position(self, x, y, z=0.0):
        self.label_x.setText(str(round(x, 3)))
        self.label_y.setText(str(round(y, 3)))
        self.label_z.setText(str(round(z, 3)))

    def update_bearing_distance(self, bearing_val, distance_val):
        self.label_bearing.setText(format_bearing(bearing_val))
        self.label_distance.setText(format_distance(distance_val))

    def add_survey_log(self, message):
        self.text_survey.append(message)

    def add_qc_log(self, message):
        self.text_qc.append(message)

    def refresh_jobs(self):
        jobs = self._jobs.get_jobs()
        self.table_jobs.setRowCount(len(jobs))
        for i, job in enumerate(jobs):
            self.table_jobs.setCellWidget(i, 0, QLabel(job.id))
            self.table_jobs.setCellWidget(i, 1, QLabel(job.name))
            self.table_jobs.setCellWidget(i, 2, QLabel(job.project))
            self.table_jobs.setCellWidget(i, 3, QLabel(job.status))

    def raise_(self):
        super().show()
        self.raise_()