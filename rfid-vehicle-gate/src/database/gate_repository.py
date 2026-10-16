import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logger = logging.getLogger(__name__)


class GateRepository:
    def __init__(self, db_url: str = None):
        # Mengambil koneksi database dari environment variable .env
        self.db_url = db_url or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/rfid_db"
        )

    def find_by_id(self, gate_id: int) -> dict:
        """
        Mencari data gate berdasarkan gate_id.
        Mengembalikan dict yang berisi 'id', 'name', dan 'channel'.
        """
        query = "SELECT id, name, channel FROM gates WHERE id = %s;"

        with psycopg2.connect(self.db_url) as conn:
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
        print(f"\n1. Melakukan query ke PostgreSQL untuk gate_id = {test_gate_id}...")
        gate_data = repo.find_by_id(test_gate_id)
        
        print(f"   -> Data Ditemukan : {gate_data}")
        print(f"   -> Gate ID       : {gate_data.get('id')}")
        print(f"   -> Gate Name     : {gate_data.get('name')}")
        print(f"   -> Relay Channel : {gate_data.get('channel')}")

        print("\n=== PENGUJIAN M2-3 SELESAI & BERHASIL ===")

    except Exception as e:
        logger.error(f"Gagal mengambil data dari PostgreSQL: {e}", exc_info=True)
