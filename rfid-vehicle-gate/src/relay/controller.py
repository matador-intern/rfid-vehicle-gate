import logging
import os
import time
from dotenv import load_dotenv

from src.database.gate_repository import GateRepository
from src.relay.modbus import ModbusRelay

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("RelayController")


class RelayController:
    def __init__(self, gate_repo: GateRepository = None, modbus_relay: ModbusRelay = None):
        self.gate_repo = gate_repo or GateRepository()
        self.modbus_relay = modbus_relay or ModbusRelay()
        self.pulse_duration = float(os.getenv("RELAY_ON_DURATION_SECONDS", "3.0"))

    def trigger_gate_pulse(self, gate_id: int, duration: float = None):
        """
        Memicu gate dengan penanganan error koneksi Modbus (Task M2-7).
        Jika kabel dicabut, error dicatat di log dan tidak membuat service crash.
        """
        gate_info = self.gate_repo.find_by_id(gate_id)
        channel = gate_info.get("channel")

        if channel is None:
            raise ValueError(f"Gate ID {gate_id} tidak memiliki pemetaan channel relay yang valid.")

        gate_name = gate_info.get("name", f"Gate-{gate_id}")
        hold_time = duration if duration is not None else self.pulse_duration

        logger.info(f"[Controller] Triggering Gate {gate_id} ('{gate_name}') pada Relay Channel {channel}")

        try:
            logger.info(f"[Controller] Turning ON Relay Channel {channel}")
            self.modbus_relay.open_channel(channel)

            logger.info(f"[Controller] Waiting for {hold_time} seconds...")
            time.sleep(hold_time)

        except (ConnectionError, TimeoutError) as net_err:
            logger.error(f"[Controller] ❌ Gagal terhubung ke hardware relay (Kabel tercabut/Network down): {net_err}")
            # Service dibiarkan lanjut/tidak crash, hanya mencatat error log

        except Exception as e:
            logger.error(f"[Controller] ❌ Error saat eksekusi pulse relay: {e}")

        finally:
            logger.info(f"[Controller] Safety Guard: Attempting to turn OFF Relay Channel {channel}")
            try:
                self.modbus_relay.close_channel(channel)
            except Exception as close_err:
                logger.warning(f"[Controller] Safety guard gagal mematikan relay (diabaikan agar service aman): {close_err}")
