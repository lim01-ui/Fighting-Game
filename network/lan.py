"""Compact asynchronous TCP input transport for rollback LAN matches.

Gameplay packets are six bytes: uint32 tick and uint16 action mask. No game
state or JSON is sent during a match. Reserved tick values carry ping echoes.
"""

import json
import queue
import select
import socket
import struct
import threading
import time
from collections import deque


PORT = 47611
# Increment when combat rules change: lockstep peers must simulate identical rules.
PROTOCOL_VERSION = 7
MAX_SETUP_SIZE = 4096
INPUT_TIMEOUT = 15.0
INPUT_PACKET = struct.Struct("!IH")
PING_FRAME = 0xFFFFFFFF
PONG_FRAME = 0xFFFFFFFE
MAX_BUFFERED_INPUTS = 2048
MAX_FRAME_AHEAD = 600
PING_INTERVAL = 0.5
ACTIONS = (
    "left", "right", "jump", "crouch", "block", "light", "heavy", "special",
    "rematch", "leave",
)


class LanPeer:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.connection.settimeout(300)
        self._incoming = queue.Queue(maxsize=MAX_BUFFERED_INPUTS)
        self._outgoing = queue.Queue(maxsize=MAX_BUFFERED_INPUTS)
        self._pending_inputs = {}
        self._next_frame = 0
        self._submitted_frame = None
        self._error = None
        self._closed = threading.Event()
        self._lifecycle_lock = threading.Lock()
        self._reader = None
        self.local_inputs = {}
        self._frame_started = None
        self._setup_buffer = bytearray()
        self._setup_started = None
        self._highest_submitted = -1
        self._highest_received = -1
        self._sent_frames = {}
        self._received_frames = {}
        self._transport_started = None
        self._last_received_input = None
        self._stats_lock = threading.Lock()
        self._sent_times = deque(maxlen=MAX_BUFFERED_INPUTS)
        self._received_times = deque(maxlen=MAX_BUFFERED_INPUTS)
        self._ping_started = {}
        self._ping_nonce = 0
        self._last_ping_sent = None
        self._ping_ms = None
        self._duplicates = 0
        self._late_packets = 0
        # select() can wait for either peer traffic or a newly queued local
        # input. This avoids adding a polling/scheduler delay to every send.
        self._wake_reader, self._wake_writer = socket.socketpair()
        self._wake_reader.setblocking(False)
        self._wake_writer.setblocking(False)

    def _receive_exactly(self, size):
        data = bytearray()
        while len(data) < size:
            chunk = self.connection.recv(size - len(data))
            if not chunk:
                raise ConnectionError("The other player disconnected.")
            data.extend(chunk)
        return bytes(data)

    def start_input_transport(self):
        # Close can race a late setup worker. Never restart a closed connection
        # or join a Thread object before its start() has completed.
        with self._lifecycle_lock:
            if self._closed.is_set():
                raise ConnectionError("The LAN connection is closed.")
            if self._reader is not None:
                return
            self.connection.setblocking(False)
            self._transport_started = time.monotonic()
            self._reader = threading.Thread(
                target=self._network_loop,
                name="LAN input transport",
                daemon=True,
            )
            self._reader.start()

    @staticmethod
    def _decode_inputs(mask):
        return {action: bool(mask & (1 << index)) for index, action in enumerate(ACTIONS)}

    def _queue_packet(self, frame, mask):
        if self._closed.is_set():
            raise ConnectionError("The LAN connection is closed.")
        try:
            self._outgoing.put_nowait(INPUT_PACKET.pack(frame, mask))
        except queue.Full as error:
            raise ConnectionError("LAN send buffer is full; the connection cannot keep up.") from error
        self._signal_wake()

    def _signal_wake(self):
        try:
            self._wake_writer.send(b"\0")
        except BlockingIOError:
            # A full wake socket is already readable; inputs remain in the
            # bounded queue, so wake bytes may safely coalesce.
            pass
        except OSError:
            if not self._closed.is_set():
                raise ConnectionError("LAN transport wakeup failed.")

    def _drain_wake(self):
        while True:
            try:
                if not self._wake_reader.recv(4096):
                    return
            except BlockingIOError:
                return

    def submit_input(self, frame, values):
        """Send a tick once, without waiting for any remote input.

        An unchanged mask is still sent on every new tick: it confirms that tick
        exists. Omitting it without an explicit run length would be ambiguous.
        Retries of an identical tick are suppressed; changing its input is an error.
        """
        if not isinstance(frame, int) or not 0 <= frame < PONG_FRAME:
            raise ValueError("Invalid LAN input tick.")
        self.start_input_transport()
        if self._error is not None:
            raise self._error
        mask = sum(1 << index for index, action in enumerate(ACTIONS) if values.get(action, False))
        if frame in self._sent_frames:
            if self._sent_frames[frame] != mask:
                raise ValueError("Cannot change an already submitted LAN input tick.")
            return
        if frame <= self._highest_submitted - MAX_BUFFERED_INPUTS:
            raise ValueError("LAN input tick is older than the retained history.")
        self._queue_packet(frame, mask)
        self._sent_frames[frame] = mask
        self._highest_submitted = max(self._highest_submitted, frame)
        cutoff = self._highest_submitted - MAX_BUFFERED_INPUTS
        if len(self._sent_frames) > MAX_BUFFERED_INPUTS:
            self._sent_frames = {tick: value for tick, value in self._sent_frames.items() if tick > cutoff}
        with self._stats_lock:
            self._sent_times.append(time.monotonic())

    def receive_inputs(self):
        """Drain newly received actual input ticks; never wait for the peer."""
        self.start_input_transport()
        if self._error is not None:
            raise self._error
        result = {}
        while True:
            try:
                incoming = self._incoming.get_nowait()
            except queue.Empty:
                break
            if incoming is None:
                raise self._error or ConnectionError("The other player disconnected.")
            frame, mask = incoming
            result[frame] = self._decode_inputs(mask)
        last_input = self._last_received_input
        if time.monotonic() - (last_input if last_input is not None else self._transport_started) > INPUT_TIMEOUT:
            raise ConnectionError("The other player stopped responding. Check the LAN connection.")
        return result

    def get_stats(self):
        """Rates count six-byte input records, not TCP/IP segments or ping records.

        TCP hides loss and retransmission, so dropped_packets is unavailable,
        rather than incorrectly reporting zero. Ping uses echoed local timestamps.
        """
        now = time.monotonic()
        with self._stats_lock:
            for samples in (self._sent_times, self._received_times):
                while samples and samples[0] < now - 1.0:
                    samples.popleft()
            return {
                "ping_ms": self._ping_ms,
                "sent_rate": len(self._sent_times),
                "received_rate": len(self._received_times),
                "dropped_packets": None,
                "duplicates": self._duplicates,
                "late_packets": self._late_packets,
                "last_received_age": None if self._last_received_input is None else now - self._last_received_input,
            }

    def _process_packet(self, frame, mask):
        now = time.monotonic()
        if frame == PING_FRAME:
            self._queue_packet(PONG_FRAME, mask)
            return
        if frame == PONG_FRAME:
            with self._stats_lock:
                started = self._ping_started.pop(mask, None)
                if started is not None:
                    sample = max(0.0, (now - started) * 1000)
                    self._ping_ms = sample if self._ping_ms is None else self._ping_ms * 0.8 + sample * 0.2
            return
        if mask & ~((1 << len(ACTIONS)) - 1):
            raise ConnectionError("Received an invalid LAN input mask.")
        if frame > max(self._highest_submitted, 0) + MAX_FRAME_AHEAD:
            raise ConnectionError("LAN input tick is too far ahead to synchronize.")
        with self._stats_lock:
            self._received_times.append(now)
            self._last_received_input = now
            if frame in self._received_frames:
                if self._received_frames[frame] != mask:
                    raise ConnectionError("The other player changed a confirmed LAN input tick.")
                self._duplicates += 1
                return
            if frame <= self._highest_received - MAX_BUFFERED_INPUTS:
                self._late_packets += 1
                return
            if frame < self._highest_received:
                self._late_packets += 1
            self._highest_received = max(self._highest_received, frame)
            self._received_frames[frame] = mask
            cutoff = self._highest_received - MAX_BUFFERED_INPUTS
            if len(self._received_frames) > MAX_BUFFERED_INPUTS:
                self._received_frames = {tick: value for tick, value in self._received_frames.items() if tick > cutoff}
        try:
            self._incoming.put_nowait((frame, mask))
        except queue.Full as error:
            raise ConnectionError("LAN input fell too far behind to stay synchronized.") from error

    def _network_loop(self):
        pending_send = bytearray()
        pending_receive = bytearray()
        try:
            while not self._closed.is_set():
                now = time.monotonic()
                if self._last_ping_sent is None or now - self._last_ping_sent >= PING_INTERVAL:
                    self._ping_nonce = (self._ping_nonce + 1) & 0xFFFF
                    with self._stats_lock:
                        self._ping_started = {nonce: started for nonce, started in self._ping_started.items() if now - started < INPUT_TIMEOUT}
                        self._ping_started[self._ping_nonce] = now
                    pending_send.extend(INPUT_PACKET.pack(PING_FRAME, self._ping_nonce))
                    self._last_ping_sent = now
                while not self._closed.is_set() and len(pending_send) < MAX_BUFFERED_INPUTS * INPUT_PACKET.size:
                    try:
                        pending_send.extend(self._outgoing.get_nowait())
                    except queue.Empty:
                        break

                readable, writable, _ = select.select(
                    [self.connection, self._wake_reader],
                    [self.connection] if pending_send else [],
                    [],
                    max(0.0, self._last_ping_sent + PING_INTERVAL - time.monotonic()),
                )
                if self._wake_reader in readable:
                    self._drain_wake()
                if self.connection in readable:
                    try:
                        chunk = self.connection.recv(4096)
                    except BlockingIOError:
                        # Readiness is advisory on nonblocking sockets.
                        chunk = None
                    if chunk is not None:
                        if not chunk:
                            raise ConnectionError("The other player disconnected.")
                        pending_receive.extend(chunk)
                        while len(pending_receive) >= INPUT_PACKET.size:
                            frame_number, input_mask = INPUT_PACKET.unpack_from(pending_receive)
                            del pending_receive[:INPUT_PACKET.size]
                            self._process_packet(frame_number, input_mask)
                if writable:
                    try:
                        sent = self.connection.send(pending_send)
                        if not sent:
                            raise ConnectionError("The other player disconnected.")
                        del pending_send[:sent]
                    except BlockingIOError:
                        pass
        except (OSError, ConnectionError, ValueError) as error:
            if not self._closed.is_set():
                self._error = ConnectionError(str(error))
                try:
                    self._incoming.put_nowait(None)
                except queue.Full:
                    pass

    def exchange_setup(self, local_setup):
        payload = json.dumps(local_setup, separators=(",", ":")).encode("utf-8")
        if len(payload) > MAX_SETUP_SIZE:
            raise ValueError("LAN setup data is too large.")
        self.connection.sendall(struct.pack("!I", len(payload)) + payload)

        size = struct.unpack("!I", self._receive_exactly(4))[0]
        if size > MAX_SETUP_SIZE:
            raise ValueError("Received oversized LAN setup data.")
        try:
            remote_setup = json.loads(self._receive_exactly(size))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("Received invalid LAN setup data.") from error
        if not isinstance(remote_setup, dict):
            raise ValueError("LAN setup data must be a JSON object.")
        return remote_setup

    def send_setup(self, setup):
        payload = json.dumps(setup, separators=(",", ":")).encode("utf-8")
        if len(payload) > MAX_SETUP_SIZE:
            raise ValueError("LAN setup data is too large.")
        self.connection.sendall(struct.pack("!I", len(payload)) + payload)

    def receive_setup(self):
        size = struct.unpack("!I", self._receive_exactly(4))[0]
        if size > MAX_SETUP_SIZE:
            raise ValueError("Received oversized LAN setup data.")
        try:
            setup = json.loads(self._receive_exactly(size))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("Received invalid LAN setup data.") from error
        if not isinstance(setup, dict):
            raise ValueError("LAN setup data must be a JSON object.")
        return setup

    def poll_setup(self):
        """Receive complete setup packets without blocking the Pygame event loop."""
        if self._setup_started is None:
            self._setup_started = time.monotonic()
        if time.monotonic() - self._setup_started > 300:
            raise ConnectionError("Timed out waiting for the other player's selection.")
        readable, _, _ = select.select([self.connection], [], [], 0)
        if readable:
            # Read only this packet: the following bytes may be gameplay inputs.
            remaining = 4 - len(self._setup_buffer)
            if remaining <= 0:
                size = struct.unpack("!I", self._setup_buffer[:4])[0]
                if size > MAX_SETUP_SIZE:
                    raise ValueError("Received oversized LAN setup data.")
                remaining = 4 + size - len(self._setup_buffer)
            chunk = self.connection.recv(max(1, remaining))
            if not chunk:
                raise ConnectionError("The other player disconnected during setup.")
            self._setup_buffer.extend(chunk)
        if len(self._setup_buffer) < 4:
            return None
        size = struct.unpack("!I", self._setup_buffer[:4])[0]
        if size > MAX_SETUP_SIZE:
            raise ValueError("Received oversized LAN setup data.")
        if len(self._setup_buffer) < 4 + size:
            return None
        payload = bytes(self._setup_buffer[4:4 + size])
        del self._setup_buffer[:4 + size]
        self._setup_started = None
        try:
            setup = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("Received invalid LAN setup data.") from error
        if not isinstance(setup, dict):
            raise ValueError("LAN setup data must be a JSON object.")
        return setup

    def poll_inputs(self, local_inputs, wait_timeout=0.0):
        """Submit a frame and optionally wait within the caller's frame budget."""
        self.start_input_transport()
        if self._error is not None:
            raise self._error
        frame_number = self._next_frame
        if self._submitted_frame != frame_number:
            self.local_inputs = dict(local_inputs)
            self.submit_input(frame_number, local_inputs)
            self._submitted_frame = frame_number
            self._frame_started = time.monotonic()

        deadline = time.monotonic() + max(0.0, wait_timeout)
        while True:
            try:
                incoming = self._incoming.get_nowait()
            except queue.Empty:
                remaining = deadline - time.monotonic()
                if frame_number in self._pending_inputs or remaining <= 0:
                    break
                try:
                    incoming = self._incoming.get(timeout=remaining)
                except queue.Empty:
                    break
            if incoming is None:
                if self._error is not None:
                    raise self._error
                raise ConnectionError("The other player disconnected.")
            received_frame, received_mask = incoming
            if received_frame >= frame_number:
                self._pending_inputs[received_frame] = received_mask

        remote_mask = self._pending_inputs.pop(frame_number, None)
        if remote_mask is None:
            if self._error is not None:
                raise self._error
            if time.monotonic() - self._frame_started > INPUT_TIMEOUT:
                raise ConnectionError("The other player stopped responding. Check the LAN connection.")
            return None

        self._next_frame += 1
        self._submitted_frame = None
        return self._decode_inputs(remote_mask)

    def close(self):
        with self._lifecycle_lock:
            self._closed.set()
            self._signal_wake()
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.connection.close()
        if (
            self._reader is not None
            and threading.current_thread() is not self._reader
        ):
            self._reader.join(timeout=1)
        with self._lifecycle_lock:
            self._wake_reader.close()
            self._wake_writer.close()


def create_host(port=PORT):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Windows SO_REUSEADDR can let two hosts bind the same port.
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("0.0.0.0", port))
        listener.listen(1)
        listener.setblocking(False)
    except OSError:
        listener.close()
        raise
    return listener


def accept_if_ready(listener):
    try:
        connection, address = listener.accept()
    except BlockingIOError:
        return None
    return LanPeer(connection, address)


def parse_address(address, default_port=PORT):
    """Accept the host's displayed IPv4 address with an optional :port."""
    host, separator, port_text = address.strip().partition(":")
    try:
        socket.inet_pton(socket.AF_INET, host)
        port = int(port_text) if separator else default_port
        if not 1 <= port <= 65535:
            raise ValueError
    except (OSError, ValueError) as error:
        raise ValueError("Enter a valid IPv4 address, optionally followed by :port.") from error
    return host, port


def connect_to_host(ip_address, port=PORT):
    ip_address, port = parse_address(ip_address, port)
    connection = socket.create_connection((ip_address, port), timeout=5)
    return LanPeer(connection, (ip_address, port))


def local_ip_address():
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 9))
        return probe.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"
    finally:
        probe.close()
