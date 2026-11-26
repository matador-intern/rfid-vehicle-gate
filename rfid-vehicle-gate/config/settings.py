import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': os.getenv('DB_NAME', 'rfid_vehicle_gate'),
    'user': os.getenv('DB_USER', 'magang'),
    'password': os.getenv('DB_PASSWORD', 'rfid_123')
}

MQTT_CONFIG = {
    'host': os.getenv('MQTT_HOST', 'localhost'),
    'port': int(os.getenv('MQTT_PORT', '1883')),
    'username': os.getenv('MQTT_USER', None),
    'password': os.getenv('MQTT_PASSWORD', None),
    'client_id': os.getenv('MQTT_CLIENT_ID', 'rfid-publisher'),
    'topic_vehicle_registered': os.getenv('MQTT_TOPIC_VEHICLE_REGISTERED', 'vehicle/registered')
}

RFID_READER_CONFIG = {
    'host': os.getenv('RFID_READER_IP') or os.getenv('RFID_READER_HOST', '192.168.10.10'),
    'port': int(os.getenv('RFID_READER_PORT', '6000')),
    'auto_inventory': os.getenv('RFID_AUTO_INVENTORY', 'true').lower() == 'true',
    'inventory_interval_sec': float(os.getenv('RFID_INVENTORY_INTERVAL', '1.0'))
}

RELAY_CONFIG = {
    'host': os.getenv('WAVESHARE_RELAY_HOST', '192.168.10.20'),
    'port': int(os.getenv('WAVESHARE_RELAY_PORT', '502')),
    'unit_id': int(os.getenv('WAVESHARE_RELAY_UNIT_ID', '1')),
    'pulse_duration_sec': float(os.getenv('RELAY_ON_DURATION_SECONDS', '3.0'))
}

GATE_CONFIG = {
    'default_gate_id': int(os.getenv('GATE_ID', '1'))
}