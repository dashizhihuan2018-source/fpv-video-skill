#!/usr/bin/env python3
"""Independent FPV teaching data, using only Python's standard library.

Units: metres, seconds, radians internally. Right-handed Z-up world; +X forward
at zero heading. ZYX quaternion construction uses +pitch nose-down. No DCC,
source assets, external geometry, network, or renderer is accessed.
"""

import argparse
import bisect
import json
import math
from pathlib import Path


def curve(u):
    return [60.0 * u, 8.0 * math.sin(2.0 * math.pi * u),
            4.0 + math.sin(math.pi * u)]


def derivatives(u):
    first = [60.0, 16.0 * math.pi * math.cos(2.0 * math.pi * u),
             math.pi * math.cos(math.pi * u)]
    second = [0.0, -32.0 * math.pi**2 * math.sin(2.0 * math.pi * u),
              -math.pi**2 * math.sin(math.pi * u)]
    return first, second


def smootherstep(t):
    """C2 time law with exact zero endpoint speed and acceleration."""
    return t**3 * (10.0 + t * (-15.0 + 6.0 * t))


def arc_table(steps=4096):
    if type(steps) is not int or steps < 2:
        raise ValueError('arc table needs at least two segments')
    cumulative = [0.0]
    previous = curve(0.0)
    for i in range(1, steps + 1):
        current = curve(i / steps)
        cumulative.append(cumulative[-1] + math.dist(previous, current))
        previous = current
    return cumulative


def distance_to_u(distance, cumulative):
    if distance <= 0.0:
        return 0.0
    if distance >= cumulative[-1]:
        return 1.0
    index = bisect.bisect_right(cumulative, distance) - 1
    fraction = ((distance - cumulative[index]) /
                (cumulative[index + 1] - cumulative[index]))
    return (index + fraction) / (len(cumulative) - 1)


def unwrap(previous, angle):
    if previous is None:
        return angle
    return previous + (angle - previous + math.pi) % (2.0 * math.pi) - math.pi


def quaternion(yaw, pitch, roll):
    cy, sy = math.cos(yaw / 2.0), math.sin(yaw / 2.0)
    cp, sp = math.cos(pitch / 2.0), math.sin(pitch / 2.0)
    cr, sr = math.cos(roll / 2.0), math.sin(roll / 2.0)
    return [sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
            cr * cp * cy + sr * sp * sy]


def segment_aabb(a, b, low, high):
    """Continuous line segment slab intersection, including boundary contact."""
    enter, leave = 0.0, 1.0
    for axis in range(3):
        delta = b[axis] - a[axis]
        if abs(delta) < 1e-14:
            if not low[axis] <= a[axis] <= high[axis]:
                return None
            continue
        p = (low[axis] - a[axis]) / delta
        q = (high[axis] - a[axis]) / delta
        enter, leave = max(enter, min(p, q)), min(leave, max(p, q))
        if enter > leave:
            return None
    return enter, leave


def gate_clearance(points, gate, padding):
    """Conservative swept sphere vs axis-aligned planar opening in X slab.

    Restricted to the piecewise-linear route, not the analytic intersample arc.
    Positive padding shrinks aperture and expands the plane's thickness.
    """
    center, half = gate['center_m'], gate['half_opening_yz_m']
    if padding < 0 or any(size <= padding for size in half):
        raise ValueError('opening is smaller than swept clearance')
    lo = center[0] - gate['thickness_m'] / 2.0 - padding
    hi = center[0] + gate['thickness_m'] / 2.0 + padding
    crossed = False
    for a, b in zip(points, points[1:]):
        dx = b[0] - a[0]
        if abs(dx) < 1e-14:
            interval = (0.0, 1.0) if lo <= a[0] <= hi else None
        else:
            p, q = (lo - a[0]) / dx, (hi - a[0]) / dx
            interval = max(0.0, min(p, q)), min(1.0, max(p, q))
            if interval[0] > interval[1]:
                interval = None
        if interval is None:
            continue
        crossed = True
        for t in interval:
            for axis, aperture in ((1, half[0]), (2, half[1])):
                value = a[axis] + t * (b[axis] - a[axis])
                if abs(value - center[axis]) + padding >= aperture:
                    raise ValueError('swept route hits gate aperture: ' + gate['id'])
    # Overlap without an actual passage is not counted as a gate traversal.
    if not crossed or not ((points[0][0] < lo and points[-1][0] > hi) or
                           (points[-1][0] < lo and points[0][0] > hi)):
        raise ValueError('route does not traverse gate: ' + gate['id'])
    return {'gate': gate['id'], 'piecewise_linear_clearance_pass': True}


def abstract_scene():
    gates, boxes = [], []
    for index, u in enumerate((0.30, 0.72)):
        center = curve(u)
        gate = {'id': 'abstract-opening-' + str(index + 1),
                'center_m': center, 'normal': [1.0, 0.0, 0.0],
                'half_opening_yz_m': [2.5, 2.5], 'thickness_m': 0.4}
        gates.append(gate)
        for sign in (-1, 1):
            boxes.append({'id': gate['id'] + '-post-' + str(sign),
                          'center_m': [center[0], center[1] + sign * 3.0, center[2]],
                          'half_extents_m': [0.2, 0.5, 3.0]})
        boxes.append({'id': gate['id'] + '-lintel',
                      'center_m': [center[0], center[1], center[2] + 3.0],
                      'half_extents_m': [0.2, 3.5, 0.5]})
    return {'gates': gates, 'boxes': boxes}


