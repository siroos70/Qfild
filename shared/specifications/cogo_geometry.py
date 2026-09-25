import math
from dataclasses import dataclass
from typing import List, Optional

from ..coordinate_rules import Point, bearing, distance, polar
from .geometry_engine import Line, line_intersection, point_projection, point_to_line_distance


@dataclass
class Circle:
    center: Point
    radius: float


def circle_line_intersection(circle, line):
    cx, cy = circle.center.x, circle.center.y
    r = circle.radius
    x1, y1 = line.start.x, line.start.y
    x2, y2 = line.end.x, line.end.y

    dx = x2 - x1
    dy = y2 - y1
    fx = x1 - cx
    fy = y1 - cy

    a = dx * dx + dy * dy
    b = 2.0 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - r * r

    discriminant = b * b - 4.0 * a * c
    if discriminant < 0:
        return []

    discriminant = math.sqrt(discriminant)
    t1 = (-b - discriminant) / (2.0 * a)
    t2 = (-b + discriminant) / (2.0 * a)

    results = []
    for t in (t1, t2):
        if -1e-9 <= t <= 1.0 + 1e-9:
            results.append(Point(x1 + t * dx, y1 + t * dy))
    return results


def circle_circle_intersection(c1, c2):
    d = distance(c1.center, c2.center)
    if d > c1.radius + c2.radius + 1e-9:
        return []
    if d < abs(c1.radius - c2.radius) - 1e-9:
        return []
    if d < 1e-12:
        return []

    a = (c1.radius * c1.radius - c2.radius * c2.radius + d * d) / (2.0 * d)
    h_sq = c1.radius * c1.radius - a * a
    if h_sq < 0:
        h_sq = 0.0
    h = math.sqrt(h_sq)

    x1, y1 = c1.center.x, c1.center.y
    x2, y2 = c2.center.x, c2.center.y

    dx = x2 - x1
    dy = y2 - y1

    px = x1 + a * dx / d
    py = y1 + a * dy / d

    rx = -dy * (h / d)
    ry = dx * (h / d)

    return [Point(px + rx, py + ry), Point(px - rx, py - ry)]


def tangent_points_from_point(circle, p):
    d = distance(p, circle.center)
    if d <= circle.radius:
        return []

    a = circle.radius * circle.radius / d
    h_sq = circle.radius * circle.radius - a * a
    h = math.sqrt(h_sq) if h_sq > 0 else 0.0

    x1, y1 = circle.center.x, circle.center.y
    x0, y0 = p.x, p.y

    dx = x0 - x1
    dy = y0 - y1

    px = x1 + a * dx / d
    py = y1 + a * dy / d

    rx = -dy * (h / d)
    ry = dx * (h / d)

    return [Point(px + rx, py + ry), Point(px - rx, py - ry)]