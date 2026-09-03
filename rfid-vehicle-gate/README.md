# RFID Vehicle Gate System

Sistem kontrol gate kendaraan berbasis RFID menggunakan Raspberry Pi,
PostgreSQL, MQTT, dan Waveshare Modbus PoE Relay.

---

## 1. Background

Project ini dibuat untuk mengontrol akses kendaraan berdasarkan RFID.

Setiap kendaraan memiliki RFID yang terdaftar pada database dan
memiliki gate tertentu.

Ketika RFID dibaca oleh RFID Reader:

1. RFID Reader mengirimkan data ke Raspberry Pi melalui TCP.
2. Raspberry Pi melakukan parsing RFID.
3. RFID dicari pada database PostgreSQL.
4. Jika kendaraan terdaftar, sistem mendapatkan gate kendaraan.
5. Data kendaraan dicatat ke `vehicle_logs`.
6. Raspberry Pi mengirim event melalui MQTT.
7. Relay Controller menerima event MQTT.
8. Relay Controller menentukan channel relay berdasarkan gate.
9. Raspberry Pi mengirim command Modbus TCP ke Waveshare Relay.
10. Channel relay aktif selama beberapa detik kemudian OFF.

---

## 2. Objective

Tujuan project:

- Membaca RFID kendaraan.
- Melakukan validasi RFID.
- Menyimpan data kendaraan pada PostgreSQL.
- Mencatat aktivitas kendaraan.
- Mengirim event menggunakan MQTT.
- Mengontrol gate melalui Waveshare Relay.
- Memisahkan RFID subsystem dan Relay subsystem.

---

## 3. System Architecture

```text
                    RFID SUBSYSTEM
                    FAHMI

RFID Reader
     |
     | TCP
     v
Raspberry Pi
     |
     v
RFID Parser
     |
     v
PostgreSQL
     |
     +---- Vehicle Lookup
     |
     +---- Gate Lookup
     |
     +---- Vehicle Log
     |
     v
MQTT
vehicle/registered
     |
     |
=============================
       MQTT INTERFACE
=============================
     |
     v

                    RELAY SUBSYSTEM
                    ADZMI

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
     |
     +---- Channel 1 -> Gate 1
     +---- Channel 2 -> Gate 2
     +---- Channel 3 -> Gate 3