import math
from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Dict, Any


@dataclass
class Point:
    """A 2D/3D coordinate in projected system (X, Y, Z)."""
    x: float
    y: float
    z: float = 0.0

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def distance_to(self, other: "Point") -> float:
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)


def bearing(p1: Point, p2: Point) -> float:
    """Bearing from p1 to p2, clockwise from North, decimal degrees."""
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    brg = math.degrees(math.atan2(dx, dy))
    return (brg + 360.0) % 360.0


def distance(p1: Point, p2: Point) -> float:
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)


def polar(origin: Point, brg: float, dist: float) -> Point:
    """Compute new point from origin, bearing, distance."""
    rad = math.radians(brg)
    return Point(origin.x + dist * math.sin(rad),
                 origin.y + dist * math.cos(rad),
                 origin.z)


def inverse_bearing(p1: Point, p2: Point) -> float:
    return (bearing(p1, p2) + 180.0) % 360.0


def dms_to_decimal(degrees: int, minutes: float, seconds: float) -> float:
    sign = -1 if (degrees < 0 or minutes < 0 or seconds < 0) else 1
    return sign * (abs(degrees) + abs(minutes) / 60.0 + abs(seconds) / 3600.0)


def decimal_to_dms(decimal: float) -> Tuple[int, int, float]:
    deg = int(math.floor(abs(decimal)))
    minutes_full = (abs(decimal) - deg) * 60.0
    minutes = int(math.floor(minutes_full))
    seconds = (minutes_full - minutes) * 60.0
    return (deg if decimal >= 0 else -deg, minutes, seconds)


def format_bearing(bearing_deg: float) -> str:
    deg, minutes, seconds = decimal_to_dms(bearing_deg)
    return f"{deg}°{minutes:02d}'{seconds:05.2f}\""


def format_distance(meters: float) -> str:
    if meters >= 1000:
        return f"{meters / 1000.0:.3f} km"
    return f"{meters:.3f} m"


def format_area(square_meters: float) -> str:
    if square_meters >= 1_000_000:
        return f"{square_meters / 1_000_000.0:.4f} km²"
    elif square_meters >= 10000:
        return f"{square_meters / 10000.0:.4f} ha"
    return f"{square_meters:.3f} m²"
