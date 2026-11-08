#!/usr/bin/env python3
"""Satu pintu gaya visual: tema (30 pilihan) atau warna polos -> JSON gaya.

Pemakaian:
  python3 gaya.py --tema=batik                 # nama, nomor (13), atau kunci
  python3 gaya.py --tema=rekomendasi --topik "matematika diskrit kombinasi"
  python3 gaya.py "--warna=#7A1F5C"            # polos, tanpa gambar latar
  python3 gaya.py --warna=hijau --fontaman
  python3 gaya.py --daftar                      # daftar 30 tema

Keluaran: JSON dengan bg, card, ink, muted, judul, utama, aksen, teks_di_utama,
font_judul, font_isi, font_arab, radius, latar, poster (path gambar atau null), seri.
Tema memakai gambar latar (aset/latar, aset/poster); --warna polos tidak.
Jika --tema dan --warna sama-sama ada, tema yang dipakai dan ada catatan di keluaran.
"""
import colorsys
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import palette  # noqa: E402

ASET = os.path.normpath(os.path.join(HERE, "..", "aset"))
TEMA = json.load(open(os.path.join(ASET, "tema.json"), encoding="utf-8"))

# Kata kunci topik -> tema (yang pertama dalam daftar dipilih). Urutan aturan = prioritas.
REKOMENDASI = [
    (("kriptografi", "keamanan siber", "pemrograman", "informatika", "kecerdasan buatan", "algoritma"), "cyberpunk"),
    (("matematika", "kombinatorik", "statistik", "aljabar", "kalkulus", "diskrit", "pendidikan", "keguruan"), "papantulis"),
    (("data", "sistem informasi", "jaringan komputer", "basis data"), "jaringan"),
    (("teknik", "arsitektur", "desain produk", "mesin", "sipil"), "blueprint"),
    (("kesehatan", "kedokteran", "keperawatan", "farmasi", "biologi", "gizi"), "medis"),
    (("lingkungan", "pertanian", "pangan", "agribisnis"), "natural"),
    (("kehutanan", "konservasi", "hutan"), "forest"),
    (("kelautan", "perikanan", "air", "laut"), "samudra"),
    (("iklim", "geografi", "kebencanaan", "cuaca"), "salju"),
    (("pariwisata", "pesisir", "wisata"), "tropis"),
    (("astronomi", "fisika", "sains", "antariksa"), "galaksi"),
    (("bisnis", "manajemen", "ekonomi", "akuntansi", "keuangan"), "korporat"),
    (("islam", "syariah", "agama", "fikih", "tafsir"), "islami"),
    (("budaya", "adat", "tradisional", "bahasa daerah", "nusantara"), "batik"),
    (("sejarah", "sastra", "arsip", "filologi"), "vintage"),
    (("seni", "desain grafis", "dkv", "kreatif"), "bauhaus"),
    (("psikologi", "anak", "paud", "kesejahteraan", "sosial"), "pastel"),
    (("jepang", "asia", "puisi"), "sakura"),
    (("hukum", "kebijakan", "karya ilmiah", "skripsi", "tesis"), "minimalis"),
    (("game", "multimedia", "hiburan"), "pixel"),
]


def rekomendasikan(topik):
    t = (topik or "").lower()
    for kata, kunci in REKOMENDASI:
        if any(k in t for k in kata):
            return kunci
    return "modern"


def cari_tema(nilai):
    n = nilai.strip().lower().replace(" ", "")
    for t in TEMA:
        if n in (str(t["no"]), t["kunci"], t["nama"].lower().replace(" ", "")):
            return t
    raise SystemExit(f"Tema '{nilai}' tidak dikenali. Jalankan: python3 gaya.py --daftar")


def _lebih_terang(hex6, f):
    r, g, b = (int(hex6[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = l + (1 - l) * f
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def dari_tema(t, fontaman, topik=None):
    aman = "Calibri"
    return {
        "mode": "tema", "kunci": t["kunci"], "nama": t["nama"], "dark": t["dark"],
        "bg": t["bg"], "card": t["card"], "ink": t["ink"], "muted": t["muted"],
        "judul": t["judul"], "utama": t["a1"], "aksen": t["a1"],
        "teks_di_utama": t["teks_di_utama"],
        "font_judul": aman if fontaman else t["head"], "font_isi": aman,
        "font_arab": "Traditional Arabic" if fontaman else "Amiri",
        "radius": t["radius"], "garis": t["garis"],
        "latar": os.path.join(ASET, "latar", t["kunci"] + ".jpg"),
        "poster": os.path.join(ASET, "poster", t["kunci"] + ".jpg"),
        "seri": [t["a1"], t["a2"], t["a3"], t["a4"]],
    }


def dari_warna(arg, fontaman):
    p = palette.resolve([arg])
    u = p["utama"]
    hasil = {
        "mode": "polos", "kunci": "polos", "nama": p["nama"], "dark": False,
        "bg": p["bg"], "card": "FFFBF2", "ink": u, "muted": u, "judul": u,
        "utama": u, "aksen": p["aksen"], "teks_di_utama": p["teks_di_utama"],
        "font_judul": "Calibri" if fontaman else "Poppins",
        "font_isi": "Calibri" if fontaman else "Lato",
        "font_arab": "Traditional Arabic" if fontaman else "Amiri",
        "radius": 0.08, "garis": u, "latar": None, "poster": None,
        "seri": [u, _lebih_terang(u, .35), p["aksen"] if p["aksen"] != u else "B08D3C", _lebih_terang(u, .6)],
    }
    if "catatan" in p:
        hasil["catatan"] = p["catatan"]
    return hasil


def main(argv):
    if "--daftar" in argv:
        for t in TEMA:
            print(f'{t["no"]:>2}. {t["nama"]} ({t["kunci"]}) - {t["nuansa"]} | {t["cocok_untuk"]}')
        return
    fontaman = "--fontaman" in argv
    topik = None
    tema = warna = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--tema="):
            tema = a.split("=", 1)[1]
        elif a == "--tema" and i + 1 < len(argv):
            i += 1
            tema = argv[i]
        elif a.startswith("--topik="):
            topik = a.split("=", 1)[1]
        elif a == "--topik" and i + 1 < len(argv):
            i += 1
            topik = argv[i]
        elif a.startswith("--warna=") or a.lstrip("-").lower() in palette.PALET:
            warna = a
        i += 1
    if tema:
        if tema.lower() in ("rekomendasi", "rekom", "0"):
            kunci = rekomendasikan(topik)
            hasil = dari_tema(cari_tema(kunci), fontaman)
            hasil["catatan"] = f"Tema direkomendasikan dari topik: {hasil['nama']}"
        else:
            hasil = dari_tema(cari_tema(tema), fontaman)
        if warna:
            hasil["catatan"] = "--tema dan --warna sama-sama ada; --tema dipakai, --warna diabaikan"
    elif warna:
        hasil = dari_warna(warna, fontaman)
    else:
        raise SystemExit("Beri --tema=<nama|nomor|rekomendasi> atau --warna=<nama|hex>. Lihat --daftar.")
    print(json.dumps(hasil, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
