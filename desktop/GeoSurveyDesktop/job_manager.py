# -*- coding: utf-8 -*-
"""Job Manager for GeoSurvey Desktop"""
import os
import sys
import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.core import QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem


class Job:
    def __init__(self, name="", project="", area="", crs="EPSG:32639"):
        self.id = str(uuid.uuid4())[:8].upper()
        self.name = name
        self.project = project
        self.area = area
        self.crs = crs
        self.layers = []
        self.survey_rules = {}
        self.accuracy_rules = {}
        self.qc_rules = {}
        self.assigned_user = ""
        self.tasks = []
        self.status = "OPEN"
        self.start_date = datetime.now().isoformat()
        self.end_date = None
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "project": self.project,
            "area": self.area, "crs": self.crs, "layers": self.layers,
            "survey_rules": self.survey_rules, "accuracy_rules": self.accuracy_rules,
            "qc_rules": self.qc_rules, "assigned_user": self.assigned_user,
            "tasks": self.tasks, "status": self.status,
            "start_date": self.start_date, "end_date": self.end_date,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        job = cls(name=data.get("name", ""), project=data.get("project", ""),
                  area=data.get("area", ""), crs=data.get("crs", "EPSG:32639"))
        job.id = data.get("id", job.id)
        job.layers = data.get("layers", [])
        job.survey_rules = data.get("survey_rules", {})
        job.accuracy_rules = data.get("accuracy_rules", {})
        job.qc_rules = data.get("qc_rules", {})
        job.assigned_user = data.get("assigned_user", "")
        job.tasks = data.get("tasks", [])
        job.status = data.get("status", "OPEN")
        job.start_date = data.get("start_date", job.start_date)
        job.end_date = data.get("end_date")
        job.created_at = data.get("created_at", job.created_at)
        return job


class JobManager:
    """Real job manager for QGIS Desktop."""

    def __init__(self):
        self._jobs = []
        self._current_job = None

    def create_job(self, name, project="", area="", crs="EPSG:32639"):
        job = Job(name=name, project=project, area=area, crs=crs)
        self._jobs.append(job)
        self._current_job = job
        return job

    def get_jobs(self):
        return self._jobs

    def get_job(self, job_id):
        for j in self._jobs:
            if j.id == job_id:
                return j
        return None

    def set_current_job(self, job):
        self._current_job = job

    def get_current_job(self):
        return self._current_job

    def add_task(self, job_id, task):
        job = self.get_job(job_id)
        if job:
            job.tasks.append(task)
            return True
        return False

    def update_task(self, job_id, task_id, updates):
        job = self.get_job(job_id)
        if not job:
            return False
        for t in job.tasks:
            if t.get("id") == task_id:
                t.update(updates)
                return True
        return False

    def close_job(self, job_id):
        job = self.get_job(job_id)
        if job:
            job.status = "CLOSED"
            job.end_date = datetime.now().isoformat()
            return True
        return False

    def save_jobs(self, filepath):
        try:
            data = [j.to_dict() for j in self._jobs]
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def load_jobs(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._jobs = [Job.from_dict(d) for d in data]
            return True
        except Exception:
            return False