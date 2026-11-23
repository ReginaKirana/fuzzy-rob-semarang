# Sistem Peringatan Dini Banjir Rob Semarang

Model **fuzzy Mamdani** untuk menentukan level siaga banjir rob di pesisir Semarang (kawasan Tanjung Emas) berdasarkan tinggi pasang air laut, curah hujan, dan kecepatan angin dari laut. Fuzzy Sugeno orde-0 dipakai sebagai pembanding.

Proyek ini dibuat untuk Tugas Kelompok 01 mata kuliah Komputasi Lunak, Program Studi Informatika, Universitas Diponegoro.

- **GUI web:** [link GUI]
- **Google Colab:** [link Colab]

## Model

| Variabel | Satuan | Himpunan fuzzy | Dasar batas |
|---|---|---|---|
| Tinggi pasang (input) | cm | Rendah, Sedang, Tinggi | Pasang harian ±148 cm, tanggul 2 m, rob Mei 2022 = 210 cm |
| Curah hujan (input) | mm/hari | Ringan, Sedang, Lebat | Kategori hujan BMKG |
| Kecepatan angin (input) | km/jam | Lemah, Sedang, Kencang | Skala Beaufort |
| Level siaga (output) | skor 0–100 | Aman, Waspada, Siaga, Awas | Batas kategori 25, 50, 75 |

- **Rule base:** 27 rule (3 × 3 × 3)
- **Mamdani:** AND = min, implikasi = min, agregasi = max, defuzzifikasi centroid
- **Sugeno orde-0:** rule yang sama, konstanta Aman 10, Waspada 35, Siaga 65, Awas 90, rata-rata terbobot

## Contoh hasil

| Skenario | Pasang (cm) | Hujan (mm/hari) | Angin (km/jam) | Mamdani | Sugeno |
|---|---|---|---|---|---|
| Normal | 100 | 5 | 10 | 13,17 (Aman) | 10,00 (Aman) |
| Skenario A | 110 | 45 | 15 | 28,25 (Waspada) | 29,29 (Waspada) |
| Skenario B | 150 | 40 | 22 | 55,36 (Siaga) | 55,00 (Siaga) |
| Rob Mei 2022* | 210 | 10 | 25 | 86,60 (Awas) | 90,00 (Awas) |

\*Hanya tinggi pasang 210 cm yang merupakan data nyata; hujan dan angin adalah asumsi.

## Isi repository

| File | Keterangan |
|---|---|
| `index.html` | Tampilan GUI web: dashboard, ilustrasi pesisir, rule base, dan penjelasan model |
| `fuzzy_engine.py` | Mesin fuzzy Python (fungsi keanggotaan, 27 rule, Mamdani, Sugeno) yang dijalankan di browser dengan Pyodide |
| `fuzzy_rob_semarang.ipynb` | Notebook Google Colab: perhitungan, tabel skenario, dan grafik untuk laporan |

## Cara menjalankan

**GUI web:** buka tautan GUI di atas. Pembukaan pertama butuh beberapa detik untuk memuat Python di browser.

**GUI di komputer sendiri:** `index.html` harus dibuka lewat server lokal, bukan diklik langsung, karena halaman perlu memuat `fuzzy_engine.py`.

```bash
python -m http.server 8000
```

Lalu buka `http://localhost:8000` di browser. Koneksi internet tetap dibutuhkan untuk memuat Pyodide.

**Notebook:** buka di Google Colab, lalu pilih **Runtime → Run all**.

## Kelompok

- Regina
- Hidah
- Yelisa

## Catatan

Data yang digunakan bersifat simulasi untuk keperluan tugas kuliah. Sistem ini bukan peringatan resmi; untuk informasi resmi, ikuti BMKG dan BPBD Kota Semarang.
