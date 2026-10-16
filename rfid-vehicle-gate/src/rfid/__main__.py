import sys
import time
import logging
from src.rfid.tcp_server import RfidTcpClient
from src.rfid.parser import extract_uid
from src.rfid.service import RfidService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    print("=== SUBSYSTEM RFID VEHICLE GATE DIMULAI ===")
    
    rfid_service = RfidService()

    def on_packet_received(packet_bytes: bytes):
        rfid_raw = extract_uid(packet_bytes)
        if rfid_raw:
            print(f"\n[EVENT] Kartu RFID Terdeteksi: {rfid_raw}")
            rfid_service.handle_rfid(rfid_raw=rfid_raw, gate_id=1)

    # Inisialisasi client yang terhubung ke IP alat RFID
    client = RfidTcpClient(packet_callback=on_packet_received)

    try:
        client.start()
    except KeyboardInterrupt:
        print("\n[INFO] Menghentikan service RFID Subsystem...")
        client.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
