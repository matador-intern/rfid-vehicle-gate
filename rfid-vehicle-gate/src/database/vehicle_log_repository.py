import psycopg2
from config.settings import DB_CONFIG

class VehicleLogRepository:
    def __init__(self):
        self.config = DB_CONFIG

    def get_connection(self):
        return psycopg2.connect(**self.config)

    def insert(self, vehicle_id: int, rfid: str, gate_id: int):
        query = """
            INSERT INTO vehicle_logs (vehicle_id, rfid, gate_id)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (vehicle_id, rfid, gate_id))
                log_id = cursor.fetchone()[0]
                conn.commit()
                return log_id
        except Exception as e:
            print(f"[ERROR DB] Error insert vehicle_logs: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
