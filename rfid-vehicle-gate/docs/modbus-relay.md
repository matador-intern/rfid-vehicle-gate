# Modbus Relay (Waveshare)

## Perangkat

- Waveshare Modbus PoE Relay.
- IP: `192.168.10.20`, Modbus TCP port `502` (lihat `WAVESHARE_RELAY_HOST` /
  `WAVESHARE_RELAY_PORT` / `WAVESHARE_RELAY_UNIT_ID`).

## Modbus Safety Rule

> Register address, coil address, function code, slave ID, dan format command
> **TIDAK BOLEH DITEBAK.**

Implementasi harus:

1. Mengikuti **manual resmi Waveshare** untuk model yang tepat.
2. Diuji dengan **hardware asli** sebelum dianggap selesai.

Isi tabel berikut dari manual (jangan tinggalkan tebakan di kode):

| Item                       | Nilai (dari manual)     |
| -------------------------- | ---------------------- |
| Slave / Unit ID            | `TODO`                 |
| Function code ON/OFF       | `TODO` (mis. 0x05 Write Single Coil) |
| Coil address channel 1..N  | `TODO`                 |
| Nilai ON / OFF             | `TODO` (mis. 0xFF00 / 0x0000) |
| Read status (opsional)     | `TODO`                 |

## Channel mapping

Default (sesuaikan dengan tabel `gate.channel` di database):

```
Channel 1 -> Gate 1
Channel 2 -> Gate 2
Channel 3 -> Gate 3
```

Relay mendapat `gate_id` dari payload MQTT, lalu `gate_repository.find_by_id`
memberi `channel`.

## Relay processing

```
MQTT Event -> gate_id -> Gate Lookup -> Relay Channel
  -> Relay ON -> Wait (RELAY_ON_DURATION_SECONDS, default 3s) -> Relay OFF
```

### Aturan

- Durasi default ON = **3 detik**.
- Relay **selalu** mencoba OFF lewat `try/finally`:

```python
open_relay(channel)
try:
    time.sleep(on_duration)
finally:
    close_relay(channel)   # selalu dijalankan, walaupun ada exception
```

- Kegagalan koneksi Modbus harus di-log, tidak boleh membuat channel "menggantung" ON.

## Testing

- Verifikasi utama = uji langsung ke relay Waveshare asli. Prosedur di
  `docs/hardware-testing.md` bagian B.
- Uji manual ON/OFF per channel dulu (nilai register dari manual), baru wiring MQTT.
- `pytest` opsional untuk logika murni (mis. gate -> channel mapping) dengan
  transport Modbus di-mock; bukan pengganti uji hardware.
