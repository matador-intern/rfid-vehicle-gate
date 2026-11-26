import logging
from src.rfid.parser import normalize_rfid
from src.database.vehicle_repository import VehicleRepository
from src.database.vehicle_log_repository import VehicleLogRepository
from src.rfid.publisher import MqttPublisher

logger = logging.getLogger(__name__)


class RfidService:
    def __init__(self, vehicle_repo=None, log_repo=None, publisher=None):
        self.vehicle_repo = vehicle_repo or VehicleRepository()
        self.log_repo = log_repo or VehicleLogRepository()
        self.publisher = publisher or MqttPublisher()

    def handle_rfid(self, rfid_raw: str, gate_id: int) -> bool:
        # 1. Normalisasi UID
        rfid_clean = normalize_rfid(rfid_raw) if callable(normalize_rfid) else rfid_raw.strip().upper()

        if not rfid_clean:
            logger.warning(f"[RFID Service] Empty RFID after normalization: {rfid_raw}")
            return False

        # 2. Lookup Database
        try:
            vehicle = self.vehicle_repo.find_by_rfid(rfid_clean)
        except Exception as e:
            logger.error(f"[RFID Service] Database error during vehicle lookup: {e}")
            return False

        # JIKA KARTU ASING / TIDAK TERDAFTAR
        if not vehicle:
            logger.warning(f"[RFID Service] Unknown/Unregistered card: {rfid_clean}")
            return False

        logger.info(f"[RFID Service] Authorized: {vehicle.get('owner_name')} | Vehicle ID: {vehicle.get('id')}")

        # 3. Simpan ke Database vehicle_logs
        try:
            log_id = self.log_repo.insert(
                vehicle_id=vehicle['id'],
                rfid=rfid_clean,
                gate_id=gate_id
            )
            if log_id:
                logger.info(f"[RFID Service] Log saved (ID: {log_id})")
            else:
                logger.error(f"[RFID Service] Failed to save log for vehicle {vehicle['id']}")
                return False
        except Exception as e:
            logger.error(f"[RFID Service] Database error during log insert: {e}")
            return False

        # 4. Kirim Sinyal MQTT ke Subscriber
        try:
            success_pub = self.publisher.publish_vehicle_registered(
                vehicle_id=vehicle['id'],
                rfid=rfid_clean,
                gate_id=gate_id
            )
            if not success_pub:
                logger.error(f"[RFID Service] MQTT publish failed for vehicle {vehicle['id']}")
                return False
        except Exception as e:
            logger.error(f"[RFID Service] MQTT publish error: {e}")
            return False

        return True