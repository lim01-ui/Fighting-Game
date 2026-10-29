"""LAN regression tests use real TCP connections on loopback."""
import json
import socket
import struct
import threading
import time
import unittest
from unittest.mock import patch
from network import lan


class LanTests(unittest.TestCase):
    def setUp(self):
        self.listener = lan.create_host(port=0)
        self.port = self.listener.getsockname()[1]
        self.guest = lan.connect_to_host('127.0.0.1', self.port)
        self.host = lan.accept_if_ready(self.listener)
        self.assertIsNotNone(self.host)

    def tearDown(self):
        self.host.close()
        self.guest.close()
        self.listener.close()

    def poll_until(self, callback):
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            result = callback()
            if result is not None:
                return result
            time.sleep(0.001)
        self.fail('Timed out on loopback')

    def test_address_with_port(self):
        self.assertEqual(lan.parse_address(' 127.0.0.1:12345 '), ('127.0.0.1', 12345))
        for bad in ('', 'abc', '1.2.3', '999.0.0.1', '127.0.0.1:0', '127.0.0.1:65536'):
            with self.assertRaises(ValueError):
                lan.parse_address(bad)

    def test_fragmented_setup_does_not_block_or_consume_game_packet(self):
        setup = {'role': 'guest', 'protocol': lan.PROTOCOL_VERSION}
        payload = json.dumps(setup).encode()
        packet = struct.pack('!I', len(payload)) + payload
        self.guest.connection.sendall(packet[:2])
        self.assertIsNone(self.host.poll_setup())
        self.guest.connection.sendall(packet[2:6])
        self.assertIsNone(self.host.poll_setup())
        self.assertIsNone(self.host.poll_setup())
        self.guest.connection.sendall(packet[6:] + struct.pack('!IH', 0, 1))
        self.assertEqual(self.poll_until(self.host.poll_setup), setup)
        remote = self.poll_until(lambda: self.host.poll_inputs({}))
        self.assertTrue(remote['left'])

    def test_setup_disconnect_and_invalid_packets(self):
        self.guest.connection.sendall(struct.pack('!I', lan.MAX_SETUP_SIZE + 1))
        with self.assertRaises(ValueError):
            self.host.poll_setup()
        self.host._setup_buffer.clear()
        self.guest.close()
        with self.assertRaises(ConnectionError):
            self.host.poll_setup()

    def test_lockstep_keeps_the_submitted_input_snapshot(self):
        self.assertIsNone(self.host.poll_inputs({'light': True}))
        # Key released while waiting: this must not alter frame zero's snapshot.
        self.assertIsNone(self.host.poll_inputs({'light': False}))
        self.assertTrue(self.host.local_inputs['light'])
        host_values = self.poll_until(lambda: self.guest.poll_inputs({'right': True}))
        guest_values = self.poll_until(lambda: self.host.poll_inputs({'light': False}))
        self.assertTrue(host_values['light'])
        self.assertTrue(guest_values['right'])
        self.assertTrue(self.host.local_inputs['light'])
        self.assertIsNone(self.host.poll_inputs({'light': False}))
        self.assertFalse(self.host.local_inputs['light'])

    def test_stalled_peer_times_out(self):
        self.host.poll_inputs({})
        with patch.object(lan.time, 'monotonic', return_value=self.host._frame_started + 16):
            with self.assertRaisesRegex(ConnectionError, 'stopped responding'):
                self.host.poll_inputs({})

    def test_input_arriving_within_frame_budget_is_used_immediately(self):
        sender = threading.Timer(
            0.01, self.guest.connection.sendall,
            args=(struct.pack('!IH', 0, 1 << lan.ACTIONS.index('heavy')),),
        )
        sender.start()
        try:
            remote = self.host.poll_inputs({'light': True}, wait_timeout=0.5)
        finally:
            sender.join()
        self.assertIsNotNone(remote)
        self.assertTrue(remote['heavy'])
        self.assertTrue(self.host.local_inputs['light'])
        self.assertEqual(self.host._next_frame, 1)

    def test_frame_budget_expires_without_advancing_simulation(self):
        started = time.monotonic()
        self.assertIsNone(self.host.poll_inputs({}, wait_timeout=0.01))
        self.assertLess(time.monotonic() - started, 0.5)
        self.assertEqual(self.host._next_frame, 0)

    def test_repeated_frames_and_rematch_inputs(self):
        for frame in range(60):
            host_input = {'left': frame % 2 == 0, 'rematch': frame == 59}
            guest_input = {'heavy': frame % 3 == 0}
            self.assertIsNone(self.host.poll_inputs(host_input))
            received_host = self.poll_until(lambda: self.guest.poll_inputs(guest_input))
            received_guest = self.poll_until(lambda: self.host.poll_inputs(host_input))
            self.assertEqual(received_host['left'], host_input['left'])
            self.assertEqual(received_host['rematch'], host_input['rematch'])
            self.assertEqual(received_guest['heavy'], guest_input['heavy'])

    def test_async_submission_never_waits_for_other_player(self):
        started = time.monotonic()
        for frame in range(120):
            self.host.submit_input(frame, {'right': True, 'light': frame == 35})
        self.assertLess(time.monotonic() - started, 0.5)
        received = {}
        self.poll_until(lambda: received.update(self.guest.receive_inputs()) or
                        (True if len(received) == 120 else None))
        self.assertEqual(sorted(received), list(range(120)))
        self.assertTrue(all(values['right'] for values in received.values()))
        self.assertTrue(received[35]['light'])
        self.assertFalse(received[34]['light'])
        # The other player can then submit independently, with no request/reply lockstep.
        for frame in range(120):
            self.guest.submit_input(frame, {'block': frame >= 60})
        reply = {}
        self.poll_until(lambda: reply.update(self.host.receive_inputs()) or
                        (True if len(reply) == 120 else None))
        self.assertTrue(reply[60]['block'])
        self.assertFalse(reply[59]['block'])

    def test_async_deduplicates_retries_but_confirms_unchanged_ticks(self):
        self.host.submit_input(0, {'left': True})
        self.host.submit_input(0, {'left': True})
        self.host.submit_input(1, {'left': True})
        with self.assertRaisesRegex(ValueError, 'already submitted'):
            self.host.submit_input(0, {'left': False})
        received = {}
        self.poll_until(lambda: received.update(self.guest.receive_inputs()) or
                        (True if len(received) == 2 else None))
        self.assertEqual(set(received), {0, 1})
        self.assertEqual(self.host.get_stats()['sent_rate'], 2)
        self.assertEqual(self.guest.get_stats()['received_rate'], 2)
        self.assertEqual(lan.INPUT_PACKET.size, 6)

    def test_async_reassembles_fragmented_and_out_of_order_tick_records(self):
        self.host.start_input_transport()
        packet = lan.INPUT_PACKET.pack(2, 1) + lan.INPUT_PACKET.pack(0, 2) + lan.INPUT_PACKET.pack(2, 1)
        self.guest.connection.sendall(packet[:3])
        time.sleep(0.005)
        self.assertEqual(self.host.receive_inputs(), {})
        self.guest.connection.sendall(packet[3:8])
        received = {}
        self.poll_until(lambda: received.update(self.host.receive_inputs()) or
                        (True if 2 in received else None))
        self.assertEqual(set(received), {2})
        self.guest.connection.sendall(packet[8:])
        self.poll_until(lambda: received.update(self.host.receive_inputs()) or
                        (True if 0 in received else None))
        self.poll_until(lambda: True if self.host.get_stats()['duplicates'] == 1 else None)
        self.assertTrue(received[2]['left'])
        self.assertTrue(received[0]['right'])
        self.assertEqual(self.host.get_stats()['late_packets'], 1)

    def test_ping_echo_and_stats_do_not_invent_tcp_drop_counts(self):
        self.host.start_input_transport()
        self.guest.start_input_transport()
        self.poll_until(lambda: self.host.get_stats()['ping_ms'])
        stats = self.host.get_stats()
        self.assertGreaterEqual(stats['ping_ms'], 0)
        self.assertIsNone(stats['dropped_packets'])
        self.assertEqual(stats['sent_rate'], 0, 'Ping records are not gameplay input records')
        self.assertEqual(stats['received_rate'], 0)

    def test_async_rejects_invalid_masks_and_far_future_ticks(self):
        self.host.start_input_transport()
        self.guest.connection.sendall(lan.INPUT_PACKET.pack(0, 1 << len(lan.ACTIONS)))
        self.poll_until(lambda: self.host._error)
        with self.assertRaisesRegex(ConnectionError, 'invalid LAN input mask'):
            self.host.receive_inputs()

    def test_async_rejects_far_future_ticks(self):
        self.host.start_input_transport()
        self.guest.connection.sendall(lan.INPUT_PACKET.pack(lan.MAX_FRAME_AHEAD + 1, 0))
        self.poll_until(lambda: self.host._error)
        with self.assertRaisesRegex(ConnectionError, 'too far ahead'):
            self.host.receive_inputs()

    def test_early_player_can_wait_for_peers_intro_without_losing_ticks(self):
        for frame in range(8):
            self.host.submit_input(frame, {'light': frame == 0})
        # Simulate a slower intro without making this test sleep for seconds.
        self.host._transport_started -= 3.0
        self.assertEqual(self.host.receive_inputs(), {})
        received = {}
        self.poll_until(lambda: received.update(self.guest.receive_inputs()) or
                        (True if len(received) == 8 else None))
        for frame in range(8):
            self.guest.submit_input(frame, {'right': True})
        reply = {}
        self.poll_until(lambda: reply.update(self.host.receive_inputs()) or
                        (True if len(reply) == 8 else None))
        self.assertTrue(received[0]['light'])
        self.assertTrue(reply[7]['right'])

    def test_closed_peer_cannot_restart_transport(self):
        self.host.close()
        with self.assertRaisesRegex(ConnectionError, 'closed'):
            self.host.submit_input(0, {})
        with self.assertRaisesRegex(ConnectionError, 'closed'):
            self.host.receive_inputs()

    def test_enqueuing_input_signals_a_nonblocking_wakeup(self):
        # No worker is running, so the wake byte cannot race this assertion.
        self.host._queue_packet(0, 1)
        readable, _, _ = lan.select.select([self.host._wake_reader], [], [], 0)
        self.assertEqual(readable, [self.host._wake_reader])
        self.assertEqual(self.host._outgoing.get_nowait(), lan.INPUT_PACKET.pack(0, 1))
        self.host._signal_wake()
        self.host._signal_wake()
        self.host._drain_wake()
        readable, _, _ = lan.select.select([self.host._wake_reader], [], [], 0)
        self.assertEqual(readable, [], 'All coalesced wake bytes must be drained')
        self.assertEqual(self.host._wake_reader.gettimeout(), 0)
        self.assertEqual(self.host._wake_writer.gettimeout(), 0)

    def test_idle_worker_waits_on_wakeup_and_delivers_queued_input(self):
        waiting = threading.Event()
        actual_select = lan.select.select
        idle_timeouts = []
        def observe_select(readers, writers, exceptional, timeout):
            if self.host._wake_reader in readers and not writers:
                idle_timeouts.append(timeout)
                waiting.set()
            return actual_select(readers, writers, exceptional, timeout)
        with patch.object(lan.select, 'select', side_effect=observe_select):
            self.host.start_input_transport()
            self.assertTrue(waiting.wait(1), 'Worker must idle on socket readiness')
            self.host.submit_input(0, {'light': True})
            received = {}
            self.poll_until(lambda: received.update(self.guest.receive_inputs()) or
                            (True if 0 in received else None))
        self.assertTrue(received[0]['light'])
        self.assertGreater(idle_timeouts[0], 0.1, 'Idle worker must not poll every millisecond')

    def test_close_releases_wakeup_sockets_and_stops_idle_worker(self):
        self.host.start_input_transport()
        reader = self.host._reader
        self.host.close()
        self.assertFalse(reader.is_alive())
        self.assertEqual(self.host._wake_reader.fileno(), -1)
        self.assertEqual(self.host._wake_writer.fileno(), -1)
        self.guest.close()
        self.assertEqual(self.guest._wake_reader.fileno(), -1)
        self.assertEqual(self.guest._wake_writer.fileno(), -1)

    def test_full_send_queue_applies_backpressure_without_blocking(self):
        for _ in range(lan.MAX_BUFFERED_INPUTS):
            self.host._outgoing.put_nowait(lan.INPUT_PACKET.pack(0, 0))
        with self.assertRaisesRegex(ConnectionError, 'send buffer is full'):
            self.host._queue_packet(1, 0)

    def test_stale_duplicate_after_history_pruning_is_not_replayed(self):
        # The transport's replay window is larger than rollback history.
        self.host._highest_submitted = lan.MAX_BUFFERED_INPUTS + 1
        for frame in range(lan.MAX_BUFFERED_INPUTS + 1):
            self.host._process_packet(frame, 0)
            self.host._incoming.get_nowait()
        self.assertNotIn(0, self.host._received_frames)
        self.host._process_packet(0, 0)
        self.assertTrue(self.host._incoming.empty())
        self.assertEqual(self.host.get_stats()['late_packets'], 1)

    def test_host_port_cannot_be_claimed_twice_and_can_reopen(self):
        with self.assertRaises(OSError):
            lan.create_host(self.port)
        self.host.close()
        self.guest.close()
        self.listener.close()
        replacement = lan.create_host(self.port)
        replacement.close()


if __name__ == '__main__':
    unittest.main()
