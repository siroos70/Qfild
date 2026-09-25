import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from ..coordinate_rules import Point, bearing, distance, polar
from .geometry_engine import Line, point_projection, point_to_line_distance


class QCStatus(Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    INFO = "INFO"


@dataclass
class QCResult:
    check_id: str
    status: QCStatus
    message: str
    feature_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


def check_duplicate_points(points, tolerance=0.001):
    results = []
    seen = []
    for i, p in enumerate(points):
        for j, sp in enumerate(seen):
            if distance(p, sp) < tolerance:
                results.append(QCResult(
                    check_id="DUP_POINT",
                    status=QCStatus.ERROR,
                    message="Duplicate point at index " + str(i),
                    details={"index": i, "duplicate_of": j, "distance": distance(p, sp)}
                ))
                break
        seen.append(p)
    return results


def check_self_intersection(points):
    results = []
    n = len(points)
    if n < 4:
        return results
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            l1 = Line(points[i], points[(i + 1) % n])
            l2 = Line(points[j], points[(j + 1) % n])
            from .geometry_engine import segment_intersection
            if segment_intersection(l1, l2):
                results.append(QCResult(
                    check_id="SELF_INTERSECTION",
                    status=QCStatus.ERROR,
                    message="Edges " + str(i) + "-" + str((i+1)%n) + " and " + str(j) + "-" + str((j+1)%n) + " intersect",
                    details={"edge1": i, "edge2": j}
                ))
    return results


def check_zero_length(points, tolerance=0.001):
    results = []
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        d = distance(points[i], points[j])
        if d < tolerance:
            results.append(QCResult(
                check_id="ZERO_LENGTH",
                status=QCStatus.ERROR,
                message="Edge " + str(i) + "-" + str(j) + " has near-zero length: " + str(d),
                details={"edge": i, "length": d}
            ))
    return results


def check_zero_area(points, tolerance=0.001):
    n = len(points)
    if n < 3:
        return [QCResult(check_id="ZERO_AREA", status=QCStatus.ERROR,
                         message="Polygon has fewer than 3 points")]
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i].x * points[j].y
        area -= points[j].x * points[i].y
    area = abs(area) / 2.0
    if area < tolerance:
        return [QCResult(check_id="ZERO_AREA", status=QCStatus.ERROR,
                         message="Polygon area is near zero: " + str(area),
                         details={"area": area})]
    return []


def check_multipart(points_list):
    if len(points_list) > 1:
        return [QCResult(check_id="MULTIPART", status=QCStatus.WARNING,
                         message="Polygon has " + str(len(points_list)) + " rings",
                         details={"ring_count": len(points_list)})]
    return []


def check_overlap(poly1, poly2):
    results = []
    min_x1 = min(p.x for p in poly1)
    max_x1 = max(p.x for p in poly1)
    min_y1 = min(p.y for p in poly1)
    max_y1 = max(p.y for p in poly1)
    min_x2 = min(p.x for p in poly2)
    max_x2 = max(p.x for p in poly2)
    min_y2 = min(p.y for p in poly2)
    max_y2 = max(p.y for p in poly2)

    if (min_x1 < max_x2 and max_x1 > min_x2 and
        min_y1 < max_y2 and max_y1 > min_y2):
        overlap_area = (min(max_x1, max_x2) - max(min_x1, min_x2)) * \
                       (min(max_y1, max_y2) - max(min_y1, min_y2))
        results.append(QCResult(
            check_id="OVERLAP",
            status=QCStatus.WARNING,
            message="Bounding boxes overlap",
            details={"overlap_area": overlap_area}
        ))
    return results


def check_gap(poly1, poly2, gap_threshold=0.5):
    results = []
    min_dist = float("inf")
    for p1 in poly1:
        for p2 in poly2:
            d = distance(p1, p2)
            if d < min_dist:
                min_dist = d
    if min_dist > gap_threshold:
        results.append(QCResult(
            check_id="GAP",
            status=QCStatus.WARNING,
            message="Gap between polygons: " + str(min_dist) + " m",
            details={"gap_distance": min_dist}
        ))
    return results


def check_point_in_polygon(p, poly):
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        if ((poly[i].y > p.y) != (poly[j].y > p.y) and
            p.x < (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x):
            inside = not inside
        j = i
    return inside


def check_point_within_area(p, area, tolerance=0.0):
    if check_point_in_polygon(p, area):
        return []
    return [QCResult(
        check_id="OUTSIDE_AREA",
        status=QCStatus.ERROR,
        message="Point (" + str(p.x) + ", " + str(p.y) + ") is outside allowed area",
        details={"point": p, "tolerance": tolerance}
    )]