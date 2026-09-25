# -*- coding: utf-8 -*-
"""Field Survey Manager for QField"""
import os
import sys

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.coordinate_rules import Point, bearing, distance, polar, format_bearing, format_distance


class FieldSurveyManager:
    """Field survey manager for QField mobile."""

    def __init__(self):
        self._capture_mode = "point"
        self._captured_points = []
        self._current_layer = None
        self._current_position = None
        self._accuracy_threshold = 0.05
        self._hdop_threshold = 1.5

    def set_capture_mode(self, mode):
        if mode not in ("point", "line", "polygon"):
            raise ValueError("Invalid capture mode: " + mode)
        self._capture_mode = mode
        self._captured_points = []

    def capture_point(self, x, y, z=0.0, accuracy=0.0, hdop=0.0, fix_type="GPS"):
        p = Point(x, y, z)
        self._captured_points.append({
            "point": p,
            "accuracy": accuracy,
            "hdop": hdop,
            "fix_type": fix_type
        })
        return p

    def get_captured_points(self):
        return self._captured_points

    def clear_captured(self):
        self._captured_points = []

    def get_position_quality(self, accuracy, hdop, fix_type):
        """Determine position quality."""
        if accuracy <= 0.05 and hdop <= 1.5 and fix_type in ("RTK FIXED", "RTK FLOAT"):
            return "GOOD"
        elif accuracy <= 0.5 and hdop <= 3.0:
            return "WARNING"
        else:
            return "BAD"

    def compute_traverse(self, points):
        if len(points) < 2:
            return {"error": "Need at least 2 points"}
        total_dist = 0.0
        bearings = []
        for i in range(len(points) - 1):
            p1 = points[i]["point"] if isinstance(points[i], dict) else points[i]
            p2 = points[i+1]["point"] if isinstance(points[i+1], dict) else points[i+1]
            d = distance(p1, p2)
            b = bearing(p1, p2)
            total_dist += d
            bearings.append(b)
        return {
            "points": len(points),
            "total_distance": total_dist,
            "bearings": bearings,
            "format_distance": format_distance(total_dist)
        }