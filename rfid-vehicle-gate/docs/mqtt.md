# MQTT Contract

MQTT adalah **communication boundary** antara RFID subsystem dan Relay subsystem.
Broker: `localhost:1883` (lihat `MQTT_HOST` / `MQTT_PORT` di `.env`).

## Topic: `vehicle/registered`

| Peran      | Subsystem       |
| ---------- | --------------- |
| Publisher  | RFID (Fahmi)    |
| Subscriber | Relay (Adzmi)   |

Dipublish **hanya** ketika RFID dikenal dan `vehicle_logs` sudah ditulis.

### Payload

```json
{
  "vehicle_id": 1,
  "rfid": "E234A192",
  "gate_id": 1,
  "timestamp": "2026-09-04T08:30:21"
}
```

| Field        | Tipe   | Keterangan                                  |
| ------------ | ------ | ------------------------------------------- |
| `vehicle_id` | int    | PK dari tabel `vehicle`                     |
| `rfid`       | string | UID sudah dinormalisasi (uppercase, no spasi)|
| `gate_id`    | int    | PK dari tabel `gate`, dipakai relay untuk lookup channel |
| `timestamp`  | string | ISO-8601, waktu pembacaan RFID              |

## Aturan

- Kontrak ini **tidak boleh diubah sepihak**. Perubahan payload = update kode di
  kedua subsystem + update dokumen ini + review bersama.
- QoS dan retain: default QoS 1, retain `false` (event, bukan state).
- Client ID: `MQTT_CLIENT_ID_RFID` dan `MQTT_CLIENT_ID_RELAY` dari `.env`.
- Unknown RFID -> **tidak ada** publish ke topic ini.

## Testing

- Uji dengan broker asli (`localhost:1883`): `mosquitto_sub -t vehicle/registered -v`
  untuk memantau publish, `mosquitto_pub` untuk mengirim payload uji ke subscriber.
  Lihat `docs/hardware-testing.md`.
- `pytest` opsional untuk logika murni (validasi / serialisasi payload) dengan
  MQTT client di-mock.
