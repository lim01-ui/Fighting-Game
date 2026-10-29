"""Input prediction and bounded rollback, independent of rendering and transport.

The game owns state serialization. ``capture`` must return an independent snapshot;
``restore`` must restore it without modifying that snapshot. Simulation callbacks
must use a fixed tick and deterministic gameplay state, including any RNG state.
"""


class RollbackSession:
    def __init__(self, step, capture, restore, local_player=1,
                 max_prediction=8, history_size=180):
        if local_player not in (1, 2):
            raise ValueError("local_player must be 1 or 2")
        if max_prediction < 1 or history_size < max_prediction:
            raise ValueError("history_size must cover the prediction window")
        self.step = step
        self.capture = capture
        self.restore = restore
        self.local_player = local_player
        self.max_prediction = max_prediction
        self.history_size = history_size
        self.frame = 0
        self.confirmed_frame = -1
        self.corrections = 0
        self.rollback_frames = 0
        self.predicted_frames = 0
        self.stale_packets = 0
        self.local_history = {}
        self.remote_history = {}
        self.snapshots = {}
        self.used_remote = {}
        self._history_floor = 0
        self._remote_seed = (-1, {})

    @staticmethod
    def _inputs(values):
        return {action: bool(pressed) for action, pressed in values.items()}

    @staticmethod
    def _same_inputs(first, second):
        # Missing actions mean released; callers may send either sparse or full
        # dictionaries without generating a false rollback.
        return ({key for key, value in first.items() if value}
                == {key for key, value in second.items() if value})

    def _remote_for(self, frame):
        if frame in self.remote_history:
            return dict(self.remote_history[frame]), False
        candidates = [number for number in self.remote_history if number < frame]
        if candidates:
            values = dict(self.remote_history[max(candidates)])
        else:
            values = dict(self._remote_seed[1])
        # Continuing movement/attacks is a useful short prediction. A predicted
        # menu action must never restart or leave a match.
        values['rematch'] = False
        values['leave'] = False
        return values, True

    def _run_tick(self, frame, replaying):
        self.snapshots[frame] = self.capture()
        remote, predicted = self._remote_for(frame)
        self.used_remote[frame] = remote
        local = self.local_history[frame]
        p1, p2 = ((local, remote) if self.local_player == 1 else (remote, local))
        self.step(frame, dict(p1), dict(p2), replaying)
        if predicted and not replaying:
            self.predicted_frames += 1

    def advance(self, local_inputs):
        """Apply one fixed tick immediately, or pause at the prediction limit.

        The caller submits ``local_inputs`` to the network for ``self.frame``
        before calling this method. A false return means no state or history was
        advanced; events and networking should continue while simulation waits.
        """
        if self.frame - self.confirmed_frame - 1 >= self.max_prediction:
            return False
        self.local_history[self.frame] = self._inputs(local_inputs)
        self._run_tick(self.frame, replaying=False)
        self.frame += 1
        self._confirm_and_prune()
        return True

    def receive_inputs(self, frames):
        """Install actual remote inputs and replay the earliest wrong prediction.

        Packets may be duplicated, reordered, or arrive ahead of simulation.
        Conflicting actual inputs are a protocol error: a peer cannot rewrite an
        input it already submitted. Old packets outside retained history are
        ignored; the prediction cap guarantees they cannot require a rollback.
        """
        earliest = None
        for number, values in frames.items():
            if not isinstance(number, int) or number < 0:
                raise ConnectionError("Received an invalid input frame")
            if number > self.frame + self.history_size:
                raise ConnectionError("Remote input is too far ahead of simulation")
            if number < self._history_floor:
                self.stale_packets += 1
                continue
            values = self._inputs(values)
            if number in self.remote_history:
                if not self._same_inputs(values, self.remote_history[number]):
                    raise ConnectionError("Peer changed an already submitted input")
                continue
            self.remote_history[number] = values
            if (number < self.frame
                    and not self._same_inputs(values, self.used_remote[number])):
                earliest = number if earliest is None else min(earliest, number)
        if earliest is not None:
            self.restore(self.snapshots[earliest])
            self.corrections += 1
            self.rollback_frames += self.frame - earliest
            for number in range(earliest, self.frame):
                self._run_tick(number, replaying=True)
        self._confirm_and_prune()

    def _confirm_and_prune(self):
        while (self.confirmed_frame + 1 < self.frame
               and self.confirmed_frame + 1 in self.remote_history):
            self.confirmed_frame += 1
        floor = max(0, min(self.frame - self.history_size, self.confirmed_frame + 1))
        if floor <= self._history_floor:
            return
        older_remote = [number for number in self.remote_history if number < floor]
        if older_remote:
            last = max(older_remote)
            self._remote_seed = (last, dict(self.remote_history[last]))
        for history in (self.local_history, self.remote_history, self.snapshots, self.used_remote):
            for number in list(history):
                if number < floor:
                    del history[number]
        self._history_floor = floor

    def get_stats(self):
        return {
            'frame': self.frame,
            'confirmed_frame': self.confirmed_frame,
            'prediction_depth': self.frame - self.confirmed_frame - 1,
            'corrections': self.corrections,
            'rollback_frames': self.rollback_frames,
            'predicted_frames': self.predicted_frames,
            'stale_packets': self.stale_packets,
        }
