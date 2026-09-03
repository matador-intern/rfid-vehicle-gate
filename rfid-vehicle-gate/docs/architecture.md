# Architecture

## Overview

Dua subsystem yang dipisahkan oleh MQTT sebagai *communication boundary*.

```
                RFID SUBSYSTEM (Fahmi)

RFID Reader
     | TCP
     v
Raspberry Pi
     |
     v
RFID Parser ------------------+
     |                        |
     v                        v
PostgreSQL              Vehicle Lookup
     |                        |
     |                        v
     |                   Vehicle Logs
     |                        |
     +-----------+------------+
                 |
                 v
               MQTT  (topic: vehicle/registered)
                 |
=================|=================  MQTT INTERFACE
                 v

                RELAY SUBSYSTEM (Adzmi)

MQTT Subscriber
     |
     v
Read gate_id
     |
     v
Gate -> Channel
     |
     v
Modbus TCP
     |
     v
Waveshare Relay
     +-- Channel 1 -> Gate 1
     +-- Channel 2 -> Gate 2
     +-- Channel 3 -> Gate 3
```

RFID dan Relay **harus tetap loosely coupled**. Tidak ada import langsung antar
`src/rfid/` dan `src/relay/`. Satu-satunya kontak = payload MQTT.

## Module map

| Module                            | Tanggung jawab                                        |
| --------------------------------- | ---------------------------------------------------- |
| `src/rfid/tcp_server.py`          | Terima koneksi TCP dari RFID Reader, framing byte    |
| `src/rfid/parser.py`              | Parse paket reader -> UID mentah -> normalisasi      |
| `src/rfid/service.py`             | Orkestrasi: lookup vehicle, tulis log, trigger publish |
| `src/rfid/publisher.py`           | Publish `vehicle/registered` ke MQTT                 |
| `src/relay/subscriber.py`         | Subscribe `vehicle/registered`                       |
| `src/relay/controller.py`         | gate_id -> channel -> ON -> wait -> OFF              |
| `src/relay/modbus.py`             | Transport Modbus TCP ke Waveshare relay              |
| `src/relay/service.py`            | Orkestrasi relay dari event MQTT                     |
| `src/database/connection.py`      | Pool / koneksi PostgreSQL                            |
| `src/database/vehicle_repository.py`     | Query tabel `vehicle`                         |
| `src/database/gate_repository.py`        | Query tabel `gate`                            |
| `src/database/vehicle_log_repository.py` | Insert `vehicle_logs`                         |
| `src/config/`                     | Load `.env` -> objek settings                        |

## RFID processing pipeline

```
RFID Reader -> TCP Server -> Packet Parser -> RFID Normalization
  -> Vehicle Lookup -> Vehicle Log -> MQTT Publisher
```

Contoh: UID `E2 34 A1 92` dinormalisasi menjadi `E234A192`.

> **Penting:** TCP adalah byte stream. Jangan menganggap satu `recv()` sama dengan
> satu paket. Framing mengikuti protokol RFID Reader yang sebenarnya
> (`docs/rfid-protocol.md`).

## Relay processing pipeline

```
MQTT Event -> gate_id -> Gate Lookup -> Relay Channel
  -> Relay ON -> Wait (default 3s) -> Relay OFF
```

Relay **selalu** mencoba OFF melalui mekanisme `try/finally`.

## Unknown RFID

```
Unknown RFID -> Log warning
  X  No vehicle log
  X  No vehicle/registered
  X  No relay activation
```

## Final goal

```
RFID Reader -> Raspberry Pi -> RFID Parser -> PostgreSQL
  -> Vehicle Validation -> Vehicle Log -> MQTT
  -> Relay Controller -> Modbus TCP -> Waveshare Relay -> Gate
```

Sistem akhir: modular, testable, maintainable, dengan pemisahan jelas RFID vs Relay.
