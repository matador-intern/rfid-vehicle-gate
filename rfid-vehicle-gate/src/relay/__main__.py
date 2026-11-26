from src.relay.service import RelayService

def main():
    """
    Entry point utama untuk menjalankan modul relay subsystem 
    menggunakan perintah: python3 -m src.relay
    """
    print("\n========================================================")
    print("=== RFID VEHICLE GATE - RELAY SUBSYSTEM SERVICE (M2-9) ===")
    print("========================================================\n")
    
    service = RelayService()
    service.run()

if __name__ == "__main__":
    main()
