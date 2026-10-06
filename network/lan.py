"""Small lockstep TCP transport for two-player LAN matches."""

import json
import queue
import select
import socket
import struct
import threading


PORT = 47611
PROTOCOL_VERSION = 3
MAX_SETUP_SIZE = 4096
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
        self._incoming = queue.Queue(maxsize=120)
        self._outgoing = queue.Queue()
        self._pending_inputs = {}
        self._next_frame = 0
        self._submitted_frame = None
        self._error = None
        self._closed = threading.Event()
        self._reader = None

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
                if not pending_send:
                    try:
                        pending_send.extend(self._outgoing.get_nowait())
                    except queue.Empty:
                        pass

                readable, writable, _ = select.select(
                    [self.connection],
                    [self.connection] if pending_send else [],
                    [],
                    0.1,
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

    def poll_inputs(self, local_inputs):
        """Submit this simulation frame without blocking and poll its peer input."""
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
            self._outgoing.put(struct.pack("!IH", frame_number, mask))
            self._submitted_frame = frame_number

        while True:
            try:
                incoming = self._incoming.get_nowait()
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
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("0.0.0.0", port))
    listener.listen(1)
    listener.setblocking(False)
    return listener


def accept_if_ready(listener):
    try:
        connection, address = listener.accept()
    except BlockingIOError:
        return None
    return LanPeer(connection, address)


def connect_to_host(ip_address, port=PORT):
    connection = socket.create_connection((ip_address, port), timeout=5)
    return LanPeer(connection, (ip_address, port))


def local_ip_address():
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 9))
        return probe.getsockname()[0]
    finally:
        probe.close()
