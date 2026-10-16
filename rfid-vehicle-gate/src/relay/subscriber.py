import json
import logging
import os
import sys
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

from src.relay.controller import RelayController

# Load environment variables dari file .env
load_dotenv()

# Konfigurasi Logging
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
        
        # Konfigurasi MQTT dari environment variable
        self.broker = os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.topic = os.getenv("MQTT_TOPIC_VEHICLE_REGISTERED", "vehicle/registered")
        self.client_id = os.getenv("MQTT_CLIENT_ID", "relay-subscriber")
        self.username = os.getenv("MQTT_USER", None)
        self.password = os.getenv("MQTT_PASSWORD", None)

        # Inisialisasi Client Paho MQTT
        self.client = mqtt.Client(client_id=self.client_id)

        # Setup authentication jika disetting di .env
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        # Binding Callback Functions
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        """Callback saat berhasil/gagal terhubung ke MQTT Broker."""
        if rc == 0:
            logger.info(f"✅ Berhasil terhubung ke MQTT Broker ({self.broker}:{self.port})")
            logger.info(f"📥 Subscribing ke topik: '{self.topic}'")
            client.subscribe(self.topic)
        else:
            logger.error(f"❌ Gagal koneksi ke MQTT Broker dengan Result Code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback saat terputus dari MQTT Broker."""
        if rc != 0:
            logger.warning(f"⚠️ Terputus dari MQTT Broker secara tidak terduga (rc={rc}). Menunggu auto-reconnect...")

    def _on_message(self, client, userdata, msg):
        """
        [Task M2-6] Callback saat pesan MQTT masuk di topik vehicle/registered.
        Memproses payload JSON untuk mendapatkan gate_id & memanggil trigger_gate_pulse.
        """
        payload_raw = msg.payload.decode("utf-8")
        logger.info(f"📩 Pesan diterima pada topik '{msg.topic}': {payload_raw}")

        try:
            # 1. Parse JSON Payload
            data = json.loads(payload_raw)

            # 2. Validasi & Ambil gate_id
            if not isinstance(data, dict):
                raise ValueError("Payload JSON harus berupa dictionary/object.")

            gate_id = data.get("gate_id")
            if gate_id is None:
                logger.warning("⚠️ Field 'gate_id' tidak ditemukan dalam payload JSON.")
                return

            gate_id = int(gate_id)
            logger.info(f"⚙️ Memproses permintaan akses kendaraan untuk Gate ID: {gate_id}")

            # 3. Eksekusi Pulse Relay via Controller
            self.controller.trigger_gate_pulse(gate_id=gate_id)
            logger.info(f"✅ Selesai memproses pesan untuk Gate ID {gate_id}\n")

        except json.JSONDecodeError as json_err:
            logger.error(f"❌ Kesalahan format JSON pada payload: {json_err}")
        except ValueError as val_err:
            logger.error(f"❌ Validasi tipe data gagal: {val_err}")
        except Exception as e:
            logger.error(f"❌ Error saat memproses pesan MQTT: {e}", exc_info=True)

    def start(self):
        """Memulai subscriber (blocking loop)."""
        logger.info(f"🚀 Memulai MQTT Subscriber di {self.broker}:{self.port}...")
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_forever()
        except KeyboardInterrupt:
            logger.info("🛑 Interupsi manual (Ctrl+C). Menghentikan MQTT Subscriber...")
            self.client.disconnect()
        except Exception as e:
            logger.critical(f"🚨 Subscriber berhenti karena error: {e}")
            sys.exit(1)


# ==========================================
# BLOK PENGUJIAN TASK M2-6 (MQTT SUBSCRIBER)
# ==========================================
if __name__ == "__main__":
    print("\n========================================================")
    print("=== UJI TASK M2-6: MQTT SUBSCRIBER vehicle/registered ===")
    print("========================================================\n")

    subscriber = VehicleRegisteredSubscriber()
    subscriber.start()
