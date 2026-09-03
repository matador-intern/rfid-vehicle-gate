# Tugas Fahmi — RFID Subsystem

Direktori: `src/rfid/`, `tests/rfid/` (boleh menyentuh `src/database/` untuk repository).
Baca dulu: `README.md`, `docs/workflow.md`, `docs/hardware-testing.md`, `docs/architecture.md`, `docs/rfid-protocol.md`, `docs/mqtt.md`, `docs/database.md`.

Batas: **tidak boleh import dari `src/relay/`**. Kontak ke relay hanya lewat MQTT.

Semua kode dan test ditulis sendiri oleh Fahmi. Direktori `src/` dan `tests/`
sekarang masih kosong (hanya `__init__.py`). Nama file di kolom "File utama"
adalah saran, boleh disesuaikan asal strukturnya tetap rapi.

## Ruang lingkup

- RFID TCP server
- RFID parser
- RFID normalization
- Vehicle lookup
- Vehicle logs
- MQTT publisher
- Uji hardware + laporan hasil di PR

## Daftar task (buat 1 issue + 1 branch + 1 PR per task)

Kolom "Bukti hardware" = apa yang harus ditunjukkan di perangkat nyata
(prosedur di `docs/hardware-testing.md` bagian A).

| #    | Task | File utama | Bukti hardware |
| ---- | ---- | ---------- | -------------- |
| M1-1 | Settings loader dari `.env` | `src/config/__init__.py` | service baca `.env` di Pi, IP/kredensial benar; error jelas kalau var wajib kosong |
| M1-2 | Pelajari & tulis framing protokol reader | `docs/rfid-protocol.md` | capture traffic reader asli, tabel framing terisi & cocok dengan capture |
| M1-3 | TCP server + buffer byte-stream | `src/rfid/tcp_server.py` | koneksi TCP ke reader asli terbentuk; tap cepat berturut-turut tetap 1 event per tap |
| M1-4 | Parser paket -> UID mentah | `src/rfid/parser.py` | UID di log cocok dengan yang tercetak di kartu / tool reader |
| M1-5 | Normalisasi UID | `src/rfid/parser.py` (`normalize_rfid`) | UID hasil normalisasi (mis. `E234A192`) match row `vehicle` |
| M1-6 | `vehicle_repository.find_by_rfid` | `src/database/vehicle_repository.py` | tap kartu terdaftar -> lookup ketemu; kartu asing -> None (cek di PostgreSQL asli) |
| M1-7 | `vehicle_log_repository.insert` | `src/database/vehicle_log_repository.py` | baris baru muncul di `vehicle_logs` setiap tap kartu terdaftar |
| M1-8 | MQTT publisher `vehicle/registered` | `src/rfid/publisher.py` | `mosquitto_sub` menerima payload sesuai `docs/mqtt.md` |
| M1-9 | Orkestrasi `RfidService.handle_rfid` | `src/rfid/service.py` | kartu terdaftar -> log + publish; kartu asing -> warning saja, tanpa log & tanpa publish |
| M1-10 | Entry point runnable (Pi) | `src/rfid/__main__.py` (baru) | `python -m rfid` di Pi jalan; recovery saat kabel reader dicabut-pasang |

## Aturan khusus

- **Jangan mengarang protokol RFID.** Kalau belum tahu framing, kerjakan M1-2 dulu.
- Unknown RFID: log warning, **tidak** ada vehicle log, **tidak** ada publish.
- Semua IP/port/kredensial dari `.env`.
- Setiap task diuji langsung di hardware (`docs/hardware-testing.md` bagian A),
  langkah + hasil ditempel di PR.
- `pytest` opsional untuk logika murni (normalisasi UID, framing parser).
