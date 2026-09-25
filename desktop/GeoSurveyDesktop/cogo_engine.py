# -*- coding: utf-8 -*-
"""COGO Engine for GeoSurvey Desktop"""
import os
import sys
import math
from typing import List, Optional, Tuple

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.core import (
    QgsVectorLayer, QgsPointXY, QgsGeometry, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsProject
)

from shared.specifications.cogo_engine import (
    COGOResult, point_from_bearing_distance, bearing_distance_from_points,
    intersection_line_line, intersection_line_circle, intersection_circle_circle,
    offset_point_from_line, offset_line, arc_from_two_points_and_radius,
    area_of_polygon, perimeter_of_polygon
)
from shared.specifications.cogo_geometry import Circle
from shared.specifications.geometry_engine import Line
from shared.coordinate_rules import Point, bearing, distance, polar


class COGOEngine:
    """Real COGO computation engine."""

    def __init__(self):
        self._history = []

    def compute_point_from_bearing_distance(self, origin, brg, dist):
        result = point_from_bearing_distance(origin, brg, dist)
        self._history.append(("point_from_bearing_distance", result))
        return result

    def compute_bearing_distance(self, p1, p2):
        result = bearing_distance_from_points(p1, p2)
        self._history.append(("bearing_distance", result))
        return result

    def compute_line_intersection(self, l1, l2):
        result = intersection_line_line(l1, l2)
        self._history.append(("line_intersection", result))
        return result

    def compute_line_circle_intersection(self, line, circle):
        result = intersection_line_circle(line, circle)
        self._history.append(("line_circle_intersection", result))
        return result

    def compute_circle_circle_intersection(self, c1, c2):
        result = intersection_circle_circle(c1, c2)
        self._history.append(("circle_circle_intersection", result))
        return result

    def compute_offset_point(self, p, line, offset):
        result = offset_point_from_line(p, line, offset)
        self._history.append(("offset_point", result))
        return result

    def compute_offset_line(self, line, offset):
        result = offset_line(line, offset)
        self._history.append(("offset_line", result))
        return result

    def compute_arc(self, p1, p2, radius, clockwise=False):
        result = arc_from_two_points_and_radius(p1, p2, radius, clockwise)
        self._history.append(("arc", result))
        return result

    def compute_area(self, points):
        return area_of_polygon(points)

    def compute_perimeter(self, points):
        return perimeter_of_polygon(points)

    def transform_to_project_crs(self, x, y, source_authid="EPSG:4326"):
        src = QgsCoordinateReferenceSystem.fromAuthId(source_authid)
        dst = QgsProject.instance().crs()
        if not src.isValid() or not dst.isValid():
            return (x, y)
        transform = QgsCoordinateTransform(src, dst, QgsProject.instance())
        pt = transform.transform(QgsPointXY(x, y))
        return (pt.x(), pt.y())

    def get_history(self):
        return self._history

    def clear_history(self):
        self._history.clear()