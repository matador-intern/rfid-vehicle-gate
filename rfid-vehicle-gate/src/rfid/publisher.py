import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from config.settings import MQTT_CONFIG

logger = logging.getLogger(__name__)


class MqttPublisher:
    def __init__(self, host=None, port=None, username=None, password=None, client_id=None):
        self.host = host or MQTT_CONFIG["host"]
        self.port = port or MQTT_CONFIG["port"]
        self.username = username or MQTT_CONFIG.get("username")
        self.password = password or MQTT_CONFIG.get("password")
        self.client_id = client_id or MQTT_CONFIG.get("client_id", "rfid-publisher")
        self.topic = MQTT_CONFIG.get("topic_vehicle_registered", "vehicle/registered")

        self._client = mqtt.Client(
            client_id=self.client_id,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        if self.username and self.password:
            self._client.username_pw_set(self.username, self.password)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish

        self._connected = False
        self._connect()

    def _connect(self):
        try:
            self._client.connect(self.host, self.port, keepalive=60)
            self._client.loop_start()
            logger.info(f"[MQTT Publisher] Connecting to {self.host}:{self.port}...")
        except Exception as e:
            logger.error(f"[MQTT Publisher] Connection failed: {e}")
            raise

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self._connected = True
            logger.info(f"[MQTT Publisher] Connected to broker (rc={rc})")
        else:
            logger.error(f"[MQTT Publisher] Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self._connected = False
        if rc != 0:
            logger.warning(f"[MQTT Publisher] Unexpected disconnect (rc={rc}), will auto-reconnect")

    def _on_publish(self, client, userdata, mid, reason_code=None, properties=None):
        logger.debug(f"[MQTT Publisher] Message published (mid={mid})")

    def publish_vehicle_registered(self, vehicle_id: int, rfid: str, gate_id: int) -> bool:
        if not self._connected:
            logger.warning("[MQTT Publisher] Not connected, attempting to reconnect...")
            try:
                self._client.reconnect()
            except Exception as e:
                logger.error(f"[MQTT Publisher] Reconnect failed: {e}")
                return False

        payload = {
            "vehicle_id": vehicle_id,
            "rfid": rfid.upper().strip(),
            "gate_id": gate_id,
            "timestamp": datetime.now().isoformat()
        }

        try:
            result = self._client.publish(self.topic, json.dumps(payload), qos=1, retain=False)
            result.wait_for_publish(timeout=5.0)
            logger.info(f"[MQTT Publisher] Published to '{self.topic}': {payload}")
            return True
        except Exception as e:
            logger.error(f"[MQTT Publisher] Failed to publish: {e}")
            return False

    def stop(self):
        self._client.loop_stop()
        self._client.disconnect()
        logger.info("[MQTT Publisher] Stopped")

    def __del__(self):
        try:
            self.stop()
        except Exception:
            pass