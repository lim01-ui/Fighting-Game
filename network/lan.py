"""Small lockstep TCP transport for two-player LAN matches."""

import json
import queue
import select
import socket
import struct
import threading
import time


PORT = 47611
# Increment when combat rules change: lockstep peers must simulate identical rules.
PROTOCOL_VERSION = 6
MAX_SETUP_SIZE = 4096
INPUT_TIMEOUT = 15.0
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
        self._incoming = queue.Queue(maxsize=300)
        self._outgoing = queue.Queue()
        self._pending_inputs = {}
        self._next_frame = 0
        self._submitted_frame = None
        self._error = None
        self._closed = threading.Event()
        self._reader = None
        self.local_inputs = {}
        self._frame_started = None
        self._setup_buffer = bytearray()
        self._setup_started = None

    def _receive_exactly(self, size):
        data = bytearray()
        while len(data) < size:
            chunk = self.connection.recv(size - len(data))
            if not chunk:
                raise ConnectionError("The other player disconnected.")
            data.extend(chunk)
        return bytes(data)

    def start_input_transport(self):
        if self._reader is not None:
            return
        self.connection.setblocking(False)
        self._reader = threading.Thread(
            target=self._network_loop,
            name="LAN input transport",
            daemon=True,
        )
        self._reader.start()

    def _network_loop(self):
        pending_send = bytearray()
        pending_receive = bytearray()
        try:
            while not self._closed.is_set():
                while not self._closed.is_set():
                    try:
                        pending_send.extend(self._outgoing.get_nowait())
                    except queue.Empty:
                        break

                readable, writable, _ = select.select(
                    [self.connection],
                    [self.connection] if pending_send else [],
                    [],
                    0.005,
                )
                if readable:
                    chunk = self.connection.recv(4096)
                    if not chunk:
                        raise ConnectionError("The other player disconnected.")
                    pending_receive.extend(chunk)
                    while len(pending_receive) >= 6:
                        packet = bytes(pending_receive[:6])
                        del pending_receive[:6]
                        frame_number, input_mask = struct.unpack("!IH", packet)
                        try:
                            self._incoming.put_nowait((frame_number, input_mask))
                        except queue.Full as error:
                            raise ConnectionError(
                                "LAN input fell too far behind to stay synchronized."
                            ) from error
                if writable:
                    sent = self.connection.send(pending_send)
                    del pending_send[:sent]
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
        mask = sum(
            (1 << index)
            for index, action in enumerate(ACTIONS)
            if local_inputs.get(action, False)
        )
        if self._submitted_frame != frame_number:
            self.local_inputs = dict(local_inputs)
            self._outgoing.put(struct.pack("!IH", frame_number, mask))
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
        return {
            action: bool(remote_mask & (1 << index))
            for index, action in enumerate(ACTIONS)
        }

    def close(self):
        self._closed.set()
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
