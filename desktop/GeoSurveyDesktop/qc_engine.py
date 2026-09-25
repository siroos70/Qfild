# -*- coding: utf-8 -*-
"""QC Engine for GeoSurvey Desktop"""
import os
import sys
from typing import List, Optional, Dict, Any

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PLUGIN_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.specifications.qc_engine import (
    QCStatus, QCResult,
    check_duplicate_points, check_self_intersection, check_zero_length,
    check_zero_area, check_multipart, check_overlap, check_gap,
    check_point_in_polygon, check_point_within_area
)
from shared.coordinate_rules import Point, distance


class QCEngine:
    """Real QC engine for vector data validation."""

    def __init__(self):
        self._results: List[QCResult] = []

    def run_geometry_qc(self, points: List[Point]) -> List[QCResult]:
        results = []
        results.extend(check_duplicate_points(points))
        results.extend(check_self_intersection(points))
        results.extend(check_zero_length(points))
        results.extend(check_zero_area(points))
        self._results.extend(results)
        return results

    def run_spatial_qc(self, points: List[Point], area: List[Point]) -> List[QCResult]:
        results = []
        for p in points:
            results.extend(check_point_within_area(p, area))
        self._results.extend(results)
        return results

    def run_gnss_qc(self, accuracy: float, hdop: float, fix_type: str,
                    satellite_count: int, rules: Dict[str, Any] = None) -> List[QCResult]:
        results = []
        rules = rules or {}

        max_accuracy = rules.get("max_accuracy", 0.05)
        max_hdop = rules.get("max_hdop", 1.5)
        min_satellites = rules.get("min_satellites", 4)
        allowed_fixes = rules.get("allowed_fixes", ["RTK FIXED", "RTK FLOAT", "GPS", "DGPS"])

        if accuracy > max_accuracy:
            results.append(QCResult(
                check_id="ACCURACY_LOW",
                status=QCStatus.ERROR if accuracy > max_accuracy * 3 else QCStatus.WARNING,
                message=f"Accuracy {accuracy:.3f} m exceeds threshold {max_accuracy} m",
                details={"accuracy": accuracy, "threshold": max_accuracy}
            ))
        else:
            results.append(QCResult(
                check_id="ACCURACY_OK",
                status=QCStatus.PASS,
                message=f"Accuracy {accuracy:.3f} m within threshold",
                details={"accuracy": accuracy}
            ))

        if hdop > max_hdop:
            results.append(QCResult(
                check_id="HDOP_HIGH",
                status=QCStatus.WARNING,
                message=f"HDOP {hdop:.2f} exceeds threshold {max_hdop}",
                details={"hdop": hdop, "threshold": max_hdop}
            ))

        if satellite_count < min_satellites:
            results.append(QCResult(
                check_id="SATELLITES_LOW",
                status=QCStatus.ERROR,
                message=f"Satellite count {satellite_count} below minimum {min_satellites}",
                details={"satellites": satellite_count, "minimum": min_satellites}
            ))

        if fix_type not in allowed_fixes:
            results.append(QCResult(
                check_id="FIX_TYPE_INVALID",
                status=QCStatus.ERROR,
                message=f"Fix type '{fix_type}' not in allowed list",
                details={"fix_type": fix_type, "allowed": allowed_fixes}
            ))

        self._results.extend(results)
        return results

    def get_results(self) -> List[QCResult]:
        return self._results

    def clear_results(self):
        self._results.clear()

    def get_summary(self) -> Dict[str, int]:
        summary = {"PASS": 0, "WARNING": 0, "ERROR": 0, "INFO": 0}
        for r in self._results:
            summary[r.status.value] = summary.get(r.status.value, 0) + 1
        return summary
