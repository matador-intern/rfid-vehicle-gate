import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    def __init__(self):
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / "config" / ".env"

        if not env_path.exists():
            raise FileNotFoundError(
                f"File .env tidak ditemukan di: {env_path}\n"
                f"Copy dari config/.env.example terlebih dahulu."
            )

        load_dotenv(dotenv_path=env_path)

        self.rfid_reader_ip = os.getenv("RFID_READER_IP")
        self.rfid_reader_port = self._get_int_env("RFID_READER_PORT")
        self.db_host = os.getenv("DB_HOST")
        self.db_port = self._get_int_env("DB_PORT", default=5432)
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.mqtt_broker = os.getenv("MQTT_BROKER")
        self.mqtt_port = self._get_int_env("MQTT_PORT", default=1883)
        self.mqtt_username = os.getenv("MQTT_USERNAME", "")
        self.mqtt_password = os.getenv("MQTT_PASSWORD", "")
        self.relay_on_duration = self._get_int_env("RELAY_ON_DURATION_SECONDS", default=3)
        self._validate()

    def _get_int_env(self, key, default=None):
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Environment variable {key} harus berupa angka, dapat: {value}")

    def _validate(self):
        required_vars = {
            "RFID_READER_IP": self.rfid_reader_ip,
            "RFID_READER_PORT": self.rfid_reader_port,
            "DB_HOST": self.db_host,
            "DB_NAME": self.db_name,
            "DB_USER": self.db_user,
            "DB_PASSWORD": self.db_password,
            "MQTT_BROKER": self.mqtt_broker,
        }

        missing = [key for key, value in required_vars.items() if not value]

        if missing:
            raise ValueError(
                f"Environment variable wajib tidak ditemukan atau kosong:\n"
                f"{', '.join(missing)}\n"
                f"Cek file config/.env"
            )

    def __repr__(self):
        return (
            f"Config(\n"
            f"  RFID: {self.rfid_reader_ip}:{self.rfid_reader_port}\n"
            f"  DB: {self.db_user}@{self.db_host}:{self.db_port}/{self.db_name}\n"
            f"  MQTT: {self.mqtt_broker}:{self.mqtt_port}\n"
            f")"
        )


config = Config()
