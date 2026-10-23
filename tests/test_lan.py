"""LAN regression tests use real TCP connections on loopback."""
import json
import socket
import struct
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
