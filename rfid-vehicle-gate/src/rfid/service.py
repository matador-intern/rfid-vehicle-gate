from src.rfid.parser import normalize_rfid
from src.database.vehicle_repository import VehicleRepository
from src.database.vehicle_log_repository import VehicleLogRepository
from src.rfid.publisher import MqttPublisher

class RfidService:
    def __init__(self, vehicle_repo=None, log_repo=None, publisher=None):
        self.vehicle_repo = vehicle_repo or VehicleRepository()
        self.log_repo = log_repo or VehicleLogRepository()
        self.publisher = publisher or MqttPublisher()

    def handle_rfid(self, rfid_raw: str, gate_id: int):
        # 1. Normalisasi UID
        rfid_clean = normalize_rfid(rfid_raw) if callable(normalize_rfid) else rfid_raw.strip().upper()

        # 2. Lookup Database
        vehicle = self.vehicle_repo.find_by_rfid(rfid_clean)

        # JIKA KARTU ASING / TIDAK TERDAFTAR
        if not vehicle:
            print(f"[WARNING] Kartu Asing / Tidak Terdaftar! RFID: {rfid_clean}")
            return False

        print(f"[TERDAFTAR] Owner: {vehicle.get('owner_name')} | Vehicle ID: {vehicle.get('id')}")

        # 3. Simpan ke Database vehicle_logs
        log_id = self.log_repo.insert(
            vehicle_id=vehicle['id'],
            rfid=rfid_clean,
            gate_id=gate_id
        )
        print(f"[DB LOG SUCCESS] Log ID: {log_id}")

        # 4. Kirim Sinyal MQTT ke Subscriber
        success_pub = self.publisher.publish_vehicle_registered(
            vehicle_id=vehicle['id'],
            rfid=rfid_clean,
            gate_id=gate_id
        )

        return success_pub
