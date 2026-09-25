import math
from dataclasses import dataclass, field
from typing import Tuple, List, Optional

from ..coordinate_rules import Point, bearing, distance, polar, inverse_bearing
from .geometry_engine import Line
from .cogo_geometry import Circle


@dataclass
class COGOResult:
    success: bool
    point: Optional[Point] = None
    bearing: Optional[float] = None
    distance: Optional[float] = None
    error: Optional[str] = None
    details: dict = None


def point_from_bearing_distance(origin, brg, dist):
    if dist < 0:
        return COGOResult(success=False, error="Distance cannot be negative")
    p = polar(origin, brg, dist)
    return COGOResult(success=True, point=p, bearing=brg, distance=dist)


def bearing_distance_from_points(p1, p2):
    brg = bearing(p1, p2)
    d = distance(p1, p2)
    return COGOResult(success=True, bearing=brg, distance=d)


def intersection_line_line(l1, l2):
    from .geometry_engine import line_intersection
    p = line_intersection(l1, l2)
    if p is None:
        return COGOResult(success=False, error="Lines are parallel or coincident")
    return COGOResult(success=True, point=p)


def intersection_line_circle(line, circle):
    from .cogo_geometry import circle_line_intersection
    pts = circle_line_intersection(circle, line)
    if not pts:
        return COGOResult(success=False, error="No intersection")
    return COGOResult(success=True, point=pts[0], details={"points": pts})


def intersection_circle_circle(c1, c2):
    from .cogo_geometry import circle_circle_intersection
    pts = circle_circle_intersection(c1, c2)
    if not pts:
        return COGOResult(success=False, error="No intersection")
    return COGOResult(success=True, point=pts[0], details={"points": pts})


def offset_point_from_line(p, line, offset):
    from .geometry_engine import point_projection
    proj = point_projection(p, line)
    brg_line = math.radians(line.bearing())
    perp = brg_line + math.pi / 2.0
    ox = offset * math.sin(perp)
    oy = offset * math.cos(perp)
    result = Point(proj.x + ox, proj.y + oy, p.z)
    return COGOResult(success=True, point=result)


def offset_line(line, offset):
    brg = math.radians(line.bearing())
    perp = brg + math.pi / 2.0
    ox = offset * math.sin(perp)
    oy = offset * math.cos(perp)
    new_line = Line(Point(line.start.x + ox, line.start.y + oy),
                    Point(line.end.x + ox, line.end.y + oy))
    return COGOResult(success=True, details={"line": new_line})


def arc_from_two_points_and_radius(p1, p2, radius, clockwise=False):
    d = distance(p1, p2)
    if d > 2 * radius + 1e-9:
        return COGOResult(success=False, error="Radius too small for given points")
    if d < 1e-12:
        return COGOResult(success=False, error="Points are coincident")

    mid = Point((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)
    brg = bearing(p1, p2)
    perp_brg = math.radians(brg + (90.0 if not clockwise else -90.0))

    h = math.sqrt(radius * radius - (d / 2.0) ** 2)
    center = Point(mid.x + h * math.sin(perp_brg),
                   mid.y + h * math.cos(perp_brg))
    return COGOResult(success=True, point=center,
                      details={"radius": radius, "center": center,
                               "start": p1, "end": p2})


def area_of_polygon(points):
    n = len(points)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i].x * points[j].y
        area -= points[j].x * points[i].y
    return abs(area) / 2.0


def perimeter_of_polygon(points):
    n = len(points)
    if n < 2:
        return 0.0
    perim = 0.0
    for i in range(n):
        j = (i + 1) % n
        perim += distance(points[i], points[j])
    return perim