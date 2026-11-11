#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ikon Lucide (aset/ikon, putih 192 px): warnai ke PNG dan pilih otomatis dari kata kunci.

Pemakaian:
  python3 ikon.py --color 1B2A4A --out ikon target users book-open   # warnai ke ikon/<nama>.png
  python3 ikon.py --auto "tujuan penulisan makalah"                  # cetak nama ikon yang cocok
  python3 ikon.py --daftar                                           # semua nama ikon
Lisensi ikon: aset/ikon/LICENSE-lucide.txt (ISC).
"""
import argparse
import json
import os

from PIL import Image

ASET = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aset"))
DIR = os.path.join(ASET, "ikon")


def nama_ikon():
    return sorted(f[:-4] for f in os.listdir(DIR) if f.endswith(".png"))


def auto(teks, bawaan="lightbulb"):
    t = (teks or "").lower()
    terbaik, skor = bawaan, 0
    for nama, kata in json.load(open(os.path.join(ASET, "kata_ikon.json"), encoding="utf-8")):
        s = sum(1 for k in kata.split() if k in t)
        if s > skor:
            terbaik, skor = nama, s
    return terbaik


def warnai(nama, hex6, out):
    src = Image.open(os.path.join(DIR, nama + ".png")).convert("RGBA")
    warna = tuple(int(hex6[i:i + 2], 16) for i in (0, 2, 4))
    hasil = Image.new("RGBA", src.size, warna + (0,))
    hasil.putalpha(src.getchannel("A"))
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, nama + ".png")
    hasil.save(path)
    return path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("nama", nargs="*")
    p.add_argument("--color", default="1B2A4A")
    p.add_argument("--out", default="ikon")
    p.add_argument("--auto")
    p.add_argument("--daftar", action="store_true")
    a = p.parse_args()
    if a.daftar:
        print(" ".join(nama_ikon()))
    elif a.auto is not None:
        print(auto(a.auto))
    else:
        ada = set(nama_ikon())
        for n in a.nama:
            if n not in ada:
                raise SystemExit(f"Ikon '{n}' tidak ada. Lihat --daftar.")
            print(warnai(n, a.color.lstrip("#"), a.out))
