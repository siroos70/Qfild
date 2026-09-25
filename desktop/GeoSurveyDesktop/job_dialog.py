# -*- coding: utf-8 -*-
"""Job Dialog for GeoSurvey Desktop"""
import os
import sys

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QComboBox, QGroupBox, QHBoxLayout, QFileDialog,
    QCheckBox, QTableWidget, QHeaderView
)
from qgis.PyQt.QtCore import Qt

from job_manager import JobManager


class JobDialog(QDialog):
    """Job manager dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeoSurvey - Job Manager")
        self.setFixedSize(600, 500)
        self._manager = JobManager()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        group = QGroupBox("Create New Job")
        layout.addWidget(group)
        form = QFormLayout(group)
        self.job_name = QLineEdit()
        self.job_name.setPlaceholderText("Job name")
        self.job_project = QLineEdit()
        self.job_project.setPlaceholderText("Project name")
        self.job_area = QLineEdit()
        self.job_area.setPlaceholderText("Area description")
        self.job_crs = QComboBox()
        self.job_crs.addItems([
            "EPSG:32639", "EPSG:32640", "EPSG:4326", "EPSG:32739"
        ])
        form.addRow("Name:", self.job_name)
        form.addRow("Project:", self.job_project)
        form.addRow("Area:", self.job_area)
        form.addRow("CRS:", self.job_crs)
        btn_create = QPushButton("Create Job")
        btn_create.clicked.connect(self._create_job)
        form.addRow(btn_create)

        group2 = QGroupBox("Jobs List")
        layout.addWidget(group2)
        v2 = QVBoxLayout(group2)
        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(5)
        self.jobs_table.setHorizontalHeaderLabels(["ID", "Name", "Project", "Area", "Status"])
        self.jobs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v2.addWidget(self.jobs_table)

        btn_load = QPushButton("Load Jobs from File")
        btn_load.clicked.connect(self._load_jobs)
        v2.addWidget(btn_load)
        btn_save = QPushButton("Save Jobs to File")
        btn_save.clicked.connect(self._save_jobs)
        v2.addWidget(btn_save)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _create_job(self):
        job = self._manager.create_job(
            name=self.job_name.text(),
            project=self.job_project.text(),
            area=self.job_area.text(),
            crs=self.job_crs.currentText()
        )
        self._refresh_table()

    def _refresh_table(self):
        jobs = self._manager.get_jobs()
        self.jobs_table.setRowCount(len(jobs))
        for i, job in enumerate(jobs):
            self.jobs_table.setCellWidget(i, 0, QLabel(job.id))
            self.jobs_table.setCellWidget(i, 1, QLabel(job.name))
            self.jobs_table.setCellWidget(i, 2, QLabel(job.project))
            self.jobs_table.setCellWidget(i, 3, QLabel(job.area))
            self.jobs_table.setCellWidget(i, 4, QLabel(job.status))

    def _save_jobs(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Jobs", "", "JSON (*.json)")
        if path:
            self._manager.save_jobs(path)

    def _load_jobs(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Jobs", "", "JSON (*.json)")
        if path:
            self._manager.load_jobs(path)
            self._refresh_table()