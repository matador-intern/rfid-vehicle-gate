import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import DB_CONFIG

class VehicleRepository:
    def __init__(self):
        self.config = DB_CONFIG

    def get_connection(self):
        return psycopg2.connect(**self.config)

    def find_by_rfid(self, rfid: str):
        query = """
            SELECT id, rfid, plate_number, owner_name, gate_id, is_active
            FROM vehicle
            WHERE rfid = %s AND is_active = TRUE;
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (rfid,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"[ERROR DB] Error query find_by_rfid: {e}")
            return None
        finally:
            if conn:
                conn.close()
