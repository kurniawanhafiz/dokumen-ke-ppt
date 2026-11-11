#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Baca dokumen sumber (.docx, .pdf, .md, .txt) dan siapkan bahan untuk isi.json.

Pemakaian:
  python3 baca_sumber.py makalah.docx
  python3 baca_sumber.py laporan.pdf --keluar=kerja --halaman=7     # ikut render halaman 7 (untuk diagram)
  python3 baca_sumber.py makalah.docx --tanpa-logo --maks-gambar=6

Keluaran di folder --keluar (bawaan ./sumber_kerja):
  sumber.txt       teks bersih tanpa daftar pustaka dan titik-titik daftar isi (rumus Word jadi LaTeX bila ada pandoc)
  pustaka.txt      daftar pustaka yang dipisahkan (untuk --pustaka dan pengecekan sitasi), jika ditemukan
  logo.png         logo di cover (.docx hasil makalah-unri; .pdf halaman 1) dengan latar transparan, jika ada
  _gambar/         gambar isi (.docx) atau halaman yang diminta (--halaman), maksimal --maks-gambar
  ringkasan.json   ringkasan yang juga dicetak: panjang, bab terdeteksi, awal dokumen (cover), rumus,
                   placeholder template, gambar beserta tebakan keterangan, dan apakah OCR dipakai

Setelah ini Claude membaca sumber.txt (Read, per bagian jika panjang), bukan membaca ulang berkas aslinya.
Tidak ada yang diunggah ke mana pun; semua diproses lokal dengan pandoc, poppler, dan tesseract jika terpasang.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

REGEX_PUSTAKA = re.compile(r"^[ \t]*(?:#+[ \t]*)?(?:\*\*)?(DAFTAR[ \t]+PUSTAKA|DAFTAR[ \t]+REFERENSI|REFERENSI|REFERENCES|BIBLIOGRAPHY)(?:\*\*)?[ \t]*$", re.I | re.M)
REGEX_BAB = re.compile(r"^[ \t]*(?:#+[ \t]*)?(?:\*\*)?(BAB[ \t]+[IVXLC\d]+\b.*|KATA[ \t]+PENGANTAR|DAFTAR[ \t]+ISI|PENDAHULUAN|PEMBAHASAN|PENUTUP|KESIMPULAN|ABSTRAK|ABSTRACT)(?:\*\*)?[ \t]*$", re.I | re.M)
REGEX_TEMPLATE = re.compile(r"\[(?:Tuliskan|Isi|Masukkan|Ketik|Write|Insert|Enter)[^\]\n]{0,80}\]", re.I)
BATAS_COVER = re.compile(r"^\s*(KATA\s+PENGANTAR|DAFTAR\s+ISI|BAB\s+I\b|ABSTRAK|ABSTRACT|PENDAHULUAN)", re.I)
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def jalankan(cmd, **kw):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=kw.pop("timeout", 300), **kw)
    except (OSError, subprocess.TimeoutExpired) as e:
        return subprocess.CompletedProcess(cmd, 127, "", str(e))


def ada(prog):
    return shutil.which(prog) is not None


# ---------------------------------------------------------------- pembersihan
def bersihkan(teks, pdf=False, markdown=False):
    if markdown:  # keluaran pandoc: gambar jadi penanda, tanda escape markdown dibuang (kecuali $)
        teks = re.sub(r"!\[[^\]]*\]\([^)]*\)(?:\{[^}]*\})?", "[gambar]", teks)
        teks = re.sub(r"\\([\[\]*_#<>~\"'\-.!()&|])", r"\1", teks)
    teks = teks.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n\n").replace(" ", " ")
    if pdf:
        teks = re.sub(r"(\w)-\n(\w)", r"\1\2", teks)            # kata terpotong di akhir baris
        teks = re.sub(r"(?m)^[ \t]*\d{1,3}[ \t]*$", "", teks)    # nomor halaman berdiri sendiri
    teks = re.sub(r"(?m)^.*\.{4,}[ \t]*\d+[ \t]*$", "", teks)    # baris daftar isi bertitik-titik
    teks = re.sub(r"[ \t]+\n", "\n", teks)
    teks = re.sub(r"\n{3,}", "\n\n", teks)
    return teks.strip() + "\n"


