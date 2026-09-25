# -*- coding: utf-8 -*-
"""Import/Export for GeoSurvey Desktop"""
import os
import sys
import json
import csv
from typing import List, Optional

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from qgis.core import (
    QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem,
    QgsProject, QgsRasterLayer, QgsRectangle, QgsCoordinateTransform,
    QgsPointXY, QgsGeometry, QgsFeature, QgsFields, QgsField
)
from qgis.PyQt.QtCore import QCoreApplication


class ImportExportManager:
    """Real import/export operations using QGIS APIs."""

    SUPPORTED_IMPORT = ["SHP", "GPKG", "GeoJSON", "CSV", "KML", "KMZ", "GPX", "DXF", "RASTER", "DEM"]
    SUPPORTED_EXPORT = ["SHP", "GPKG", "GeoJSON", "CSV", "KML", "DXF", "PDF"]

    def __init__(self, iface):
        self.iface = iface

    def import_layer(self, filepath, layer_name=""):
        """Import a vector layer from file."""
        if not os.path.exists(filepath):
            return None

        ext = os.path.splitext(filepath)[1].upper()
        if ext in (".SHP", ".GPKG", ".GEOJSON", ".JSON", ".KML", ".KMZ", ".GPX", ".DXF"):
            layer = QgsVectorLayer(filepath, layer_name or os.path.basename(filepath), "ogr")
            if layer.isValid():
                if self.iface:
                    self.iface.legendInterface().addLayer(layer)
                return layer
        elif ext in (".TIF", ".TIFF", ".IMG", ".RASTER"):
            layer = QgsRasterLayer(filepath, layer_name or os.path.basename(filepath))
            if layer.isValid() and self.iface:
                self.iface.legendInterface().addLayer(layer)
            return layer
        elif ext == ".CSV":
            return self._import_csv(filepath, layer_name)
        return None

    def _import_csv(self, filepath, layer_name):
        """Import CSV with X,Y columns."""
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            if not rows:
                return None

            x_field = None
            y_field = None
            for col in rows[0].keys():
                cl = col.strip().lower()
                if cl in ("x", "easting", "east", "lon", "longitude"):
                    x_field = col
                elif cl in ("y", "northing", "north", "lat", "latitude"):
                    y_field = col
            if not x_field or not y_field:
                return None

            uri = "Point?crs=EPSG:4326"
            layer = QgsVectorLayer(uri, layer_name or "CSV Import", "memory")
            provider = layer.dataProvider()
            provider.addAttributes([QgsField(col, 2) for col in rows[0].keys()])
            layer.updateFields()

            features = []
            for row in rows:
                try:
                    x = float(row[x_field])
                    y = float(row[y_field])
                    feat = QgsFeature()
                    feat.setGeometry(QgsGeometry.fromWkt("POINT (" + str(x) + " " + str(y) + ")"))
                    feat.setAttributes([row.get(k, "") for k in rows[0].keys()])
                    features.append(feat)
                except (ValueError, KeyError):
                    continue
            provider.addFeatures(features)
            if self.iface:
                self.iface.legendInterface().addLayer(layer)
            return layer
        except Exception:
            return None

    def export_layer(self, layer, filepath, format="GPKG"):
        """Export a vector layer to file."""
        if layer is None or not layer.isValid():
            return False

        ext_map = {
            "SHP": ".shp", "GPKG": ".gpkg", "GeoJSON": ".geojson",
            "CSV": ".csv", "KML": ".kml", "DXF": ".dxf"
        }
        ext = ext_map.get(format, ".gpkg")
        full_path = filepath if filepath.lower().endswith(ext.lower()) else filepath + ext

        driver_map = {
            "SHP": "ESRI Shapefile",
            "GPKG": "GPKG",
            "GeoJSON": "GeoJSON",
            "KML": "KML",
            "DXF": "DXF"
        }
        error = QgsVectorFileWriter.writeAsVectorFormat(
            layer, full_path, "UTF-8", layer.crs(),
            driverName=driver_map.get(format, "GPKG")
        )
        return error[0] == QgsVectorFileWriter.NoError

    def export_to_pdf(self, layer, filepath):
        """Export map to PDF using QGIS print layout."""
        try:
            from qgis.core import QgsPrintLayout, QgsLayoutItemMap
            from qgis.PyQt.QtCore import QSizeF
            project = QgsProject.instance()
            layout = QgsPrintLayout(project)
            layout.initializePages()
            page = layout.page()
            page.setPageSize(QSizeF(210, 297))
            map_item = QgsLayoutItemMap(layout)
            map_item.setExtent(layer.extent())
            layout.addMapItem(map_item)
            exporter = QgsLayoutExporter(layout)
            exporter.exportToPdf(filepath)
            return True
        except Exception:
            return False