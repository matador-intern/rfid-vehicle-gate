import logging
import sys
from dotenv import load_dotenv

from src.relay.subscriber import RelaySubscriber

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("RelayService")


class RelayService:
    """
    [Task M2-8] Orkestrasi end-to-end untuk Relay Subsystem.
    Menggabungkan fungsionalitas MQTT listener, kontrol relay Modbus TCP,
    dan pencatatan log ke database PostgreSQL.
    """
    def __init__(self):
        logger.info("[RelayService] Menginisialisasi komponen Relay Subsystem...")
        # Menggunakan RelaySubscriber yang sudah mencakup Controller & Log Repository
        self.subscriber = RelaySubscriber()

    def run(self):
        """
        Menjalankan service secara kontinu (blocking loop) untuk 
        memproses event kendaraan masuk secara end-to-end.
        """
        logger.info("[RelayService] 🚀 Memulai Relay Service (End-to-End)...")
        try:
            self.subscriber.start()
        except KeyboardInterrupt:
            logger.info("[RelayService] 🛑 Relay Service dihentikan manual oleh pengguna (Ctrl+C).")
        except Exception as e:
            logger.critical(f"[RelayService] 🚨 Service mengalami error fatal: {e}")
            sys.exit(1)


# Blok eksekusi utama jika dijalankan langsung
if __name__ == "__main__":
    print("\n========================================================")
    print("=== M2-8: ORKESTRASI RELAY SERVICE.RUN (END-TO-END) ===")
    print("========================================================\n")
    
    service = RelayService()
    service.run()
