# Development Workflow

## Git

```
Issue -> Branch -> Development -> Commit -> Push -> Pull Request -> Review -> Merge -> Issue Closed
```

- **Jangan coding langsung di `main`.**
- Satu branch per issue: `feature/<area>-<deskripsi-singkat>`
  (contoh: `feature/rfid-tcp-parser`, `feature/relay-modbus-transport`).
- Commit message berprefix tipe: `feat(rfid): ...`, `fix(relay): ...`,
  `docs(mqtt): ...`, `test(rfid): ...`, `chore: ...`.
- Push langsung ke `main` hanya untuk konfigurasi awal. Setelah workflow dimulai,
  semua perubahan lewat Issue -> Branch -> PR.
- Setiap PR memakai `.github/pull_request_template.md`.

Contoh:

```bash
git checkout -b feature/rfid-tcp-parser
# ... development ...
git add .
git commit -m "feat(rfid): implement TCP server and parser"
git push -u origin feature/rfid-tcp-parser
```

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config/.env.example .env      # lalu edit .env sesuai kebutuhan
```

Cara menjalankan tiap subsystem sendiri (RFID saja / Relay saja) ada di
`docs/hardware-testing.md` bagian "Menjalankan tiap subsystem sendiri-sendiri".

## Testing

**Verifikasi utama = uji langsung dengan hardware fisik** (RFID reader, Waveshare
relay, broker MQTT, dan PostgreSQL yang sebenarnya). Prosedur lengkap ada di
`docs/hardware-testing.md`.

Setiap task hanya dianggap selesai kalau sudah dijalankan di perangkat nyata dan
hasilnya dicatat di PR (langkah, output, foto/serial log bila ada).

`pytest` bersifat pelengkap untuk logika murni yang tidak butuh perangkat
(mis. normalisasi UID, framing parser, channel mapping). Jalankan bila ada:

```bash
pytest
```

- Boleh pakai `pytest-mock` untuk unit test logika, tapi **bukan pengganti** uji hardware.
- Jangan mem-block progress hanya karena unit test belum ditulis; yang wajib adalah
  bukti jalan di hardware.

## Aturan wajib

1. Baca `README.md` dan dokumen `docs/` yang relevan sebelum mulai.
2. Periksa implementasi yang sudah ada.
3. **Tidak mengarang protokol RFID** (lihat `docs/rfid-protocol.md`).
4. **Tidak mengarang register Modbus** (lihat `docs/modbus-relay.md`).
5. Menjaga batas RFID <-> Relay: komunikasi hanya lewat MQTT, tidak ada import silang.
6. Menguji setiap behavior baru langsung di hardware fisik (lihat `docs/hardware-testing.md`).
7. Memperbarui dokumentasi jika behavior berubah.
8. Tidak memasukkan credential / IP hardcoded ke repository — semua dari `.env`.

## Definition of Done (per task)

- Kode jalan dan sesuai kontrak di `docs/`.
- **Sudah diuji di hardware fisik**, langkah + hasil dicatat di PR.
- Unit test `pytest` untuk logika murni ditambahkan bila relevan.
- Tidak ada secret / IP hardcoded.
- Dokumentasi terkait diperbarui bila perlu.
- Dibuka sebagai PR dari branch, direview minimal 1 orang sebelum merge.
