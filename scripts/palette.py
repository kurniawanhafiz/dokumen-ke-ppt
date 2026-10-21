#!/usr/bin/env python3
"""Ubah flag warna jadi palet PPT (JSON) dan pastikan kontrasnya aman.

Pemakaian:
  python3 palette.py --hijau
  python3 palette.py --navy
  python3 palette.py "--warna=#7A1F5C"
  python3 palette.py "--warna=ungu"

Keluaran: JSON berisi bg, utama, aksen, teks_di_utama, orb_transparansi.
Palet bawaan: hijau, navy, marun, teal, cokelat, hitam.
Warna sendiri lewat --warna=<hex atau nama>. Jika terlalu terang, warna
digelapkan otomatis sampai kontras terhadap latar krem minimal 4.5.
"""
import colorsys
import json
import sys

KREM = "F5EFE0"

PALET = {
    "hijau": {"utama": "1E4D3B", "aksen": "1E4D3B"},
    "navy": {"utama": "1B2A4A", "aksen": "1B2A4A"},
    "marun": {"utama": "6B1E2E", "aksen": "6B1E2E"},
    "teal": {"utama": "134E4A", "aksen": "134E4A"},
    "cokelat": {"utama": "4A2F1F", "aksen": "4A2F1F"},
    # hitam: satu-satunya palet dengan aksen berbeda (emas tipis, hanya untuk garis judul)
    "hitam": {"utama": "1C1C1E", "aksen": "B08D3C"},
}

# Nama warna umum untuk --warna=<nama>. Nama lain: pilih hex sendiri lalu pakai --warna=#hex.
NAMA_WARNA = {
    "ungu": "4B2E6F",
    "merah": "8E1B1B",
    "biru": "1E4E8C",
    "oranye": "A8531A",
    "abu": "3A3F47",
    "pink": "9C3D5C",
    "kuning": "8A6D12",
}


def _luminance(hex6):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex6[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def kontras(a, b):
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def gelapkan_sampai_aman(hex6, target=4.5):
    r, g, b = (int(hex6[i : i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    while kontras(hex6, KREM) < target and l > 0.05:
        l -= 0.02
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        hex6 = "%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))
    return hex6


def _hex_valid(teks):
    t = teks.lstrip("#").upper()
    if len(t) == 3:
        t = "".join(c * 2 for c in t)
    if len(t) == 6 and all(c in "0123456789ABCDEF" for c in t):
        return t
    return None


def resolve(argumen):
    for a in argumen:
        if a.startswith("--warna="):
            nilai = a.split("=", 1)[1].strip()
            hex6 = _hex_valid(nilai) or NAMA_WARNA.get(nilai.lower())
            if not hex6:
                raise SystemExit(
                    f"Warna '{nilai}' tidak dikenali. Pilih hex sendiri dan pakai --warna=#RRGGBB."
                )
            asli = hex6.upper()
            aman = gelapkan_sampai_aman(asli)
            hasil = {"nama": "kustom", "utama": aman, "aksen": aman}
            if aman != asli:
                hasil["catatan"] = f"{asli} digelapkan jadi {aman} agar kontras terhadap krem minimal 4.5"
            break
        nama = a.lstrip("-").lower()
        if nama in PALET:
            hasil = {"nama": nama, **PALET[nama]}
            break
    else:
        raise SystemExit(
            "Tidak ada flag warna. Pilihan: " + ", ".join("--" + n for n in PALET) + ", --warna=<hex atau nama>"
        )
    hasil.update(
        bg=KREM,
        teks_di_utama=KREM,
        orb_transparansi=90,
        kontras_utama_vs_krem=round(kontras(hasil["utama"], KREM), 2),
    )
    return hasil


if __name__ == "__main__":
    print(json.dumps(resolve(sys.argv[1:]), indent=2, ensure_ascii=False))
