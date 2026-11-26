import sys
import logging
from src.rfid.tcp_server import RfidTcpClient
from src.rfid.parser import extract_uid
from src.rfid.service import RfidService
from config.settings import GATE_CONFIG, RFID_READER_CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

logger = logging.getLogger(__name__)


def parse_gate_id() -> int:
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid gate_id argument: {sys.argv[1]}")
            sys.exit(1)
    return GATE_CONFIG['default_gate_id']


def main():
    gate_id = parse_gate_id()
    logger.info(f"=== RFID SUBSYSTEM STARTED (Gate ID: {gate_id}) ===")

    rfid_service = RfidService()

    def on_packet_received(packet_bytes: bytes):
        rfid_raw = extract_uid(packet_bytes)
        if rfid_raw:
            logger.info(f"[EVENT] RFID detected: {rfid_raw} | Gate: {gate_id}")
            rfid_service.handle_rfid(rfid_raw=rfid_raw, gate_id=gate_id)

    client = RfidTcpClient(
        host=RFID_READER_CONFIG['host'],
        port=RFID_READER_CONFIG['port'],
        packet_callback=on_packet_received,
        auto_inventory=RFID_READER_CONFIG['auto_inventory']
    )

    try:
        client.start()
    except KeyboardInterrupt:
        logger.info("Shutting down RFID subsystem...")
        client.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()