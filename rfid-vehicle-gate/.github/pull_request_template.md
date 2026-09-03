<!-- Judul PR: <tipe>(<area>): ringkasan singkat  -- contoh: feat(rfid): implement TCP server and parser -->

## Issue terkait

Closes #___

## Subsystem

- [ ] RFID (`src/rfid/`) — Fahmi
- [ ] Relay (`src/relay/`) — Adzmi
- [ ] Database (`src/database/`)
- [ ] Docs / config

## Apa yang berubah

<!-- Jelaskan singkat. -->

## Checklist (Definition of Done)

- [ ] Sudah membaca `README.md` dan dokumen `docs/` yang relevan
- [ ] Tidak mengarang protokol RFID / register Modbus
- [ ] Batas RFID <-> Relay tetap terjaga (komunikasi hanya via MQTT)
- [ ] Tidak ada credential / IP hardcoded (semua dari `.env`)
- [ ] **Sudah diuji di hardware fisik** (lihat `docs/hardware-testing.md`), hasil ditempel di bawah
- [ ] `pytest` untuk logika murni ditambahkan bila relevan
- [ ] Memperbarui dokumentasi bila behavior berubah
- [ ] Branch dari issue, bukan commit langsung ke `main`

## Hasil uji hardware

```
Task:
Tanggal / perangkat:
Langkah:
Hasil (output / log / foto):
Status: PASS / FAIL + catatan
```
