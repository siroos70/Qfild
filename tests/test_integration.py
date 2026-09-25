# -*- coding: utf-8 -*-
"""Integration Tests for GeoSurvey Plugin"""
import os
import sys
import math
import unittest

_PROJECT_ROOT = "F:\\QGIS_script"
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.coordinate_rules import Point, bearing, distance, polar
from shared.specifications.cogo_engine import (
    point_from_bearing_distance, bearing_distance_from_points,
    intersection_line_line, area_of_polygon, perimeter_of_polygon
)
from shared.specifications.geometry_engine import Line
from shared.specifications.cogo_geometry import Circle, circle_line_intersection, circle_circle_intersection
from shared.specifications.qc_engine import (
    QCStatus, check_duplicate_points, check_self_intersection,
    check_zero_area, check_point_in_polygon
)


class TestIntegration(unittest.TestCase):
    """Integration tests using real-world survey values."""

    def test_known_point_bearing_distance(self):
        origin = Point(500000.000, 3000000.000)
        result = point_from_bearing_distance(origin, 35.3361, 25.450)
        self.assertTrue(result.success)
        # x = 500000 + 25.450 * sin(35.3361) = 500014.720
        # y = 3000000 + 25.450 * cos(35.3361) = 3000020.762
        self.assertAlmostEqual(result.point.x, 500014.720, places=1)
        self.assertAlmostEqual(result.point.y, 3000020.762, places=1)

    def test_known_bearing_distance(self):
        p1 = Point(500000.000, 3000000.000)
        p2 = Point(500021.000, 3000025.000)
        result = bearing_distance_from_points(p1, p2)
        self.assertTrue(result.success)
        self.assertAlmostEqual(result.distance, 32.649, places=1)

    def test_line_intersection_real(self):
        l1 = Line(Point(500000, 3000000), Point(500100, 3000100))
        l2 = Line(Point(500000, 3000100), Point(500100, 3000000))
        result = intersection_line_line(l1, l2)
        self.assertTrue(result.success)
        self.assertAlmostEqual(result.point.x, 500050.0, places=1)
        self.assertAlmostEqual(result.point.y, 3000050.0, places=1)

    def test_circle_intersection_real(self):
        c1 = Circle(Point(500000, 3000000), 50.0)
        c2 = Circle(Point(500050, 3000000), 50.0)
        pts = circle_circle_intersection(c1, c2)
        self.assertEqual(len(pts), 2)

    def test_polygon_area_known(self):
        points = [
            Point(500000, 3000000),
            Point(500100, 3000000),
            Point(500100, 3000100),
            Point(500000, 3000100)
        ]
        area = area_of_polygon(points)
        self.assertAlmostEqual(area, 10000.0, places=1)

    def test_traverse_computation(self):
        points = [
            Point(500000, 3000000),
            Point(500100, 3000000),
            Point(500100, 3000100)
        ]
        perim = perimeter_of_polygon(points)
        # 100 + 100 + sqrt(100^2+100^2) = 100 + 100 + 141.421 = 341.421
        self.assertAlmostEqual(perim, 341.421, places=1)

    def test_qc_geometry_checks(self):
        points = [
            Point(500000, 3000000),
            Point(500000.0001, 3000000.0001),
            Point(500100, 3000100)
        ]
        results = check_duplicate_points(points)
        self.assertGreater(len(results), 0)

    def test_qc_self_intersection(self):
        points = [
            Point(0, 0), Point(100, 100),
            Point(100, 0), Point(0, 100)
        ]
        results = check_self_intersection(points)
        self.assertGreater(len(results), 0)

    def test_qc_zero_area(self):
        points = [Point(0, 0), Point(1, 1), Point(2, 2)]
        results = check_zero_area(points)
        self.assertGreater(len(results), 0)

    def test_point_in_polygon(self):
        poly = [Point(0, 0), Point(100, 0), Point(100, 100), Point(0, 100)]
        inside = check_point_in_polygon(Point(50, 50), poly)
        self.assertTrue(inside)
        outside = check_point_in_polygon(Point(150, 150), poly)
        self.assertFalse(outside)

    def test_coordinate_transform_consistency(self):
        p1 = Point(500000, 3000000)
        p2 = Point(500000, 3000000)
        d = distance(p1, p2)
        self.assertAlmostEqual(d, 0.0, places=10)

    def test_bearing_round_trip(self):
        p1 = Point(500000, 3000000)
        p2 = Point(500100, 3000050)
        brg = bearing(p1, p2)
        recovered = polar(p1, brg, distance(p1, p2))
        self.assertAlmostEqual(recovered.x, p2.x, places=6)
        self.assertAlmostEqual(recovered.y, p2.y, places=6)


if __name__ == "__main__":
    unittest.main()