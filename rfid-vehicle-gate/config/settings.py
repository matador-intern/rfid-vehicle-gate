import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': os.getenv('DB_NAME', 'rfid_vehicle_gate'),
    'user': os.getenv('DB_USER', 'magang'),
    'password': os.getenv('DB_PASSWORD', 'rfid_123')
}