def pisah_pustaka(teks):
    """Potong dari judul daftar pustaka terakhir yang berada di paruh akhir dokumen."""
    cocok = [m for m in REGEX_PUSTAKA.finditer(teks) if m.start() > len(teks) * 0.3]
    if not cocok:
        return teks, ""
    m = cocok[-1]
    return teks[:m.start()].rstrip() + "\n", teks[m.start():].strip() + "\n"


# ---------------------------------------------------------------- docx
def teks_docx_xml(z):
    """Cadangan tanpa pandoc: ambil teks per paragraf; rumus OMML ditulis sebagai teksnya saja."""
    from xml.etree import ElementTree as ET
    akar = ET.fromstring(z.read("word/document.xml"))
    baris = []
    for p in akar.iter(W + "p"):
        t = "".join(x.text or "" for x in p.iter() if x.tag in (W + "t", "{http://schemas.openxmlformats.org/officeDocument/2006/math}t"))
        baris.append(t.strip())
    return "\n".join(baris)


def teks_docx(path, z):
    if ada("pandoc"):
        r = jalankan(["pandoc", path, "-t", "markdown", "--wrap=none", "--markdown-headings=atx"])
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout, "pandoc"
    return teks_docx_xml(z), "xml"


def gambar_docx(z, outdir, maks, tanpa_logo):
    """Urutan gambar sesuai kemunculan di dokumen. Gambar sebelum 'KATA PENGANTAR' dianggap cover (logo)."""
    from xml.etree import ElementTree as ET
    rels = {}
    if "word/_rels/document.xml.rels" in z.namelist():
        for r in ET.fromstring(z.read("word/_rels/document.xml.rels")):
            rels[r.get("Id")] = r.get("Target")
    akar = ET.fromstring(z.read("word/document.xml"))
    R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    paragraf = list(akar.iter(W + "p"))
    cover, isi, selesai_cover = [], [], False
    for k, p in enumerate(paragraf):
        t = "".join(x.text or "" for x in p.iter(W + "t")).strip()
        if not selesai_cover and BATAS_COVER.match(t):
            selesai_cover = True
        for e in p.iter():
            rid = e.get(R + "embed")
            if rid and rid in rels and rels[rid].startswith("media/"):
                # tebakan keterangan: paragraf berikutnya (atau ini) yang diawali 'Gambar'
                ket = ""
                for q in paragraf[k:k + 3]:
                    tq = "".join(x.text or "" for x in q.iter(W + "t")).strip()
                    if re.match(r"(?i)^(gambar|figure|diagram|bagan)\b", tq):
                        ket = tq
                        break
                (isi if selesai_cover else cover).append(("word/" + rels[rid], ket))
    from PIL import Image
    import io
    hasil = {"logo": None, "gambar": []}
    if cover and not tanpa_logo:
        try:
            im = Image.open(io.BytesIO(z.read(cover[0][0]))).convert("RGBA")
            im.save(os.path.join(outdir, "logo.png"))
            hasil["logo"] = {"file": "logo.png", "ukuran": list(im.size), "dari": cover[0][0]}
        except Exception as e:  # gambar format aneh (emf/wmf)
            hasil["logo_catatan"] = f"gambar cover tidak bisa dibuka ({e})"
    dipakai = set()
    os.makedirs(os.path.join(outdir, "_gambar"), exist_ok=True)
    for nama, ket in isi:
        if nama in dipakai or len(hasil["gambar"]) >= maks:
            continue
        dipakai.add(nama)
        data = z.read(nama)
        ext = os.path.splitext(nama)[1].lower()
        if len(data) < 4000:  # ikon, garis, dekorasi
            continue
        if ext in (".emf", ".wmf", ".tif", ".tiff"):
            hasil.setdefault("gambar_dilewati", []).append(f"{nama} (format {ext} perlu dikonversi manual)")
            continue
        tujuan = f"_gambar/gambar{len(hasil['gambar']) + 1}{ext}"
        open(os.path.join(outdir, tujuan), "wb").write(data)
        try:
            ukuran = list(Image.open(os.path.join(outdir, tujuan)).size)
        except Exception:
            ukuran = None
        hasil["gambar"].append({"file": tujuan, "ukuran": ukuran, "keterangan": ket})
    return hasil


