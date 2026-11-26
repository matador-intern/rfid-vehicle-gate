import logging
from config.settings import DB_CONFIG
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class GateRepository:
    def __init__(self):
        self.config = DB_CONFIG

    def _get_connection(self):
        return psycopg2.connect(**self.config)

    def find_by_id(self, gate_id: int) -> dict:
        """
        Mencari data gate berdasarkan gate_id.
        Mengembalikan dict yang berisi 'id', 'name', dan 'channel'.
        """
        # Sesuaikan nama tabel ('gate' atau 'gates') dengan skema PostgreSQL kamu
        query = "SELECT id, name, channel FROM gate WHERE id = %s;"

        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (gate_id,))
                result = cur.fetchone()

                if not result:
                    raise ValueError(f"Gate dengan ID {gate_id} tidak ditemukan di database.")

                return dict(result)


if __name__ == "__main__":
    print("\n=== DATABASE TEST: GATE REPOSITORY LOOKUP ===")
    repo = GateRepository()
    test_gate_id = 1

    try:
        print(f"Connecting to database '{repo.config['dbname']}' ({repo.config['host']}:{repo.config['port']})...")
        print(f"Querying PostgreSQL for gate_id = {test_gate_id}...")
        gate_data = repo.find_by_id(test_gate_id)

        print(f"   -> Data Found    : {gate_data}")
        print(f"   -> Gate ID       : {gate_data.get('id')}")
        print(f"   -> Gate Name     : {gate_data.get('name')}")
        print(f"   -> Relay Channel : {gate_data.get('channel')}")

        print("\n=== TEST COMPLETED SUCCESSFULLY ===")

    except Exception as e:
        logger.error(f"Failed to fetch data from PostgreSQL: {e}", exc_info=True)