# Simple_Wave_Game
Simple Wave Game — Game arcade berbasis Python & Pygame terinspirasi dari mode Wave di Geometry Dash. Hindari rintangan segitiga dengan menahan/melepas klik mouse, bertahan selama mungkin, dan raih skor tertinggi di leaderboard lokal.

## Cara Install & Menjalankan

### 1. Pastikan Python sudah terinstall
Buka terminal / command prompt, ketik:
```
python --version
```
Harus muncul **Python 3.7** ke atas.

### 2. Install Pygame
```
pip install pygame
```

### 3. Jalankan game
Letakkan file `wave_game.py` di folder mana saja, lalu:
```
python wave_game.py
```

---

## Kontrol

| Tombol / Aksi | Fungsi |
|---|---|
| **Tahan klik kiri** | Player naik |
| **Lepas klik** | Player turun |
| **SPACE** (tahan) | Player naik (alternatif mouse) |
| **P** | Pause / Resume |
| **ESC** | Keluar ke game over |
| **M** (di game over) | Kembali ke menu |
| **ENTER** (di menu) | Mulai game |
| **Backspace** (di menu) | Hapus huruf nama |

---

## Cara Bermain

1. Di **menu utama**, ketik nama kamu (maks 8 karakter), lalu tekan **ENTER**
2. Game langsung mulai — hindari segitiga merah atas dan bawah
3. Celah di tengah adalah jalur aman — arahkan player melewatinya
4. Semakin lama bertahan, semakin cepat dan sempit rintangannya
5. Setelah mati, lihat **ranking** kamu di leaderboard

---

## Sistem Skor

| Sumber | Poin |
|---|---|
| Per frame bertahan hidup | +0.025 |
| Berhasil melewati 1 rintangan | +5 |

Skor tersimpan otomatis di file `scores.json` (dibuat otomatis).

---

## Difficulty Scaling

Game makin sulit secara otomatis:

| Parameter | Awal | Maksimum |
|---|---|---|
| Kecepatan rintangan | 6.0 | ~14+ |
| Kecepatan naik/turun | 5.5 | ~11+ |
| Lebar celah | 175px | 85px (minimum) |

---

## Perbaikan dari Versi Lama

| Aspek | Versi Lama | Versi Baru |
|---|---|---|
| Collision | AABB kotak (tidak akurat) | Polygon-based (akurat) |
| Scoring | Bug: bonus hampir tidak pernah masuk | +5 per rintangan yang dilewati |
| Trail | Semua titik satu warna | Gradasi cyan → gelap |
| High score | 1 angka di .txt | Top-10 leaderboard + nama di JSON |
| Menu | Tidak ada | Menu utama + input nama |
| Pause | Tidak ada | Tombol P |
| Efek visual | Tidak ada | Particle explosion saat mati |
| Sorting | Trail (tidak berguna) | Insertion sort leaderboard |
| Searching | AABB sederhana | Binary search untuk rank |
| Konstanta | Tersebar di kode | Terpusat di bagian atas |

---

## Struktur File

```
folder_game/
├── wave_game.py     ← file utama
└── scores.json      ← dibuat otomatis saat pertama main
```

---

## Troubleshooting

**"No module named pygame"**
→ Jalankan: `pip install pygame`

**Game terasa lambat**
→ Pastikan tidak ada program berat lain yang berjalan

**File scores.json rusak**
→ Hapus file tersebut, akan dibuat ulang otomatis
