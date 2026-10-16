import logging
import os
from dotenv import load_dotenv
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class ModbusRelay:
    def __init__(self):
        self.host = os.getenv("WAVESHARE_RELAY_HOST", "192.168.10.20")
        self.port = int(os.getenv("WAVESHARE_RELAY_PORT", 502))
        self.unit_id = int(os.getenv("WAVESHARE_RELAY_UNIT_ID", 1))

    def _get_client(self) -> ModbusTcpClient:
        return ModbusTcpClient(self.host, port=self.port, timeout=3.0)

    def open_channel(self, channel: int):
        """
        Membuka channel relay dengan error handling koneksi Modbus TCP.
        """
        client = self._get_client()
        try:
            if not client.connect():
                raise ConnectionError(f"Gagal terhubung ke Modbus TCP server di {self.host}:{self.port}")

            address = channel - 1  # Pemetaan register coil Waveshare mulai dari 0
            result = client.write_coil(address, True, slave=self.unit_id)
            
            if result.isError():
                raise ModbusException(f"Modbus response error saat menulis coil channel {channel}")
            
            logger.info(f"[Modbus] Berhasil membuka (ON) Relay Channel {channel}")

        except (ConnectionException, ConnectionError, TimeoutError) as conn_err:
            logger.error(f"[Modbus Error] Koneksi ke Waveshare Relay ({self.host}) terputus/timeout: {conn_err}")
            raise
        except Exception as e:
            logger.error(f"[Modbus Error] Kesalahan tak terduga saat membuka channel {channel}: {e}")
            raise
        finally:
            try:
                client.close()
            except Exception:
                pass

    def close_channel(self, channel: int):
        """
        Menutup channel relay dengan error handling yang aman (tidak melempar fatal error di blok finally).
        """
        client = self._get_client()
        try:
            if not client.connect():
                raise ConnectionError(f"Gagal terhubung ke Modbus TCP server di {self.host}:{self.port}")

            address = channel - 1
            result = client.write_coil(address, False, slave=self.unit_id)
            
            if result.isError():
                raise ModbusException(f"Modbus response error saat mematikan coil channel {channel}")
            
            logger.info(f"[Modbus] Berhasil menutup (OFF) Relay Channel {channel}")

        except Exception as e:
            logger.warning(f"[Modbus Warning] Gagal menutup channel {channel} (kemungkinan kabel terputus): {e}")
            # Tidak di-raise ulang agar blok finally di controller tidak terganggu fatal
