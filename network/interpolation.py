"""Tiny tick-tagged position buffer for remote *visuals* only.

Never write sampled positions into gameplay objects: hit detection must use the
rollback simulation's positions, not this delayed presentation.
"""


class RenderInterpolator:
    def __init__(self, delay_frames=2.0, extrapolation_frames=1.0, capacity=3):
        if delay_frames < 0 or extrapolation_frames < 0 or capacity < 2:
            raise ValueError("Invalid interpolation buffer settings")
        self.delay_frames = float(delay_frames)
        self.extrapolation_frames = float(extrapolation_frames)
        self.capacity = capacity
        self.snapshots = []

    def append(self, frame, x, y, replaying=False):
        """Insert a snapshot; retain tick order and replace rollback corrections."""
        value = (float(frame), float(x), float(y))
        if replaying:
            self.discard_from(frame)
        if len(self.snapshots) == self.capacity and frame < self.snapshots[0][0]:
            return False
        self.snapshots = [item for item in self.snapshots if item[0] != frame]
        self.snapshots.append(value)
        self.snapshots.sort(key=lambda item: item[0])
        self.snapshots = self.snapshots[-self.capacity:]
        return True

    def discard_from(self, frame):
        """Remove predicted visual samples before appending replayed positions."""
        self.snapshots = [item for item in self.snapshots if item[0] < frame]

    def sample(self, render_frame):
        if not self.snapshots:
            return None
        target = render_frame - self.delay_frames
        first = self.snapshots[0]
        if target <= first[0]:
            return first[1], first[2]
        for left, right in zip(self.snapshots, self.snapshots[1:]):
            if target <= right[0]:
                fraction = (target - left[0]) / (right[0] - left[0])
                return (left[1] + (right[1] - left[1]) * fraction,
                        left[2] + (right[2] - left[2]) * fraction)
        latest = self.snapshots[-1]
        if len(self.snapshots) < 2:
            return latest[1], latest[2]
        previous = self.snapshots[-2]
        spacing = latest[0] - previous[0]
        # Do not infer a fresh velocity from a large gap in received snapshots.
        if spacing > self.capacity:
            return latest[1], latest[2]
        extra = min(self.extrapolation_frames, target - latest[0])
        return (latest[1] + (latest[1] - previous[1]) / spacing * extra,
                latest[2] + (latest[2] - previous[2]) / spacing * extra)
