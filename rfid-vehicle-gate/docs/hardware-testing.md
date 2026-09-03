# Hardware Testing

Verifikasi setiap task **langsung di perangkat fisik**. Catat langkah + hasil
(output terminal, serial log, foto relay/gate) di deskripsi PR.

## Perangkat & jaringan

Subnet `192.168.10.0/24` (lihat `docs/architecture.md`, nilai dari `.env`).

| Perangkat       | IP              | Catatan                         |
| --------------- | --------------- | ------------------------------- |
| RFID Reader     | 192.168.10.10   | TCP                             |
| Waveshare Relay | 192.168.10.20   | Modbus TCP port 502             |
| Raspberry Pi    | 192.168.10.100  | menjalankan RFID & Relay service|
| MQTT broker     | localhost:1883  | di Raspberry Pi                 |
| PostgreSQL      | localhost:5432  | di Raspberry Pi                 |

## Persiapan (sekali)

```bash
# di Raspberry Pi
source .venv/bin/activate
pip install -r requirements.txt
cp config/.env.example .env && nano .env      # sesuaikan IP, kredensial DB, dsb.

# muat .env ke shell (supaya $DB_USER, $WAVESHARE_RELAY_HOST, dst. bisa dipakai di perintah manual)
set -a && source .env && set +a

# cek konektivitas
ping -c3 192.168.10.10        # RFID reader
ping -c3 192.168.10.20        # relay
# broker & db jalan?
mosquitto_sub -h localhost -t '#' -v &         # monitor semua topik MQTT
psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c '\dt'
```

Seed minimal data uji di PostgreSQL: minimal 1 `device`, 1 `gate` (dengan `channel`
yang benar), 1 `vehicle` dengan `rfid` = UID kartu tes yang sudah dinormalisasi.

---

## Menjalankan tiap subsystem SENDIRI-SENDIRI

Kedua subsystem berjalan sebagai proses Python terpisah dan **tidak saling import**.
Batas mereka cuma MQTT, jadi tiap orang bisa menguji bagiannya tanpa menunggu yang lain:

- **Fahmi** menguji RFID tanpa relay: cukup lihat pesan keluar di MQTT.
- **Adzmi** menguji relay tanpa RFID reader: cukup kirim pesan MQTT palsu.

`src/` belum dipasang sebagai package, jadi jalankan dengan `PYTHONPATH=src`
(atau `cd src` dulu). Semua perintah di bawah dari root repo, venv aktif.

### RFID subsystem (Fahmi)

Butuh: PostgreSQL + broker MQTT + RFID reader. **Tidak butuh relay.**

```bash
# terminal 1 — pantau output subsystem
mosquitto_sub -h localhost -t vehicle/registered -v

# terminal 2 — jalankan service RFID
PYTHONPATH=src python -m rfid
# (entry point dibuat di task M1-10: src/rfid/__main__.py)
```

Kalau reader belum siap, uji lapis per lapis tanpa hardware reader:

```bash
# normalisasi UID saja
PYTHONPATH=src python -c "from rfid.parser import normalize_rfid; print(normalize_rfid('E2 34 A1 92'))"

# kirim byte paket palsu ke TCP server (format sesuai docs/rfid-protocol.md)
PYTHONPATH=src python -m rfid &
printf '<byte-paket-sesuai-protokol>' | nc 127.0.0.1 "$RFID_TCP_BIND_PORT"
```

### Relay subsystem (Adzmi)

Butuh: broker MQTT + relay Waveshare + PostgreSQL (untuk gate -> channel).
**Tidak butuh RFID reader.**

```bash
# terminal 1 — jalankan service relay
PYTHONPATH=src python -m relay
# (entry point dibuat di task M2-9: src/relay/__main__.py)

# terminal 2 — kirim event palsu, seolah-olah dari RFID subsystem
mosquitto_pub -h localhost -t vehicle/registered \
  -m '{"vehicle_id":1,"rfid":"E234A192","gate_id":1,"timestamp":"2026-09-04T08:30:21"}'
```

Uji lapis Modbus saja (tanpa MQTT), untuk memvalidasi register dari manual Waveshare:

