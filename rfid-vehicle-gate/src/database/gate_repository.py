import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load variabel dari file .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class GateRepository:
    def __init__(self):
        # Kredensial default disesuaikan dengan database dummy
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.dbname = os.getenv("DB_NAME", "rfid_vehicle_gate")
        self.user = os.getenv("DB_USER", "magang")
        self.password = os.getenv("DB_PASSWORD", "rfid_123")

    def _get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )

    def find_by_id(self, gate_id: int) -> dict:
        """
        Mencari data gate berdasarkan gate_id dari tabel 'gate'.
        Mengembalikan dict yang berisi 'id', 'name', dan 'channel'.
        """
        # Mengubah 'gates' menjadi 'gate' (tunggal)
        query = "SELECT id, name, channel FROM gate WHERE id = %s;"

        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (gate_id,))
                result = cur.fetchone()

                if not result:
                    raise ValueError(f"Gate dengan ID {gate_id} tidak ditemukan di database.")

                return dict(result)


# BLOK PENGUJIAN DATABASE (TASK M2-3)
if __name__ == "__main__":
    print("\n=== UJI DATABASE TASK M2-3 (GATE REPOSITORY LOOKUP) ===")
    repo = GateRepository()
    test_gate_id = 1

    try:
        print(f"Menghubungkan ke database '{repo.dbname}' ({repo.host}:{repo.port})...")
        print(f"1. Melakukan query ke PostgreSQL untuk gate_id = {test_gate_id}...")
        gate_data = repo.find_by_id(test_gate_id)

        print(f"   -> Data Ditemukan : {gate_data}")
        print(f"   -> Gate ID       : {gate_data.get('id')}")
        print(f"   -> Gate Name     : {gate_data.get('name')}")
        print(f"   -> Relay Channel : {gate_data.get('channel')}")

        print("\n=== PENGUJIAN M2-3 SELESAI & BERHASIL ===")

    except Exception as e:
        logger.error(f"Gagal mengambil data dari PostgreSQL: {e}", exc_info=True)
