# RFID Protocol

## Transport

- RFID Reader terhubung ke Raspberry Pi lewat **TCP**.
- Reader: `192.168.10.10` (lihat `RFID_READER_HOST` / `RFID_READER_PORT`).
- Raspberry Pi menjalankan TCP server / listener (`RFID_TCP_BIND_HOST:RFID_TCP_BIND_PORT`).

> Cek manual reader: sebagian model bertindak sebagai TCP **client** (connect ke Pi),
> sebagian sebagai TCP **server** (Pi yang connect). Tentukan sesuai hardware,
> lalu perbarui dokumen ini.

## Framing (WAJIB diisi dari manual reader)

**Jangan mengarang protokol.** Isi bagian ini setelah membaca manual / meng-capture
traffic reader yang sebenarnya:

- Byte awal / header: `TODO`
- Panjang payload: `TODO` (fixed / length-prefixed / delimiter)
- Delimiter akhir (mis. `\r\n`): `TODO`
- Checksum / CRC: `TODO`
- Encoding UID (ASCII hex / binary): `TODO`

### Aturan byte stream

- TCP adalah **byte stream**. Satu `recv()` **bukan** satu paket.
- Gunakan buffer akumulasi: baca ke buffer, potong paket lengkap, sisakan sisa byte
  untuk `recv()` berikutnya.
- Tangani: paket terpotong, banyak paket dalam satu `recv()`, koneksi putus.

## Normalisasi UID

Setelah UID diekstrak dari paket:

1. Buang semua whitespace.
2. Uppercase.
3. (Opsional, sesuai reader) buang separator seperti `:` atau `-`.

Contoh:

```
"E2 34 A1 92"  -> "E234A192"
"e2:34:a1:92"  -> "E234A192"
```

Hasil normalisasi inilah yang dipakai untuk lookup ke tabel `vehicle` dan yang
masuk ke payload MQTT.

## Setelah normalisasi

```
RFID Normalization -> Vehicle Lookup (vehicle_repository.find_by_rfid)
  -> [dikenal]     -> Vehicle Log -> MQTT publish vehicle/registered
  -> [tidak dikenal] -> log warning, stop
```
