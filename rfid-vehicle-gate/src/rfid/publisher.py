import json
from datetime import datetime
import paho.mqtt.client as mqtt
from config.settings import DB_CONFIG

class MqttPublisher:
    def __init__(self, host="localhost", port=1883):
        self.host = host
        self.port = int(port)
        self.topic = "vehicle/registered"

    def publish_vehicle_registered(self, vehicle_id: int, rfid: str, gate_id: int):
        payload = {
            "vehicle_id": vehicle_id,
            "rfid": rfid.upper().strip(),
            "gate_id": gate_id,
            "timestamp": datetime.now().isoformat()
        }

        try:
            client = mqtt.Client(client_id="MQTT_CLIENT_ID_RFID")
            client.connect(self.host, self.port, 60)
            client.publish(self.topic, json.dumps(payload), qos=1, retain=False)
            client.disconnect()
            print(f"[MQTT SUCCESS] Published to '{self.topic}': {payload}")
            return True
        except Exception as e:
            print(f"[MQTT ERROR] Failed to publish message: {e}")
            return False
