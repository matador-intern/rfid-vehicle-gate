# Tugas Adzmi — Relay Subsystem

Direktori: `src/relay/`, `tests/relay/` (boleh menyentuh `src/database/gate_repository.py`).
Baca dulu: `README.md`, `docs/workflow.md`, `docs/hardware-testing.md`, `docs/architecture.md`, `docs/modbus-relay.md`, `docs/mqtt.md`, `docs/database.md`.

Batas: **tidak boleh import dari `src/rfid/`**. Input hanya payload MQTT `vehicle/registered`.

Semua kode dan test ditulis sendiri oleh Adzmi. Direktori `src/` dan `tests/`
sekarang masih kosong (hanya `__init__.py`). Nama file di kolom "File utama"
adalah saran, boleh disesuaikan asal strukturnya tetap rapi.

## Ruang lingkup

- Waveshare Modbus TCP
- Relay ON/OFF
- MQTT subscriber
- Gate lookup
- Channel mapping
- Error handling
- Uji hardware + laporan hasil di PR

## Daftar task (buat 1 issue + 1 branch + 1 PR per task)

Kolom "Bukti hardware" = apa yang harus ditunjukkan di perangkat nyata
(prosedur di `docs/hardware-testing.md` bagian B).

| #    | Task | File utama | Bukti hardware |
| ---- | ---- | ---------- | -------------- |
| M2-1 | Pelajari & tulis register Waveshare | `docs/modbus-relay.md` | tabel slave ID / function code / coil address terisi dari manual resmi model yang dipakai |
| M2-2 | Transport Modbus TCP (`open_channel` / `close_channel`) | `src/relay/modbus.py` | kirim ON/OFF manual ke relay asli: channel benar "klik" + LED, OFF balik normal |
| M2-3 | `gate_repository.find_by_id` (butuh `channel`) | `src/database/gate_repository.py` | lookup ke PostgreSQL asli mengembalikan `channel` yang benar per `gate_id` |
| M2-4 | Channel mapping gate -> channel | `src/relay/controller.py` | Gate 1/2/3 mengaktifkan channel 1/2/3 di relay fisik |
| M2-5 | Relay ON -> wait -> OFF dengan `try/finally` | `src/relay/controller.py` | relay ON lalu OFF sendiri ± 3 detik; Ctrl+C saat ON tetap membuat channel OFF |
| M2-6 | MQTT subscriber `vehicle/registered` | `src/relay/subscriber.py` | `mosquitto_pub` payload uji -> subscriber menerima & memproses `gate_id` |
| M2-7 | Error handling koneksi Modbus | `src/relay/modbus.py` / `controller.py` | cabut kabel relay lalu publish: error di-log, service tidak crash |
| M2-8 | Orkestrasi `RelayService.run` | `src/relay/service.py` | end-to-end: publish `vehicle/registered` -> gate fisik buka lalu tutup |
| M2-9 | Entry point runnable | `src/relay/__main__.py` (baru) | `python -m relay` di Pi jalan dan tersambung ke broker + relay |
| M2-10| Integrasi penuh dengan RFID subsystem | — | tap kartu -> RFID service -> MQTT -> relay -> Gate 1/2/3 buka-tutup; catat waktu tap->buka |

## Aturan khusus

- **Register/coil/function code/slave ID TIDAK boleh ditebak.** Kerjakan M2-1 dulu,
  lalu langsung uji ke relay fisik.
- Durasi default relay ON = 3 detik (`RELAY_ON_DURATION_SECONDS`).
- Relay **selalu** mencoba OFF lewat `try/finally`.
- Semua IP/port dari `.env`.
- Setiap task diuji langsung di hardware (`docs/hardware-testing.md` bagian B),
  langkah + hasil ditempel di PR.
- `pytest` opsional untuk logika murni (channel mapping, parsing payload).
