import logging
import sys
from config.settings import MQTT_CONFIG

from src.relay.subscriber import VehicleRegisteredSubscriber

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("RelayService")


class RelayService:
    """
    Orkestrasi end-to-end untuk Relay Subsystem.
    Menggabungkan fungsionalitas MQTT listener, kontrol relay Modbus TCP,
    dan pencatatan log ke database PostgreSQL.
    """
    def __init__(self):
        logger.info("[RelayService] Initializing Relay Subsystem components...")
        self.subscriber = VehicleRegisteredSubscriber()

    def run(self):
        """
        Menjalankan service secara kontinu (blocking loop) untuk 
        memproses event kendaraan masuk secara end-to-end.
        """
        logger.info("[RelayService] Starting Relay Service (End-to-End)...")
        try:
            self.subscriber.start()
        except KeyboardInterrupt:
            logger.info("[RelayService] Relay Service stopped by user (Ctrl+C).")
        except Exception as e:
            logger.critical(f"[RelayService] Fatal error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    print("\n========================================================")
    print("=== RELAY SERVICE - END-TO-END ORCHESTRATION ===")
    print("========================================================\n")
    
    service = RelayService()
    service.run()