#!/usr/bin/env python3
"""Render rumus matematika ke PNG transparan untuk ditempel di slide.

Pemakaian:
  python3 render_rumus.py --color 1B2A4A --size 32 --out rumus1.png "C(n,r)=\\frac{n!}{r!(n-r)!}"

Teks rumus memakai sintaks mathtext matplotlib (subset LaTeX): \\frac, \\binom, \\sum,
\\sqrt, pangkat ^ dan indeks _ didukung (sudah dites: \\frac, \\binom, \\sqrt, {}_{n}C_{r}).
Perintah yang tidak dikenal akan menimbulkan galat; sederhanakan rumusnya bila itu terjadi.
Rumus sederhana (satu baris, tanpa pecahan atau akar) lebih baik ditulis sebagai teks biasa di slide.
"""
import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("rumus")
    p.add_argument("--color", default="1B2A4A")
    p.add_argument("--size", type=int, default=32, help="ukuran huruf (pt)")
    p.add_argument("--out", default="rumus.png")
    a = p.parse_args()

    teks = a.rumus.strip()
    if not (teks.startswith("$") and teks.endswith("$")):
        teks = f"${teks}$"

    plt.rcParams["mathtext.fontset"] = "dejavusans"
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, teks, fontsize=a.size, color="#" + a.color.lstrip("#"))
    fig.savefig(a.out, dpi=300, transparent=True, bbox_inches="tight", pad_inches=0.08)
    print(f"OK {a.out}")


if __name__ == "__main__":
    main()
