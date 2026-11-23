"""
Mesin Fuzzy - Sistem Peringatan Dini Banjir Rob Pesisir Semarang
Fuzzy Mamdani (utama) dan Fuzzy Sugeno orde-0 (pembanding)

Tugas Kelompok 01 - Komputasi Lunak, Informatika Universitas Diponegoro

File ini dijalankan di browser oleh Pyodide (Python versi WebAssembly).
Logikanya sama dengan notebook Colab: fungsi keanggotaan, 27 rule,
operator min-max, dan defuzzifikasi centroid.
"""
import json

# ---------------------------------------------------------------------------
# 1. Himpunan fuzzy: 3 angka = segitiga, 4 angka = trapesium
# ---------------------------------------------------------------------------
PARAM = {
    'pasang': {'rendah': [0, 0, 120, 160], 'sedang': [120, 160, 200], 'tinggi': [160, 200, 250, 250]},
    'hujan': {'ringan': [0, 0, 20, 35], 'sedang': [20, 35, 50], 'lebat': [35, 50, 200, 200]},
    'angin': {'lemah': [0, 0, 12, 20], 'sedang': [12, 24, 39], 'kencang': [29, 39, 60, 60]},
    'siaga': {'aman': [0, 0, 15, 35], 'waspada': [15, 35, 55], 'siaga': [45, 65, 85], 'awas': [65, 85, 100, 100]},
}
SEMESTA = {'pasang': (0, 250), 'hujan': (0, 200), 'angin': (0, 60), 'siaga': (0, 100)}


def mf(x, p):
    """Derajat keanggotaan x pada himpunan dengan parameter p."""
    if len(p) == 3:
        p = [p[0], p[1], p[1], p[2]]
    a, b, c, d = p
    if x < a or x > d:
        return 0.0
    if x < b:
        return (x - a) / (b - a)
    if x <= c:
        return 1.0
    return (d - x) / (d - c)


def fuzzifikasi(pasang, hujan, angin):
    nilai = {'pasang': pasang, 'hujan': hujan, 'angin': angin}
    return {var: {h: mf(nilai[var], p) for h, p in PARAM[var].items()} for var in nilai}


# ---------------------------------------------------------------------------
# 2. Rule base: (pasang, hujan, angin, output)
# ---------------------------------------------------------------------------
RULES = [
    ('rendah', 'ringan', 'lemah', 'aman'), ('rendah', 'ringan', 'sedang', 'aman'), ('rendah', 'ringan', 'kencang', 'aman'),
    ('rendah', 'sedang', 'lemah', 'aman'), ('rendah', 'sedang', 'sedang', 'waspada'), ('rendah', 'sedang', 'kencang', 'waspada'),
    ('rendah', 'lebat', 'lemah', 'waspada'), ('rendah', 'lebat', 'sedang', 'waspada'), ('rendah', 'lebat', 'kencang', 'waspada'),
    ('sedang', 'ringan', 'lemah', 'waspada'), ('sedang', 'ringan', 'sedang', 'waspada'), ('sedang', 'ringan', 'kencang', 'siaga'),
    ('sedang', 'sedang', 'lemah', 'waspada'), ('sedang', 'sedang', 'sedang', 'siaga'), ('sedang', 'sedang', 'kencang', 'siaga'),
    ('sedang', 'lebat', 'lemah', 'siaga'), ('sedang', 'lebat', 'sedang', 'siaga'), ('sedang', 'lebat', 'kencang', 'awas'),
    ('tinggi', 'ringan', 'lemah', 'siaga'), ('tinggi', 'ringan', 'sedang', 'awas'), ('tinggi', 'ringan', 'kencang', 'awas'),
    ('tinggi', 'sedang', 'lemah', 'awas'), ('tinggi', 'sedang', 'sedang', 'awas'), ('tinggi', 'sedang', 'kencang', 'awas'),
    ('tinggi', 'lebat', 'lemah', 'awas'), ('tinggi', 'lebat', 'sedang', 'awas'), ('tinggi', 'lebat', 'kencang', 'awas'),
]
Z_SUGENO = {'aman': 10, 'waspada': 35, 'siaga': 65, 'awas': 90}

# Semesta output dibagi tiap 0,1 (1.001 titik), sama dengan notebook
Y = [i / 10 for i in range(1001)]
MF_OUT = {nama: [mf(z, p) for z in Y] for nama, p in PARAM['siaga'].items()}


def evaluasi_rule(mu):
    """Kekuatan tiap rule: alpha = min(mu pasang, mu hujan, mu angin)."""
    return [min(mu['pasang'][tp], mu['hujan'][th], mu['angin'][ta]) for tp, th, ta, _ in RULES]


def centroid(xs, ys):
    """Centroid eksak kurva linear sepotong-sepotong (sama dengan skfuzzy)."""
    luas = momen = 0.0
    for i in range(1, len(xs)):
        x1, x2, y1, y2 = xs[i - 1], xs[i], ys[i - 1], ys[i]
        dx = x2 - x1
        luas += dx * (y1 + y2) / 2
        momen += dx * (x1 * (2 * y1 + y2) + x2 * (y1 + 2 * y2)) / 6
    return momen / luas if luas > 0 else 0.0


def kategori(z):
    return 'Aman' if z < 25 else 'Waspada' if z < 50 else 'Siaga' if z < 75 else 'Awas'


def hitung(pasang, hujan, angin):
    """Seluruh proses inferensi untuk satu set input."""
    mu = fuzzifikasi(pasang, hujan, angin)
    alphas = evaluasi_rule(mu)

    # Mamdani: implikasi min, agregasi max (rule berkonsekuen sama digabung max)
    alpha_out = {k: 0.0 for k in Z_SUGENO}
    for (_, _, _, out), al in zip(RULES, alphas):
        alpha_out[out] = max(alpha_out[out], al)
    agregasi = [max(min(alpha_out[k], MF_OUT[k][i]) for k in alpha_out) for i in range(len(Y))]
    z_m = centroid(Y, agregasi)

    # Sugeno orde-0: rata-rata terbobot semua rule
    total = sum(alphas)
    z_s = sum(al * Z_SUGENO[out] for (_, _, _, out), al in zip(RULES, alphas)) / total if total else 0.0

    aktif = [{'no': i + 1, 'pasang': r[0], 'hujan': r[1], 'angin': r[2], 'output': r[3], 'alpha': al}
             for i, (r, al) in enumerate(zip(RULES, alphas)) if al > 0]
    return {
        'mu': mu,
        'alpha': alphas,
        'alpha_out': alpha_out,
        'aktif': aktif,
        'agregasi': agregasi[::5],          # 201 titik untuk grafik
        'mamdani': z_m, 'kat_mamdani': kategori(z_m),
        'sugeno': z_s, 'kat_sugeno': kategori(z_s),
    }


def hitung_json(pasang, hujan, angin):
    return json.dumps(hitung(pasang, hujan, angin))


def model_json():
    """Data model untuk tampilan: parameter, rule, dan kurva fungsi keanggotaan."""
    kurva = {}
    for var, (lo, hi) in SEMESTA.items():
        xs = [lo + (hi - lo) * i / 250 for i in range(251)]
        kurva[var] = {'x': xs, 'y': {h: [mf(x, p) for x in xs] for h, p in PARAM[var].items()}}
    return json.dumps({'param': PARAM, 'rules': RULES, 'sugeno': Z_SUGENO, 'kurva': kurva})
