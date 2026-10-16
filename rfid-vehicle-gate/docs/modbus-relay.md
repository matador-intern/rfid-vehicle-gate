# Waveshare Modbus PoE Relay - Specification & Register Mapping

Dokumen ini berisi spesifikasi teknis dan pemetaan register Modbus TCP untuk Waveshare Modbus PoE Relay yang digunakan pada Relay Subsystem.

---

## 1. Configuration & Network Default

| Parameter | Value | Keterangan |
| :--- | :--- | :--- |
| **Protocol** | Modbus TCP | Komunikasi via Ethernet Socket |
| **Default IP** | `192.168.1.200` | Dapat dikonfigurasi melalui `.env` (`RELAY_HOST`) |
| **Port Modbus** | `502` | Port standar Modbus TCP (`RELAY_PORT`) |
| **Slave ID / Unit ID** | `1` (`0x01`) | Device ID default Modbus Slave |

---

## 2. Modbus Function Codes

| Function Code (Hex) | Function Code (Dec) | Function Name | Kegunaan dalam Project |
| :--- | :--- | :--- | :--- |
| `0x01` | `1` | Read Coils | Membaca status ON/OFF relay |
| `0x05` | `5` | Write Single Coil | Mengontrol 1 channel relay (ON/OFF) |
| `0x0F` | `15` | Write Multiple Coils | Mengontrol banyak channel relay sekaligus |

---

## 3. Coil Address Mapping (Relay Channel)

Sistem menggunakan 0-based indexing address untuk pengontrolan relay:

| Gate Target | Channel Relay | Coil Address (Dec) | Coil Address (Hex) | Command ON Value | Command OFF Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Channel 1 | `0` | `0x0000` | `0xFF00` | `0x0000` |
| **Gate 2** | Channel 2 | `1` | `0x0001` | `0xFF00` | `0x0000` |
| **Gate 3** | Channel 3 | `2` | `0x0002` | `0xFF00` | `0x0000` |
| - | Channel 4 | `3` | `0x0003` | `0xFF00` | `0x0000` |
| - | Channel 5-8 | `4` - `7` | `0x0004` - `0x0007` | `0xFF00` | `0x0000` |

*Keterangan Value Modbus Standard:*
* **ON State:** Data value = `0xFF00` (65280)
* **OFF State:** Data value = `0x0000` (0)

---

## 4. Struktur Frame Modbus TCP (Contoh Payload Write Single Coil)

Struktur MBAP Header + PDU Modbus TCP untuk mengaktifkan Relay Channel 1:

```text
[ Transaction ID ] [ Protocol ID ] [ Length ] [ Unit ID ] [ FC ] [ Addr High ] [ Addr Low ] [ Value High ] [ Value Low ]
      0x00 0x01        0x00 0x00    0x00 0x06    0x01     0x05      0x00         0x00          0xFF          0x00