# ---------------------------------------------------------------- pdf
def ocr_pdf(path, outdir):
    if not ada("pdftoppm") or not ada("tesseract"):
        return None, "OCR tidak tersedia (butuh pdftoppm dan tesseract). Minta .docx atau teks dari pengguna."
    langs = jalankan(["tesseract", "--list-langs"]).stdout
    bahasa = "ind+eng" if "ind" in langs.split() else "eng"
    tmp = os.path.join(outdir, "_ocr")
    os.makedirs(tmp, exist_ok=True)
    jalankan(["pdftoppm", "-r", "300", "-png", path, os.path.join(tmp, "p")], timeout=900)
    bagian = []
    for f in sorted(os.listdir(tmp)):
        if f.endswith(".png"):
            bagian.append(jalankan(["tesseract", os.path.join(tmp, f), "-", "-l", bahasa], timeout=300).stdout)
    shutil.rmtree(tmp, ignore_errors=True)
    return "\f".join(bagian), bahasa


def logo_pdf(path, outdir):
    """Logo dari halaman 1; gambar mask (smask) yang menyertai jadi kanal alpha."""
    if not ada("pdfimages"):
        return None
    daftar = jalankan(["pdfimages", "-list", "-f", "1", "-l", "1", path]).stdout.splitlines()[2:]
    baris = [b.split() for b in daftar if b.strip()]
    if not baris:
        return None
    tmp = os.path.join(outdir, "_pi")
    os.makedirs(tmp, exist_ok=True)
    jalankan(["pdfimages", "-png", "-f", "1", "-l", "1", path, os.path.join(tmp, "i")])
    from PIL import Image
    berkas = sorted(f for f in os.listdir(tmp) if f.endswith(".png"))
    hasil = None
    for k, b in enumerate(baris):
        if len(b) > 4 and b[2] == "image" and k < len(berkas):
            if int(b[3]) < 60 or int(b[4]) < 60:
                continue
            im = Image.open(os.path.join(tmp, berkas[k])).convert("RGB")
            if k + 1 < len(baris) and baris[k + 1][2] == "smask" and k + 1 < len(berkas):
                m = Image.open(os.path.join(tmp, berkas[k + 1])).convert("L")
                if m.size != im.size:
                    m = m.resize(im.size)
                im.putalpha(m)
            else:
                im = im.convert("RGBA")
            im.save(os.path.join(outdir, "logo.png"))
            hasil = {"file": "logo.png", "ukuran": list(im.size), "dari": "pdf halaman 1"}
            break
    shutil.rmtree(tmp, ignore_errors=True)
    return hasil


def render_halaman(path, n, outdir):
    os.makedirs(os.path.join(outdir, "_gambar"), exist_ok=True)
    jalankan(["pdftoppm", "-r", "200", "-png", "-f", str(n), "-l", str(n), path, os.path.join(outdir, "_gambar", f"halaman-{n}")])
    f = [x for x in os.listdir(os.path.join(outdir, "_gambar")) if x.startswith(f"halaman-{n}")]
    return f"_gambar/{f[0]}" if f else None


