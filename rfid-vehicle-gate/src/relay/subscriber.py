import json
import logging
import sys
import paho.mqtt.client as mqtt
from config.settings import MQTT_CONFIG

from src.relay.controller import RelayController

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("MQTTSubscriber")


class VehicleRegisteredSubscriber:
    """
    MQTT Subscriber yang mendengarkan event 'vehicle/registered'
    dan memicu pembukaan gate (relay pulse) berdasarkan gate_id.
    """
    def __init__(self, controller: RelayController = None):
        self.controller = controller or RelayController()

        self.broker = MQTT_CONFIG["host"]
        self.port = MQTT_CONFIG["port"]
        self.topic = MQTT_CONFIG["topic_vehicle_registered"]
        self.client_id = MQTT_CONFIG.get("client_id", "relay-subscriber")
        self.username = MQTT_CONFIG.get("username")
        self.password = MQTT_CONFIG.get("password")

        self.client = mqtt.Client(
            client_id=self.client_id,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback saat berhasil/gagal terhubung ke MQTT Broker."""
        if rc == 0:
            logger.info(f"Connected to MQTT Broker ({self.broker}:{self.port})")
            logger.info(f"Subscribing to topic: '{self.topic}' with QoS 1")
            client.subscribe(self.topic, qos=1)
        else:
            logger.error(f"Failed to connect to MQTT Broker, result code: {rc}")

    def _on_disconnect(self, client, userdata, rc, properties=None):
        """Callback saat terputus dari MQTT Broker."""
        if rc != 0:
            logger.warning(f"Unexpected disconnect from MQTT Broker (rc={rc}). Waiting for auto-reconnect...")

    def _on_message(self, client, userdata, msg):
        """
        Callback saat pesan MQTT masuk di topik vehicle/registered.
        Memproses payload JSON untuk mendapatkan gate_id & memanggil trigger_gate_pulse.
        """
        payload_raw = msg.payload.decode("utf-8")
        logger.info(f"Message received on topic '{msg.topic}': {payload_raw}")

        try:
            data = json.loads(payload_raw)

            if not isinstance(data, dict):
                raise ValueError("Payload JSON harus berupa dictionary/object.")

            gate_id = data.get("gate_id")
            if gate_id is None:
                logger.warning("Field 'gate_id' tidak ditemukan dalam payload JSON.")
                return

            gate_id = int(gate_id)
            logger.info(f"Processing vehicle access request for Gate ID: {gate_id}")

            self.controller.trigger_gate_pulse(gate_id=gate_id)
            logger.info(f"Finished processing message for Gate ID {gate_id}")

        except json.JSONDecodeError as json_err:
            logger.error(f"JSON decode error: {json_err}")
        except ValueError as val_err:
            logger.error(f"Validation error: {val_err}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)

    def start(self):
        """Memulai subscriber (blocking loop)."""
        logger.info(f"Starting MQTT Subscriber at {self.broker}:{self.port}...")
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Manual interrupt (Ctrl+C). Stopping MQTT Subscriber...")
            self.client.disconnect()
        except Exception as e:
            logger.critical(f"Subscriber stopped due to error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    print("\n========================================================")
    print("=== TEST: MQTT SUBSCRIBER vehicle/registered ===")
    print("========================================================\n")

    subscriber = VehicleRegisteredSubscriber()
    subscriber.start()