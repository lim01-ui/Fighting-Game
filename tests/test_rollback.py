"""Deterministic rollback and presentation behavior under delayed input."""
import copy
import unittest

from network.rollback import RollbackSession
from network.interpolation import RenderInterpolator


class ToyFight:
    """Tiny stateful combat model: movement, hits, meter and frame timers."""
    def __init__(self):
        self.state = {'x': [0, 4], 'health': [100, 100], 'meter': [0, 0],
                      'cooldown': [0, 0], 'ticks': 0}
        self.calls = []

    def capture(self):
        return copy.deepcopy(self.state)

    def restore(self, snapshot):
        self.state = copy.deepcopy(snapshot)

    def step(self, frame, first, second, replaying):
        self.calls.append((frame, replaying))
        inputs = first, second
        for index, values in enumerate(inputs):
            self.state['x'][index] += bool(values.get('right')) - bool(values.get('left'))
            self.state['cooldown'][index] = max(0, self.state['cooldown'][index] - 1)
        for index, values in enumerate(inputs):
            if (values.get('light') and self.state['cooldown'][index] == 0
                    and abs(self.state['x'][0] - self.state['x'][1]) < 6):
                self.state['health'][1 - index] -= 3
                self.state['meter'][index] += 3
                self.state['cooldown'][index] = 4
        self.state['ticks'] += 1

    def session(self, **kwargs):
        return RollbackSession(self.step, self.capture, self.restore, **kwargs)


class RollbackTests(unittest.TestCase):
    def test_local_movement_runs_immediately_without_peer_input(self):
        game = ToyFight()
        session = game.session()
        self.assertTrue(session.advance({'right': True}))
        self.assertEqual(game.state['x'], [1, 4])
        self.assertEqual(session.frame, 1)
        self.assertEqual(session.confirmed_frame, -1)

    def test_wrong_prediction_restores_health_meter_and_frame_data(self):
        game = ToyFight()
        session = game.session()
        for _ in range(4):
            session.advance({})
        session.receive_inputs({0: {'light': True}, 1: {}, 2: {}, 3: {}})
        expected = ToyFight()
        for frame in range(4):
            expected.step(frame, {}, {'light': frame == 0}, False)
        self.assertEqual(game.state, expected.state)
        self.assertEqual(session.corrections, 1)
        self.assertEqual(session.rollback_frames, 4)
        self.assertEqual(session.confirmed_frame, 3)
        self.assertTrue(all(replaying for _, replaying in game.calls[-4:]))

    def test_two_peers_converge_with_delayed_reordered_inputs(self):
        first, second, reference = ToyFight(), ToyFight(), ToyFight()
        first_session = first.session(local_player=1, max_prediction=12)
        second_session = second.session(local_player=2, max_prediction=12)
        input1 = [{'right': i < 3, 'light': i % 7 == 0} for i in range(120)]
        input2 = [{'left': i < 2, 'light': i % 9 == 0} for i in range(120)]
        for tick in range(120):
            self.assertTrue(first_session.advance(input1[tick]))
            self.assertTrue(second_session.advance(input2[tick]))
            reference.step(tick, input1[tick], input2[tick], False)
            if tick >= 4:
                # Deliver pairs in reverse tick order every other tick.
                if tick % 2 == 1:
                    a, b = tick - 4, tick - 5
                    first_session.receive_inputs({a: input2[a], b: input2[b]})
                    second_session.receive_inputs({a: input1[a], b: input1[b]})
        first_session.receive_inputs(dict(enumerate(input2)))
        second_session.receive_inputs(dict(enumerate(input1)))
        self.assertEqual(first.state, second.state)
        self.assertEqual(first.state, reference.state)
        self.assertEqual(first_session.confirmed_frame, 119)
        self.assertGreater(first_session.corrections, 0)

    def test_prediction_is_bounded_and_recovers_after_stall(self):
        game = ToyFight()
        session = game.session(max_prediction=3)
        for _ in range(3):
            self.assertTrue(session.advance({'right': True}))
        state = game.capture()
        self.assertFalse(session.advance({'right': True}))
        self.assertEqual(game.state, state)
        self.assertNotIn(3, session.local_history)
        session.receive_inputs({0: {}, 1: {}, 2: {}})
        self.assertTrue(session.advance({'right': True}))

    def test_future_packet_never_leaks_into_earlier_prediction(self):
        game = ToyFight()
        session = game.session()
        session.receive_inputs({3: {'left': True}})
        session.advance({})
        self.assertEqual(game.state['x'][1], 4)

    def test_predicts_held_action_but_not_match_control(self):
        game = ToyFight()
        session = game.session()
        session.receive_inputs({0: {'right': True, 'rematch': True, 'leave': True}})
        session.advance({})
        session.advance({})
        self.assertTrue(session.used_remote[1]['right'])
        self.assertFalse(session.used_remote[1]['rematch'])
        self.assertFalse(session.used_remote[1]['leave'])

    def test_duplicate_sparse_inputs_do_not_cause_false_corrections(self):
        game = ToyFight()
        session = game.session()
        session.advance({})
        session.receive_inputs({0: {'right': False}})
        session.receive_inputs({0: {}})
        self.assertEqual(session.corrections, 0)
        with self.assertRaisesRegex(ConnectionError, 'already submitted'):
            session.receive_inputs({0: {'right': True}})

    def test_history_is_bounded_and_keeps_remote_prediction_seed(self):
        game = ToyFight()
        session = game.session(max_prediction=3, history_size=6)
        for tick in range(30):
            session.receive_inputs({tick: {'right': True}})
            session.advance({})
        for history in (session.snapshots, session.local_history, session.remote_history):
            self.assertLessEqual(len(history), 6)
        session.advance({})
        self.assertTrue(session.used_remote[30]['right'])
        session.receive_inputs({0: {'left': True}})
        self.assertEqual(session.stale_packets, 1)


class InterpolationTests(unittest.TestCase):
    def test_smooths_remote_visual_two_ticks_behind_without_mutating_samples(self):
        interpolation = RenderInterpolator()
        for frame in range(3):
            interpolation.append(frame, frame * 10, 50)
        snapshots = list(interpolation.snapshots)
        self.assertEqual(interpolation.sample(2.5), (5, 50))
        self.assertEqual(interpolation.snapshots, snapshots)

    def test_reordered_and_duplicate_samples_are_sorted_and_bounded(self):
        interpolation = RenderInterpolator()
        for frame in (0, 2, 1, 2, 3):
            interpolation.append(frame, frame * 5, 0)
        self.assertEqual([sample[0] for sample in interpolation.snapshots], [1, 2, 3])
        self.assertFalse(interpolation.append(0, 99, 0))
        self.assertEqual(interpolation.sample(4.5), (12.5, 0))

    def test_gap_extrapolation_is_limited_to_one_tick_then_holds(self):
        interpolation = RenderInterpolator(delay_frames=0)
        interpolation.append(0, 0, 0)
        interpolation.append(1, 10, 0)
        self.assertEqual(interpolation.sample(1.5), (15, 0))
        self.assertEqual(interpolation.sample(100), (20, 0))
        interpolation.append(20, 500, 0)
        self.assertEqual(interpolation.sample(100), (500, 0))

    def test_replayed_positions_replace_incorrect_future_visuals(self):
        interpolation = RenderInterpolator(delay_frames=0)
        for frame in range(3):
            interpolation.append(frame, frame * 10, 0)
        interpolation.append(1, 2, 0, replaying=True)
        interpolation.append(2, 4, 0, replaying=True)
        self.assertEqual(interpolation.sample(1.5), (3, 0))


if __name__ == '__main__':
    unittest.main()