def diagnostics(rows, fps):
    velocities = [[(b - a) * fps for a, b in zip(p['position_m'], q['position_m'])]
                  for p, q in zip(rows, rows[1:])]
    accelerations = [[(b - a) * fps for a, b in zip(p, q)]
                     for p, q in zip(velocities, velocities[1:])]
    jerks = [[(b - a) * fps for a, b in zip(p, q)]
             for p, q in zip(accelerations, accelerations[1:])]
    norm = lambda vector: math.sqrt(sum(x * x for x in vector))
    return {'finite_difference_peak_speed_m_s': max(map(norm, velocities)),
            'finite_difference_peak_acceleration_m_s2': max(map(norm, accelerations)),
            'finite_difference_peak_jerk_m_s3': max(map(norm, jerks)),
            'limits_optimized_or_accepted': False}


def generate(fps=30, seconds=12.0, radius=0.25, margin=0.40):
    if type(fps) is not int or not 1 <= fps <= 240:
        raise ValueError('fps must be an integer in 1..240')
    if not math.isfinite(seconds) or seconds <= 0 or seconds * fps > 100000:
        raise ValueError('duration must be positive and at most 100000 frames')
    count = round(seconds * fps)
    if count < 4 or abs(count - seconds * fps) > 1e-8:
        raise ValueError('duration must give an integer number of at least four frames')
    if not all(math.isfinite(x) and x >= 0 for x in (radius, margin)):
        raise ValueError('radius and margin must be finite and nonnegative')
    cumulative = arc_table()
    length = cumulative[-1]
    rows, last_yaw, last_gaze_yaw = [], None, None
    for frame in range(count + 1):
        t = frame / count
        distance = length * smootherstep(t)
        u = distance_to_u(distance, cumulative)
        position = curve(u)
        first, second = derivatives(u)
        speed = length * 30.0 * t**2 * (1.0 - t)**2 / seconds
        accel = length * 60.0 * t * (1.0 - t) * (1.0 - 2.0 * t) / seconds**2
        curvature = ((first[0] * second[1] - first[1] * second[0]) /
                     (first[0]**2 + first[1]**2)**1.5)
        yaw = unwrap(last_yaw, math.atan2(first[1], first[0]))
        pitch = -math.atan2(first[2], math.hypot(first[0], first[1]))
        # Negative roll banks toward +Y (left) in this declared coordinate system.
        roll = max(-math.radians(35), min(math.radians(35),
                   -math.atan2(speed**2 * curvature, 9.81)))
        target_distance = distance + 4.0
        target = curve(distance_to_u(target_distance, cumulative))
        if target_distance > length:
            tangent, _ = derivatives(1.0)
            norm = math.sqrt(sum(x * x for x in tangent))
            target = [a + (target_distance - length) * d / norm
                      for a, d in zip(curve(1.0), tangent)]
        gaze = [b - a for a, b in zip(position, target)]
        gaze_yaw = unwrap(last_gaze_yaw, math.atan2(gaze[1], gaze[0]))
        gaze_pitch = -math.atan2(gaze[2], math.hypot(gaze[0], gaze[1]))
        rows.append({'frame': frame, 'time_s': frame / fps,
                     'output_frame': frame < count, 'position_m': position,
                     'distance_m': distance, 'speed_m_s': speed,
                     'tangential_acceleration_m_s2': accel,
                     'signed_horizontal_curvature_m_inv': curvature,
                     'body_yaw_pitch_roll_deg': list(map(math.degrees, (yaw, pitch, roll))),
                     'body_quaternion_xyzw': quaternion(yaw, pitch, roll),
                     'gaze_target_m': target,
                     'gaze_yaw_pitch_roll_deg': list(map(math.degrees, (gaze_yaw, gaze_pitch, 0.0))),
                     'gaze_quaternion_xyzw': quaternion(gaze_yaw, gaze_pitch, 0.0)})
        last_yaw, last_gaze_yaw = yaw, gaze_yaw
    scene = abstract_scene()
    points = [row['position_m'] for row in rows]
    clearance = [gate_clearance(points, gate, radius + margin) for gate in scene['gates']]
    for box in scene['boxes']:
        low = [p - h - radius - margin for p, h in zip(box['center_m'], box['half_extents_m'])]
        high = [p + h + radius + margin for p, h in zip(box['center_m'], box['half_extents_m'])]
        if any(segment_aabb(a, b, low, high) is not None for a, b in zip(points, points[1:])):
            raise ValueError('swept route intersects box: ' + box['id'])
    return {'schema': 'fpv-independent-synthetic-route-v1',
            'provenance': 'new analytic curve and abstract boxes; no project assets',
            'coordinate_system': 'right-handed Z-up; ZYX; +pitch nose-down; metres',
            'native_or_visual_acceptance': False, 'fps': fps, 'duration_s': seconds,
            'output_frame_range_inclusive': [0, count - 1],
            'boundary_key_range_inclusive': [0, count], 'route_length_m': length,
            'swept_radius_m': radius, 'safety_margin_m': margin,
            'scene': scene, 'clearance_receipts': clearance,
            'diagnostics': diagnostics(rows, fps), 'keys': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--seconds', type=float, default=12.0)
    parser.add_argument('--radius', type=float, default=0.25)
    parser.add_argument('--margin', type=float, default=0.40)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('refusing to overwrite existing output')
    try:
        route = generate(args.fps, args.seconds, args.radius, args.margin)
    except ValueError as error:
        parser.error(str(error))
    # Exclusive creation protects existing data if another process creates it now.
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(route, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    print('Synthetic JSON generated; not native or visual acceptance:', args.output)


if __name__ == '__main__':
    main()
