import logging
import socket
import time
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class RfidTcpClient:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        packet_callback: Optional[Callable[[bytes], None]] = None,
        reconnect_delay_sec: float = 2.0,
        recv_size: int = 1024,
        auto_inventory: bool = True,
        inventory_interval_sec: float = 1.0,
    ):
        self.host = host or "192.168.10.10"
        self.port = port or 6000
        self.packet_callback = packet_callback
        self.reconnect_delay_sec = reconnect_delay_sec
        self.recv_size = recv_size
        self.auto_inventory = auto_inventory
        self.inventory_interval_sec = inventory_interval_sec

        self.running = False
        self._socket: Optional[socket.socket] = None
        self._buffer = bytearray()
        self._last_inventory_time = 0.0

    def start(self) -> None:
        self.running = True
        logger.info("RFID TCP client starting: %s:%s", self.host, self.port)
        while self.running:
            try:
                self._connect()
                self._recv_loop()
            except Exception as exc:
                logger.warning("Reader connection lost: %s", exc)
            finally:
                self._close_socket()

            if self.running:
                logger.info("Reconnecting in %.1fs...", self.reconnect_delay_sec)
                time.sleep(self.reconnect_delay_sec)

    def stop(self) -> None:
        self.running = False
        self._close_socket()
        logger.info("RFID TCP client stopped.")

    def _connect(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        sock.settimeout(5.0)
        sock.connect((self.host, self.port))
        self._socket = sock
        self._buffer.clear()
        self._last_inventory_time = 0.0

        logger.info("Connected to RFID reader %s:%s", self.host, self.port)

    def _send_inventory_command(self) -> bool:
        if not self._socket:
            return False

        current_time = time.time()
        if current_time - self._last_inventory_time < self.inventory_interval_sec:
            return False

        cmd = bytes.fromhex("040001db4b")
        try:
            self._socket.sendall(cmd)
            self._last_inventory_time = current_time
            logger.debug("Inventory command sent")
            return True
        except Exception as exc:
            logger.warning("Failed to send inventory command: %s", exc)
            return False

    def _close_socket(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None

    def _recv_loop(self) -> None:
        assert self._socket is not None
        self._socket.settimeout(1.0)

        while self.running:
            if self.auto_inventory:
                self._send_inventory_command()

            try:
                data = self._socket.recv(self.recv_size)
            except socket.timeout:
                continue
            except Exception as exc:
                raise ConnectionError(f"Socket error: {exc}")

            if not data:
                raise ConnectionError("Reader closed connection (empty recv)")

            self._buffer.extend(data)
            self._extract_packets()

    def _extract_packets(self) -> None:
        while True:
            if not self._buffer:
                return
            packet_length = self._buffer[0]
            total_size = 1 + packet_length
            if len(self._buffer) < total_size:
                return
            packet = bytes(self._buffer[:total_size])
            del self._buffer[:total_size]
            if self.packet_callback:
                try:
                    self.packet_callback(packet)
                except Exception as exc:
                    logger.error("Packet callback error: %s", exc)