# ---------------------------------------------------------------- utama
def main(argv):
    pos, o = [], {"keluar": "sumber_kerja", "halaman": None, "maks_gambar": 12, "tanpa_logo": False}
    for a in argv:
        if a.startswith("--keluar="):
            o["keluar"] = a.split("=", 1)[1]
        elif a.startswith("--halaman="):
            o["halaman"] = int(a.split("=", 1)[1])
        elif a.startswith("--maks-gambar="):
            o["maks_gambar"] = int(a.split("=", 1)[1])
        elif a == "--tanpa-logo":
            o["tanpa_logo"] = True
        elif a in ("-h", "--help"):
            raise SystemExit(__doc__)
        elif a.startswith("--"):
            raise SystemExit(f"Opsi tidak dikenal: {a}\n\n{__doc__}")
        else:
            pos.append(a)
    if len(pos) != 1:
        raise SystemExit(__doc__)
    path = pos[0]
    if not os.path.isfile(path):
        raise SystemExit(f"ERROR: berkas tidak ditemukan: {path}")
    os.makedirs(o["keluar"], exist_ok=True)
    ext = os.path.splitext(path)[1].lower()
    R = {"sumber": os.path.abspath(path), "jenis": ext.lstrip("."), "ocr": False, "logo": None, "gambar": [], "catatan": []}
    teks, pdf = "", False

    if ext == ".docx":
        with zipfile.ZipFile(path) as z:
            teks, mesin = teks_docx(path, z)
            R["pembaca"] = mesin
            R["rumus"] = len(re.findall(r"\$[^$\n]+\$", teks)) if mesin == "pandoc" else len(re.findall(r"<m:oMath[ >]", z.read("word/document.xml").decode("utf-8", "ignore")))
            if mesin == "xml" and R["rumus"]:
                R["catatan"].append("Ada rumus Word tetapi pandoc tidak tersedia: tulis ulang rumus dari word/document.xml dan cocokkan dengan sumber.")
            g = gambar_docx(z, o["keluar"], o["maks_gambar"], o["tanpa_logo"])
            R["logo"], R["gambar"] = g["logo"], g["gambar"]
            for k in ("logo_catatan", "gambar_dilewati"):
                if k in g:
                    R["catatan"].append(g[k] if isinstance(g[k], str) else "; ".join(g[k]))
    elif ext == ".pdf":
        pdf = True
        if not ada("pdftotext"):
            raise SystemExit("ERROR: pdftotext tidak tersedia. Minta .docx atau teks dari pengguna.")
        r = jalankan(["pdftotext", path, "-"])
        teks = r.stdout
        halaman = max(1, teks.count("\f"))
        if len(teks.strip()) < 60 * halaman:
            hasil, info = ocr_pdf(path, o["keluar"])
            if hasil is None:
                R["catatan"].append(info)
                R["ocr"] = "gagal"
            else:
                teks, R["ocr"] = hasil, True
                R["catatan"].append(f"Teks dibaca lewat OCR ({info}). Angka, nama, dan ayat wajib diperiksa ulang; sebut 'perlu dicek manual' di balasan akhir.")
        if not o["tanpa_logo"]:
            R["logo"] = logo_pdf(path, o["keluar"])
        if o["halaman"]:
            hal = render_halaman(path, o["halaman"], o["keluar"])
            if hal:
                R["gambar"].append({"file": hal, "keterangan": f"halaman {o['halaman']} (render 200 dpi); crop dengan PIL bila perlu"})
    elif ext in (".md", ".markdown", ".txt", ""):
        teks = open(path, encoding="utf-8", errors="replace").read()
    else:
        raise SystemExit(f"ERROR: jenis berkas '{ext}' belum didukung (pakai .docx, .pdf, .md, atau .txt).")

    teks = bersihkan(teks, pdf=pdf, markdown=(R.get("pembaca") == "pandoc"))
    badan, pustaka = pisah_pustaka(teks)
    open(os.path.join(o["keluar"], "sumber.txt"), "w", encoding="utf-8").write(badan)
    if pustaka:
        open(os.path.join(o["keluar"], "pustaka.txt"), "w", encoding="utf-8").write(pustaka)
    n_kata = len(re.findall(r"\S+", badan))
    R.update({
        "sumber_txt": os.path.join(o["keluar"], "sumber.txt"),
        "pustaka_txt": os.path.join(o["keluar"], "pustaka.txt") if pustaka else None,
        "karakter": len(badan), "kata": n_kata, "perkiraan_halaman": round(n_kata / 300, 1),
        "pustaka_entri_kira_kira": len([b for b in pustaka.splitlines()[1:] if len(b.strip()) > 30]) if pustaka else 0,
        "bab_terdeteksi": [re.sub(r"[#*]", "", m.group(0)).strip() for m in REGEX_BAB.finditer(badan)][:40],
        "template_placeholder": sorted(set(REGEX_TEMPLATE.findall(badan)))[:10],
        "awal_dokumen": [b.strip()[:160] for b in badan.splitlines() if b.strip()][:25],
    })
    if R["template_placeholder"]:
        R["catatan"].append("Isi dokumen masih berupa template (ada placeholder seperti [Tuliskan ...]). Beri tahu pengguna sebelum membuat slide.")
    if n_kata < 150:
        R["catatan"].append("Teks sangat pendek; periksa apakah dokumen kosong atau berupa gambar (coba OCR atau minta versi .docx).")
    json.dump(R, open(os.path.join(o["keluar"], "ringkasan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(R, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
