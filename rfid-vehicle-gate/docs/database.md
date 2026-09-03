# Database

PostgreSQL. Tabel utama: `device`, `gate`, `vehicle`, `vehicle_logs`.

## Relasi

```
device --> gate --> vehicle --> vehicle_logs
```

- `gate` dimiliki oleh sebuah `device`.
- `vehicle` terhubung ke satu `gate`.
- `vehicle_logs` mencatat setiap pembacaan RFID untuk satu `vehicle`.
- Kolom `rfid` pada `vehicle` bersifat **unique** dan disimpan sudah dinormalisasi
  (uppercase, tanpa spasi, contoh `E234A192`).

## Skema referensi

> Skema di bawah adalah acuan awal. Sesuaikan tipe/constraint saat implementasi,
> lalu perbarui dokumen ini bila berubah.

```sql
CREATE TABLE device (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    ip_address  INET,
    created_at  TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE gate (
    id          SERIAL PRIMARY KEY,
    device_id   INTEGER NOT NULL REFERENCES device(id),
    name        TEXT NOT NULL,
    channel     SMALLINT NOT NULL,          -- channel relay Waveshare
    created_at  TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (device_id, channel)
);

CREATE TABLE vehicle (
    id          SERIAL PRIMARY KEY,
    rfid        TEXT NOT NULL UNIQUE,       -- sudah dinormalisasi
    plate_number TEXT,
    owner_name  TEXT,
    gate_id     INTEGER NOT NULL REFERENCES gate(id),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE vehicle_logs (
    id          SERIAL PRIMARY KEY,
    vehicle_id  INTEGER NOT NULL REFERENCES vehicle(id),
    rfid        TEXT NOT NULL,
    gate_id     INTEGER NOT NULL REFERENCES gate(id),
    read_at     TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_vehicle_logs_vehicle_id ON vehicle_logs(vehicle_id);
CREATE INDEX idx_vehicle_logs_read_at    ON vehicle_logs(read_at);
```

## Query yang dibutuhkan

| Repository                    | Operasi                                             |
| ---------------------------- | -------------------------------------------------- |
| `vehicle_repository`         | `find_by_rfid(rfid) -> Vehicle | None`             |
| `gate_repository`            | `find_by_id(gate_id) -> Gate | None` (butuh channel) |
| `vehicle_log_repository`     | `insert(vehicle_id, rfid, gate_id, read_at)`       |

## Aturan

- Semua kredensial DB dari `.env` (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).
- Tidak ada RFID yang belum dinormalisasi masuk ke tabel.
- RFID tidak dikenal -> **tidak** menulis `vehicle_logs`.
