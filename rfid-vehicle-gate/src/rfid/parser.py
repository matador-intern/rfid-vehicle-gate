from typing import List, Tuple


def parse_frames(buffer: bytes) -> Tuple[List[bytes], bytes]:
    """
    Memotong buffer byte stream TCP menjadi frame-frame RFID yang utuh.
    """
    frames = []
    while buffer:
        if len(buffer) < 1:
            break
        frame_len = buffer[0] + 1
        if len(buffer) < frame_len:
            break
        frame = buffer[:frame_len]
        buffer = buffer[frame_len:]
        frames.append(frame)
    return frames, buffer

def extract_uid(frame: bytes) -> str | None:
    """
    Ekstrak EPC 24-Hex (12 Byte) dari frame RFID.
    """
    if len(frame) < 5:
        return None

    hex_str = frame.hex().upper()

    # Abaikan paket heartbeat idle pendek
    if hex_str.startswith("0700EE") or hex_str.startswith("0400EE"):
        return None

    # Cari pola EPC Gen2 yang diawali header standar '3008'
    if "3008" in hex_str:
        idx = hex_str.find("3008")
        epc = hex_str[idx : idx + 24]
        if len(epc) == 24:
            return epc

    # Fallback untuk payload lain yang panjangnya mencukupi
    if len(hex_str) >= 24:
        return hex_str[:24]

    return None



def normalize_rfid(uid: str | None) -> str:
    """
    Normalisasi string UID/EPC RFID (Task M1-5):
    - Hapus spasi, titik dua (:), strip (-), tab, newline
    - Ubah huruf ke UPPERCASE
    """
    if not uid:
        return ""

    cleaned = (
        uid.replace(" ", "")
        .replace(":", "")
        .replace("-", "")
        .replace("\t", "")
        .replace("\n", "")
    )

    return cleaned.upper()
