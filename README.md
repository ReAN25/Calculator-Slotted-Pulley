# ⚙️ Slotted Timing Belt Pulley Calculator & Kinematic Simulator

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GUI](https://img.shields.io/badge/GUI-Tkinter%20%7C%20Matplotlib-orange.svg)](#)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](#)

Aplikasi desktop interaktif berbasis Python untuk menghitung parameter teknik, geometri chordal action, dan mensimulasikan kinematika **Pulley Timing Belt Berongga (Slotted Pulley)**. 

Dirancang khusus untuk kebutuhan perancangan mekanisme transmisi timing belt yang memiliki **bracket / attachment pembawa** pada belt, di mana pulley memerlukan rongga U-slot presisi agar bracket dapat melintas bebas tanpa benturan (*collision-free*).

---

## 📸 Tampilan Antarmuka (Preview)

Aplikasi dilengkapi antarmuka modern dark-mode (Catppuccin themed) yang terbagi menjadi 3 panel:
1. **Panel Kontrol & Parameter Desain** (Kiri)
2. **Visualisasi Animasi Kinematika Real-Time** (Tengah)
3. **Laporan & Verifikasi Teknis Lengkap** (Kanan)

---

## ✨ Fitur Utama

- 📐 **Kalkulasi Geometri & Kinematika Presisi**:
  - Penentuan Pitch Diameter ($D_p$) dan Outer Diameter ($D_o$).
  - Perhitungan Jarak Antar Sumbu (*Center Distance - $C$*) secara eksak menggunakan iterasi analitik Newton-Raphson.
  - Perhitungan sudut kontak (*Wrap Angle*) dan panjang lintasan belt.
- 🎯 **Analisis Chordal Action & Dimensi Rongga (Slot)**:
  - **Chordal Dip**: Penurunan lintasan chordal saat bracket melingkari pulley.
  - **Ayunan Masuk/Keluar (Lead-in Swing)**: Deformasi sudut saat attachment memasuki radius pulley.
  - Rekomendasi dimensi rongga U-slot (lebar & kedalaman minimum) dengan penambahan toleransi *clearance*.
- 🔄 **Verifikasi Sinkronisasi Otomatis**:
  - Validasi matematis apakah posisi rongga pulley driver dan driven akan selalu bertepatan dengan bracket belt setiap siklus putaran:
    $$\text{Periode} = \frac{Z}{\text{slots}} \quad \text{dan} \quad Z_{belt} \pmod{\frac{Z}{\text{slots}}} = 0$$
- 🛡️ **Pengecekan Kekuatan & Integritas Mekanik**:
  - Estimasi gaya tarik belt ($F_t$) berdasarkan torsi kerja ($T$).
  - Jumlah gigi aktif yang mencengkeram (*remaining engaged teeth*).
  - Ketebalan sisa dinding struktural antara dasar rongga dan diameter poros (*shaft wall thickness*).
- 🎬 **Simulasi Animasi & Inspeksi Interaktif**:
  - Animasi gerak kontinu dengan pengaturan kecepatan putar variabel.
  - Fitur **Inspeksi Manual (Slider)** untuk memeriksa pergerakan langkah demi langkah (0 - 3 siklus putaran) guna mengamati clearance saat bracket memasuki rongga.

---

## 🧮 Rumus & Logika Perhitungan

| Parameter | Rumus / Pendekatan | Deskripsi |
| :--- | :--- | :--- |
| **Pitch Diameter ($D_p$)** | $D_p = \frac{Z \cdot p}{\pi}$ | Diameter pitch standar timing belt |
| **Outer Diameter ($D_o$)** | $D_o = 2 \times (r_p - \Delta_{ded})$ | Diameter luar pulley dikurangi dedendum gigi |
| **Center Distance ($C$)** | $L \approx 2C + \pi(r_1+r_2) + \frac{(r_2-r_1)^2}{C}$ (Iteratif) | Jarak sumbu presisi belt loop tertutup |
| **Chordal Dip** | $\Delta_{\text{dip}} = r_p - \sqrt{r_p^2 - (w/2)^2}$ | Penurunan bracket akibat lintasan lurus |
| **Ayunan Masuk** | $\delta_{\text{swing}} = h \cdot \left(\frac{w/2}{r_p}\right)$ | Ayunan ujung bracket saat membelok |
| **Kedalaman Rongga** | $d_{\text{slot}} = (h - (r_p - r_o)) + \Delta_{\text{dip}} + c$ | Kedalaman pemotongan U-slot aman |
| **Lebar Rongga** | $w_{\text{slot}} = 2 \cdot (w/2 + \delta_{\text{swing}} + c)$ | Bukaan lebar U-slot aman |

---

## 🛠️ Kebutuhan Sistem & Instalasi

### Prasyarat
Pastikan Anda telah menginstal **Python 3.8** atau versi yang lebih baru di sistem Anda.

### Instalasi Dependensi
Aplikasi ini menggunakan pustaka standar `tkinter` serta pustaka ilmiah `numpy` dan `matplotlib`:

```bash
pip install numpy matplotlib
```

*(Catatan untuk Linux: jika `tkinter` belum terpasang, instal melalui `sudo apt install python3-tk`)*

---

## 🚀 Cara Menjalankan

1. Clone repositori ini atau download source code:
   ```bash
   git clone https://github.com/ReAN25/Calculator-Slotted-Pulley.git
   cd Calculator-Slotted-Pulley
   ```
2. Jalankan aplikasi:
   ```bash
   python slotted_pulley_calculator.py
   ```

---

## 📖 Panduan Penggunaan

1. **Input Parameter Desain**: Masukkan konfigurasi sistem Anda di panel kiri:
   - Pitch Timing Belt (misal: 3 mm untuk GT2 / HTD 3M)
   - Jumlah gigi pulley Driver ($Z_1$) dan Driven ($Z_2$)
   - Jumlah total gigi belt ($Z_b$)
   - Jumlah rongga pada masing-masing pulley
   - Dimensi Bracket: lebar ($b_{\text{width}}$) dan tinggi tonjolan ($b_{\text{height}}$)
   - Clearance tambahan dan diameter poros driver ($D_{\text{shaft}}$)
   - Torsi kerja motor
2. **Update Konfigurasi**: Klik tombol **`Update Konfigurasi & Grafik`**.
3. **Evaluasi Status**: Perhatikan banner indikator pada panel kanan:
   - 🟢 **SINKRON & AMAN**: Geometri dan siklus timing sinkron tanpa tabrakan.
   - 🔴 **TIDAK SINKRON**: Bracket akan menabrak gigi pulley di putaran tertentu.
   - 🟠 **CEK DINDING / JARAK C**: Dinding poros terlalu tipis atau jarak center terlalu mepet.
4. **Analisis Gerak**: Gunakan tombol **Pause / Play** atau geser **Slider Inspeksi Manual** untuk melihat bracket masuk dan keluar rongga pulley secara mendetail.

---

## 📂 Struktur File

```text
Calculator-Slotted-Pulley/
├── slotted_pulley_calculator.py   # Script utama aplikasi GUI & kalkulator
├── README.md                      # Dokumentasi teknis proyek
└── .gitignore                     # Filter file temporary / cache
```

---

## 📄 Lisensi

Proyek ini didistribusikan di bawah lisensi **MIT**. Silakan gunakan, modifikasi, dan kembangkan sesuai kebutuhan riset maupun industri Anda.
