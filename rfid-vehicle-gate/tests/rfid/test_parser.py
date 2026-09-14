import sys
from pathlib import Path

# Tambahkan direktori src ke sys.path
src_path = str(Path(__file__).resolve().parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.rfid.parser import extract_uid, normalize_rfid, parse_frames


def test_normalize_rfid_valid():
    assert normalize_rfid("300833b2ddd9014000000004") == "300833B2DDD9014000000004"
    assert normalize_rfid("3008-33B2-DDD9") == "300833B2DDD9"
    assert normalize_rfid("30:08:33:B2") == "300833B2"
    assert normalize_rfid("  300833b2  ") == "300833B2"
    assert normalize_rfid("e2 34 a1 92") == "E234A192"
    assert normalize_rfid("e2:34:a1:92") == "E234A192"


def test_normalize_rfid_empty():
    assert normalize_rfid("") == ""
    assert normalize_rfid(None) == ""


def test_parse_frames_single():
    # 1 paket utuh (8 byte)
    buffer = bytes.fromhex("0700EE0030088334")
    frames, remaining = parse_frames(buffer)
    assert len(frames) == 1
    assert frames[0] == buffer
    assert remaining == b""


def test_parse_frames_partial():
    # Paket terpotong (baru masuk 4 byte)
    buffer = bytes.fromhex("0700EE00")
    frames, remaining = parse_frames(buffer)
    assert len(frames) == 0
    assert remaining == buffer


def test_parse_frames_multiple():
    # 2 paket sekaligus dalam 1 buffer
    p1 = bytes.fromhex("0700EE0030088334")
    p2 = bytes.fromhex("0700890130088335")
    buffer = p1 + p2
    frames, remaining = parse_frames(buffer)
    assert len(frames) == 2
    assert frames[0] == p1
    assert frames[1] == p2
    assert remaining == b""
