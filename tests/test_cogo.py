# -*- coding: utf-8 -*-
"""Tests for COGO Engine"""
import os
import sys
import math
import unittest

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.coordinate_rules import Point, bearing, distance, polar
from shared.specifications.cogo_engine import (
    point_from_bearing_distance, bearing_distance_from_points,
    intersection_line_line, area_of_polygon, perimeter_of_polygon
)
from shared.specifications.geometry_engine import Line
from shared.specifications.cogo_geometry import Circle, circle_line_intersection, circle_circle_intersection


class TestCoordinateRules(unittest.TestCase):
    def test_bearing_north(self):
        p1 = Point(0, 0)
        p2 = Point(0, 100)
        self.assertAlmostEqual(bearing(p1, p2), 0.0, places=6)

    def test_bearing_east(self):
        p1 = Point(0, 0)
        p2 = Point(100, 0)
        self.assertAlmostEqual(bearing(p1, p2), 90.0, places=6)

    def test_bearing_south(self):
        p1 = Point(0, 0)
        p2 = Point(0, -100)
        self.assertAlmostEqual(bearing(p1, p2), 180.0, places=6)

    def test_bearing_west(self):
        p1 = Point(0, 0)
        p2 = Point(-100, 0)
        self.assertAlmostEqual(bearing(p1, p2), 270.0, places=6)

    def test_distance(self):
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        self.assertAlmostEqual(distance(p1, p2), 5.0, places=6)

    def test_polar(self):
        origin = Point(0, 0)
        p = polar(origin, 90.0, 100.0)
        self.assertAlmostEqual(p.x, 100.0, places=6)
        self.assertAlmostEqual(p.y, 0.0, places=6)


class TestCOGOEngine(unittest.TestCase):
    def test_point_from_bearing_distance(self):
        origin = Point(500000.0, 3000000.0)
        result = point_from_bearing_distance(origin, 35.3361, 25.450)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.point)
        self.assertGreater(result.point.x, 500000)
        self.assertGreater(result.point.y, 3000000)

    def test_bearing_distance_from_points(self):
        p1 = Point(500000.0, 3000000.0)
        p2 = Point(500021.0, 3000025.0)
        result = bearing_distance_from_points(p1, p2)
        self.assertTrue(result.success)
        self.assertGreater(result.distance, 0)
        self.assertGreaterEqual(result.bearing, 0)
        self.assertLess(result.bearing, 360)

    def test_line_intersection(self):
        l1 = Line(Point(0, 0), Point(100, 100))
        l2 = Line(Point(0, 100), Point(100, 0))
        result = intersection_line_line(l1, l2)
        self.assertTrue(result.success)
        self.assertAlmostEqual(result.point.x, 50.0, places=6)
        self.assertAlmostEqual(result.point.y, 50.0, places=6)

    def test_parallel_lines_no_intersection(self):
        l1 = Line(Point(0, 0), Point(100, 0))
        l2 = Line(Point(0, 50), Point(100, 50))
        result = intersection_line_line(l1, l2)
        self.assertFalse(result.success)

    def test_area_of_polygon_square(self):
        points = [Point(0, 0), Point(100, 0), Point(100, 100), Point(0, 100)]
        area = area_of_polygon(points)
        self.assertAlmostEqual(area, 10000.0, places=2)

    def test_area_of_polygon_triangle(self):
        points = [Point(0, 0), Point(100, 0), Point(0, 100)]
        area = area_of_polygon(points)
        self.assertAlmostEqual(area, 5000.0, places=2)

    def test_perimeter_of_polygon(self):
        points = [Point(0, 0), Point(3, 0), Point(3, 4)]
        perim = perimeter_of_polygon(points)
        self.assertAlmostEqual(perim, 12.0, places=6)


class TestGeometryEngine(unittest.TestCase):
    def test_circle_line_intersection(self):
        circle = Circle(Point(0, 0), 50.0)
        line = Line(Point(-100, 0), Point(100, 0))
        pts = circle_line_intersection(circle, line)
        self.assertEqual(len(pts), 2)
        xs = sorted([p.x for p in pts])
        self.assertAlmostEqual(xs[0], -50.0, places=6)
        self.assertAlmostEqual(xs[1], 50.0, places=6)

    def test_circle_circle_intersection(self):
        c1 = Circle(Point(0, 0), 50.0)
        c2 = Circle(Point(50, 0), 50.0)
        pts = circle_circle_intersection(c1, c2)
        self.assertEqual(len(pts), 2)

    def test_no_intersection_disjoint_circles(self):
        c1 = Circle(Point(0, 0), 10.0)
        c2 = Circle(Point(100, 0), 10.0)
        pts = circle_circle_intersection(c1, c2)
        self.assertEqual(len(pts), 0)


class TestQCEngine(unittest.TestCase):
    def test_check_duplicate_points(self):
        from shared.specifications.qc_engine import check_duplicate_points
        points = [Point(0, 0), Point(0.0001, 0.0001), Point(100, 100)]
        results = check_duplicate_points(points)
        self.assertGreater(len(results), 0)

    def test_check_self_intersection(self):
        from shared.specifications.qc_engine import check_self_intersection
        points = [Point(0, 0), Point(100, 100), Point(100, 0), Point(0, 100)]
        results = check_self_intersection(points)
        self.assertGreater(len(results), 0)

    def test_check_zero_area(self):
        from shared.specifications.qc_engine import check_zero_area
        points = [Point(0, 0), Point(1, 1), Point(2, 2)]
        results = check_zero_area(points)
        self.assertGreater(len(results), 0)


if __name__ == "__main__":
    unittest.main()