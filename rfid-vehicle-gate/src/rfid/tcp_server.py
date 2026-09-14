import logging
import os
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
    ):
        self.host = host or os.getenv("RFID_READER_IP") or os.getenv("RFID_READER_HOST", "192.168.10.10")
        self.port = port or int(os.getenv("RFID_READER_PORT", "6000"))
        self.packet_callback = packet_callback
        self.reconnect_delay_sec = reconnect_delay_sec
        self.recv_size = recv_size
        self.auto_inventory = auto_inventory

        self.running = False
        self._socket: Optional[socket.socket] = None
        self._buffer = bytearray()

    def start(self) -> None:
        self.running = True
        logger.info("RFID TCP client mulai ke %s:%s", self.host, self.port)
        while self.running:
            try:
                self._connect()
                self._recv_loop()
            except Exception as exc:
                logger.warning("Koneksi reader terputus: %s", exc)
            finally:
                self._close_socket()

            if self.running:
                logger.info("Reconnect dalam %.1fs...", self.reconnect_delay_sec)
                time.sleep(self.reconnect_delay_sec)

    def stop(self) -> None:
        self.running = False
        self._close_socket()
        logger.info("RFID TCP client dihentikan.")

    def _connect(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        sock.settimeout(5.0)
        sock.connect((self.host, self.port))
        self._socket = sock
        self._buffer.clear()

        logger.info("Terhubung ke RFID reader %s:%s", self.host, self.port)

    def _send_inventory_command(self) -> None:
        # Perintah scan inventory standar HW-VX6330K
        cmd = bytes.fromhex("040001db4b")
        try:
            if self._socket:
                self._socket.sendall(cmd)
        except Exception:
            pass

    def _close_socket(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None

    def _recv_loop(self) -> None:
        assert self._socket is not None
        while self.running:
            # Kirim pancingan scan terus-menerus jika auto_inventory True
            if self.auto_inventory:
                self._send_inventory_command()
                time.sleep(1.0)

            data = self._socket.recv(self.recv_size)
            if not data:
                raise ConnectionError("Reader menutup koneksi (recv kosong)")

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
                    logger.error("Error pada packet_callback: %s", exc)
