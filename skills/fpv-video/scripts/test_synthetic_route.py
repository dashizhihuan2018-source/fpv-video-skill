"""Behavioral tests for independent synthetic data, not source-project proof."""

import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import synthetic_route as route


class SyntheticRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = route.generate()

    def test_output_and_end_boundary_are_different(self):
        data = self.data
        self.assertEqual(data['output_frame_range_inclusive'], [0, 359])
        self.assertEqual(data['boundary_key_range_inclusive'], [0, 360])
        self.assertEqual(len(data['keys']), 361)
        self.assertEqual(sum(row['output_frame'] for row in data['keys']), 360)
        self.assertTrue(data['keys'][0]['output_frame'])
        self.assertFalse(data['keys'][-1]['output_frame'])

    def test_endpoint_speed_and_acceleration_are_zero(self):
        for row in (self.data['keys'][0], self.data['keys'][-1]):
            self.assertEqual(row['speed_m_s'], 0.0)
            self.assertEqual(row['tangential_acceleration_m_s2'], 0.0)

    def test_arc_length_distance_and_positions_are_monotonic(self):
        rows = self.data['keys']
        self.assertTrue(all(a['distance_m'] < b['distance_m'] for a, b in zip(rows, rows[1:])))
        self.assertTrue(all(a['position_m'][0] < b['position_m'][0] for a, b in zip(rows, rows[1:])))
        self.assertAlmostEqual(rows[-1]['distance_m'], self.data['route_length_m'])
        self.assertAlmostEqual(rows[-1]['position_m'][0], 60.0)

    def test_arc_lookup_matches_independent_finer_integration(self):
        table = route.arc_table()
        for fraction in (0.1, 0.3, 0.6, 0.9):
            target = table[-1] * fraction
            u = route.distance_to_u(target, table)
            previous, distance = route.curve(0), 0.0
            for i in range(1, 10001):
                point = route.curve(u * i / 10000)
                distance += math.dist(previous, point)
                previous = point
            self.assertAlmostEqual(distance, target, delta=0.0001)

    def test_all_values_serializable_without_nan(self):
        json.dumps(self.data, allow_nan=False)

    def test_body_and_gaze_are_independent_and_quaternions_unit(self):
        self.assertTrue(any(abs(row['body_yaw_pitch_roll_deg'][0] -
                                row['gaze_yaw_pitch_roll_deg'][0]) > 1.0
                            for row in self.data['keys']))
        for row in self.data['keys']:
            for field in ('body_quaternion_xyzw', 'gaze_quaternion_xyzw'):
                self.assertAlmostEqual(sum(x*x for x in row[field]), 1.0, places=12)

    def test_bank_tracks_speed_curvature_and_is_limited(self):
        for row in self.data['keys']:
            bank = row['body_yaw_pitch_roll_deg'][2]
            curvature = row['signed_horizontal_curvature_m_inv']
            self.assertLessEqual(abs(bank), 35.0)
            self.assertLessEqual(bank * curvature, 1e-10)
            if row['speed_m_s'] == 0.0:
                self.assertEqual(bank, 0.0)

    def test_adjacent_orientation_is_continuous(self):
        for a, b in zip(self.data['keys'], self.data['keys'][1:]):
            for field in ('body_quaternion_xyzw', 'gaze_quaternion_xyzw'):
                dot = abs(sum(x*y for x, y in zip(a[field], b[field])))
                self.assertLess(2 * math.acos(min(1.0, dot)), math.radians(10))

    def test_unwrap_crosses_180_without_full_spin(self):
        value = route.unwrap(math.radians(179), math.radians(-179))
        self.assertAlmostEqual(math.degrees(value), 181.0)

    def test_synthetic_openings_traversed(self):
        self.assertEqual(len(self.data['clearance_receipts']), 2)
        self.assertTrue(all(row['piecewise_linear_clearance_pass']
                            for row in self.data['clearance_receipts']))

    def test_gate_rejects_between_frame_collision(self):
        gate = {'id': 'test', 'center_m': [0, 0, 0],
                'half_opening_yz_m': [1, 1], 'thickness_m': 0.4}
        with self.assertRaises(ValueError):
            route.gate_clearance([[-2, 2, 0], [2, 2, 0]], gate, 0.1)
        with self.assertRaises(ValueError):
            route.gate_clearance([[-2, 0, 0], [2, 0, 0]], gate, 1.1)
        with self.assertRaises(ValueError):
            route.gate_clearance([[-2, 0, 0], [-1, 0, 0]], gate, 0.1)

    def test_segment_box_intersection_is_continuous(self):
        hit = route.segment_aabb([-10, 0, 0], [10, 0, 0], [-1]*3, [1]*3)
        self.assertAlmostEqual(hit[0], 0.45)
        self.assertAlmostEqual(hit[1], 0.55)
        self.assertIsNone(route.segment_aabb([-10, 2, 0], [10, 2, 0], [-1]*3, [1]*3))

    def test_invalid_parameters_fail(self):
        for kwargs in ({'fps': 0}, {'fps': 30.0}, {'seconds': float('nan')},
                       {'seconds': 0}, {'seconds': 0.01}, {'seconds': 1.01},
                       {'radius': -1}, {'margin': float('inf')}, {'radius': 4}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                route.generate(**kwargs)

    def test_duration_is_not_fixed_to_case_study(self):
        data = route.generate(fps=24, seconds=10)
        self.assertEqual(len(data['keys']), 241)
        self.assertEqual(data['output_frame_range_inclusive'], [0, 239])

    def test_diagnostics_are_not_visual_or_limit_acceptance(self):
        self.assertFalse(self.data['native_or_visual_acceptance'])
        self.assertFalse(self.data['diagnostics']['limits_optimized_or_accepted'])
        for key, value in self.data['diagnostics'].items():
            if key.startswith('finite_difference_peak_'):
                self.assertGreater(value, 0)
                self.assertTrue(math.isfinite(value))

    def test_cli_writes_json_and_refuses_overwrite(self):
        # Keep test writes inside the repository's staging boundary.
        staging = Path(__file__).resolve().parents[3]
        with tempfile.TemporaryDirectory(prefix='.route-test-', dir=staging) as temp:
            output = Path(temp) / 'synthetic.json'
            cmd = [sys.executable, str(Path(route.__file__)), '--output', str(output)]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(output.read_text())['schema'], self.data['schema'])
            original = output.read_bytes()
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(original, output.read_bytes())


if __name__ == '__main__':
    unittest.main()
