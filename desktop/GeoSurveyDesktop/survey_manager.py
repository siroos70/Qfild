# -*- coding: utf-8 -*-
"""Survey Tools for GeoSurvey Desktop"""
import os
import sys

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.core import (
    QgsVectorLayer, QgsPointXY, QgsGeometry, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsProject, QgsFeature, QgsFields, QgsField
)
from qgis.PyQt.QtCore import Qt, QTimer, QMetaObject
from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QToolBar
from qgis.PyQt.QtCore import QVariant

from shared.coordinate_rules import Point, bearing, distance, polar, format_bearing, format_distance
from shared.specifications.geometry_engine import Line


class SurveyManager:
    """Real survey tools for QGIS Desktop."""

    def __init__(self, iface):
        self.iface = iface
        self._capture_mode = None
        self._captured_points = []
        self._current_layer = None

    def set_capture_mode(self, mode):
        if mode not in ("point", "line", "polygon"):
            raise ValueError("Invalid capture mode: " + mode)
        self._capture_mode = mode
        self._captured_points = []

    def capture_point(self, x, y, z=0.0):
        p = Point(x, y, z)
        self._captured_points.append(p)
        return p

    def get_current_layer(self):
        return self.iface.activeLayer() if self.iface else None

    def create_survey_layer(self, name, geometry_type="Point", crs_authid="EPSG:32639"):
        geom_map = {
            "point": "Point", "line": "LineString", "polygon": "Polygon",
            "multipoint": "MultiPoint", "multiline": "MultiLineString",
            "multipolygon": "MultiPolygon",
        }
        geom = geom_map.get(geometry_type.lower(), "Point")
        uri = geom + "?crs=" + crs_authid
        layer = QgsVectorLayer(uri, name, "memory")
        if not layer.isValid():
            return None
        provider = layer.dataProvider()
        provider.addAttributes([
            QgsField("id", QVariant.String),
            QgsField("name", QVariant.String),
            QgsField("code", QVariant.String),
            QgsField("survey_date", QVariant.String),
            QgsField("surveyor", QVariant.String),
            QgsField("accuracy", QVariant.Double),
            QgsField("hdop", QVariant.Double),
            QgsField("fix_type", QVariant.String)
        ])
        layer.updateFields()
        self._current_layer = layer
        return layer

    def add_feature_to_layer(self, layer, point, attributes=None):
        if layer is None or not layer.isValid():
            return False
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(
            "POINT (" + str(point.x) + " " + str(point.y) + " " + str(point.z) + ")"))
        attrs = []
        if attributes:
            for field_name in ["id", "name", "code", "survey_date", "surveyor",
                               "accuracy", "hdop", "fix_type"]:
                attrs.append(attributes.get(field_name, ""))
        feature.setAttributes(attrs)
        return layer.dataProvider().addFeature(feature)

    def compute_traverse(self, points):
        if len(points) < 2:
            return {"error": "Need at least 2 points"}
        total_dist = 0.0
        bearings = []
        for i in range(len(points) - 1):
            d = distance(points[i], points[i+1])
            b = bearing(points[i], points[i+1])
            total_dist += d
            bearings.append(b)
        return {
            "points": len(points),
            "total_distance": total_dist,
            "bearings": bearings,
            "format_distance": format_distance(total_dist)
        }

    def get_captured_points(self):
        return self._captured_points

    def clear_captured(self):
        self._captured_points = []