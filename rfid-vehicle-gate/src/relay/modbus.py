import logging
from config.settings import RELAY_CONFIG
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class ModbusRelay:
    def __init__(self):
        self.host = RELAY_CONFIG['host']
        self.port = RELAY_CONFIG['port']
        self.unit_id = RELAY_CONFIG['unit_id']
        self._client: ModbusTcpClient | None = None

    def _get_client(self) -> ModbusTcpClient:
        if self._client is None or not self._client.connected:
            self._client = ModbusTcpClient(self.host, port=self.port, timeout=3.0)
        return self._client

    def _ensure_connected(self) -> bool:
        client = self._get_client()
        if not client.connected:
            return client.connect()
        return True

    def open_channel(self, channel: int):
        """
        Membuka channel relay dengan error handling koneksi Modbus TCP.
        """
        client = self._get_client()
        try:
            if not self._ensure_connected():
                raise ConnectionError(f"Failed to connect to Modbus TCP server at {self.host}:{self.port}")

            address = channel - 1
            result = client.write_coil(address, True, slave=self.unit_id)

            if result.isError():
                raise ModbusException(f"Modbus response error writing coil channel {channel}")

            logger.info(f"[Modbus] Successfully opened (ON) Relay Channel {channel}")

        except (ConnectionException, ConnectionError, TimeoutError) as conn_err:
            logger.error(f"[Modbus Error] Connection to Waveshare Relay ({self.host}) lost/timeout: {conn_err}")
            self._client = None
            raise
        except Exception as e:
            logger.error(f"[Modbus Error] Unexpected error opening channel {channel}: {e}")
            raise

    def close_channel(self, channel: int):
        """
        Menutup channel relay dengan error handling yang aman.
        """
        client = self._get_client()
        try:
            if not self._ensure_connected():
                raise ConnectionError(f"Failed to connect to Modbus TCP server at {self.host}:{self.port}")

            address = channel - 1
            result = client.write_coil(address, False, slave=self.unit_id)

            if result.isError():
                raise ModbusException(f"Modbus response error turning off coil channel {channel}")

            logger.info(f"[Modbus] Successfully closed (OFF) Relay Channel {channel}")

        except Exception as e:
            logger.warning(f"[Modbus Warning] Failed to close channel {channel} (possible cable disconnect): {e}")
            self._client = None

    def close(self):
        """Explicitly close the Modbus connection."""
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None