```bash
PYTHONPATH=src python -c "
from relay.modbus import WaveshareModbusRelay
import os, time
r = WaveshareModbusRelay(os.environ['WAVESHARE_RELAY_HOST'])
r.open_channel(1); time.sleep(2); r.close_channel(1)
"
```

### Uji dua subsystem bersamaan

Jalankan `python -m rfid` dan `python -m relay` di dua terminal di Pi, lalu tap
kartu asli. Ini yang dicatat di bagian C.

---

## A. Uji RFID subsystem (Fahmi)

1. Jalankan service RFID di Pi (`python -m rfid` atau entry point yang dibuat).
2. **Konektivitas reader**: pastikan koneksi TCP ke/ dari reader terbentuk (cek log).
3. **Kartu terdaftar**: tap kartu yang `rfid`-nya ada di tabel `vehicle`.
   - [ ] UID di log = hasil normalisasi yang benar (mis. `E234A192`)
   - [ ] baris baru muncul di `vehicle_logs` (`SELECT * FROM vehicle_logs ORDER BY id DESC LIMIT 5;`)
   - [ ] `mosquitto_sub` menampilkan pesan di `vehicle/registered` dengan payload
         `{vehicle_id, rfid, gate_id, timestamp}` sesuai `docs/mqtt.md`
4. **Kartu tidak terdaftar**: tap kartu yang tidak ada di DB.
   - [ ] hanya muncul log warning
   - [ ] TIDAK ada baris di `vehicle_logs`
   - [ ] TIDAK ada pesan MQTT
5. **Byte stream**: tap beberapa kartu cepat berturut-turut.
   - [ ] tiap tap diproses sebagai 1 event (framing benar, tidak ada paket
         tergabung / terpotong yang salah parse)
6. **Recovery**: cabut & pasang lagi kabel reader.
   - [ ] service tidak crash, koneksi pulih sendiri

## B. Uji Relay subsystem (Adzmi)

1. **Modbus manual dulu** (sebelum wiring MQTT): dari Pi, kirim command ON/OFF ke
   satu channel relay pakai nilai register dari manual Waveshare (`docs/modbus-relay.md`).
   - [ ] channel yang benar bunyi "klik" dan LED menyala
   - [ ] OFF mengembalikan channel ke kondisi awal
2. Jalankan service relay (`python -m relay` atau entry point yang dibuat).
3. **End-to-end dari MQTT**: publish payload uji ke `vehicle/registered`:
   ```bash
   mosquitto_pub -h localhost -t vehicle/registered \
     -m '{"vehicle_id":1,"rfid":"E234A192","gate_id":1,"timestamp":"2026-09-04T08:30:21"}'
   ```
   - [ ] `gate_id` -> channel benar sesuai `gate.channel`
   - [ ] relay ON lalu OFF otomatis setelah ± 3 detik (`RELAY_ON_DURATION_SECONDS`)
   - [ ] gate fisik benar-benar terbuka lalu menutup
4. **try/finally**: hentikan paksa service (Ctrl+C) saat relay sedang ON.
   - [ ] channel tetap kembali OFF (tidak "menggantung" menyala)
5. **gate_id tidak dikenal**: publish payload dengan `gate_id` yang tidak ada.
   - [ ] log warning, tidak ada channel yang aktif
6. **Relay unreachable**: cabut kabel relay lalu publish payload.
   - [ ] error di-log, service tidak crash

## C. Uji integrasi penuh

1. RFID service + Relay service jalan bersamaan di Pi.
2. Tap kartu terdaftar untuk Gate 1.
   - [ ] rantai lengkap: reader -> log DB -> MQTT -> relay channel 1 -> Gate 1 buka -> tutup
3. Ulangi untuk Gate 2 dan Gate 3 (kartu / vehicle berbeda).
4. Ukur waktu dari tap sampai gate mulai membuka; catat di PR.

## Format catatan hasil (tempel di PR)

```
Task: M_-__
Tanggal / perangkat:
Langkah yang dijalankan:
Hasil (output / log / foto):
Status: PASS / FAIL + catatan
```
