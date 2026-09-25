import math
from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Dict, Any

from ..coordinate_rules import Point, bearing, distance, polar, inverse_bearing


@dataclass
class Line:
    """A 2D line defined by two points."""
    start: Point
    end: Point

    def length(self):
        return distance(self.start, self.end)

    def bearing(self):
        return bearing(self.start, self.end)

    def inverse_bearing(self):
        return inverse_bearing(self.start, self.end)

    def point_at_distance(self, dist):
        if self.length() == 0:
            return self.start
        ratio = dist / self.length()
        return Point(self.start.x + (self.end.x - self.start.x) * ratio,
                     self.start.y + (self.end.y - self.start.y) * ratio,
                     self.start.z)

    def offset_point(self, dist_along, offset_perp):
        brg = math.radians(self.bearing())
        perp = brg + math.pi / 2.0
        p = self.point_at_distance(dist_along)
        return Point(p.x + offset_perp * math.sin(perp),
                     p.y + offset_perp * math.cos(perp),
                     p.z)


def line_intersection(l1, l2):
    """Compute intersection of two lines."""
    x1, y1 = l1.start.x, l1.start.y
    x2, y2 = l1.end.x, l1.end.y
    x3, y3 = l2.start.x, l2.start.y
    x4, y4 = l2.end.x, l2.end.y

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-12:
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)
    return Point(x, y)


def segment_intersection(l1, l2):
    """Intersection of two line segments."""
    p = line_intersection(l1, l2)
    if p is None:
        return None
    if (min(l1.start.x, l1.end.x) - 1e-9 <= p.x <= max(l1.start.x, l1.end.x) + 1e-9 and
        min(l1.start.y, l1.end.y) - 1e-9 <= p.y <= max(l1.start.y, l1.end.y) + 1e-9 and
        min(l2.start.x, l2.end.x) - 1e-9 <= p.x <= max(l2.start.x, l2.end.x) + 1e-9 and
        min(l2.start.y, l2.end.y) - 1e-9 <= p.y <= max(l2.start.y, l2.end.y) + 1e-9):
        return p
    return None


def point_to_line_distance(p, line):
    """Perpendicular distance from point to infinite line."""
    x0, y0 = p.x, p.y
    x1, y1 = line.start.x, line.start.y
    x2, y2 = line.end.x, line.end.y
    num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    den = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    if den == 0:
        return distance(p, line.start)
    return num / den


def point_projection(p, line):
    """Project point onto infinite line."""
    x0, y0 = p.x, p.y
    x1, y1 = line.start.x, line.start.y
    x2, y2 = line.end.x, line.end.y
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return Point(x1, y1)
    t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)
    return Point(x1 + t * dx, y1 + t * dy, p.z)


def parallel_offset(line, offset):
    """Return a line parallel to the given line, offset to the right."""
    brg = math.radians(line.bearing())
    perp = brg + math.pi / 2.0
    ox = offset * math.sin(perp)
    oy = offset * math.cos(perp)
    return Line(Point(line.start.x + ox, line.start.y + oy),
                Point(line.end.x + ox, line.end.y + oy))


def perpendicular_offset(line, p):
    """Return (along_distance, perpendicular_offset) of point relative to line."""
    proj = point_projection(p, line)
    along = distance(line.start, proj)
    perp = distance(proj, p)
    brg_line = math.radians(line.bearing())
    brg_proj = bearing(proj, p)
    delta = (brg_proj - brg_line + 180.0) % 360.0 - 180.0
    if delta < 0:
        perp = -perp
    return along, perp