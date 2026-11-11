#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pasang transisi antar-slide dan (opsional) tema warna di sebuah .pptx.

Pemakaian:
  python3 add_morph.py masuk.pptx keluar.pptx [--transisi=morph|fade|kombinasi] [--gaya=gaya.json]

--transisi (bawaan morph)
  morph      Morph di semua slide (cadangan fade untuk PowerPoint lama)
  fade       Fade di semua slide (paling aman untuk Google Slides, Keynote, Canva)
  kombinasi  Morph di sebagian besar slide, Push (dari bawah) di pembatas bab,
             Wipe di slide grafik (grafik tidak ikut Morph, jadi dibuka dari sisi)
--gaya     gaya.json dari gaya.py. Warna dan font tema dituliskan ke tema PowerPoint
           (Design > Variants), sehingga slide yang ditambah pengguna ikut serasi.

pptxgenjs tidak punya opsi transisi, jadi blok XML disisipkan langsung ke
ppt/slides/slideN.xml. Aman dijalankan ulang (slide yang sudah punya transisi dilewati).

PowerPoint hanya memasangkan objek antar slide berdasarkan nama jika namanya diawali
"!!" (contoh "!!judul"). Script ini memberi peringatan untuk slide yang tidak punya
objek bernama "!!...", atau yang namanya tidak muncul di slide lain, karena Morph di
slide itu kemungkinan jatuh ke tebakan kemiripan atau fade.
"""
import json
import re
import sys
import zipfile

MORPH_XML = (
    '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
    '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
    '<p:transition spd="slow" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" p14:dur="1250">'
    '<p159:morph option="byObject"/></p:transition></mc:Choice>'
    '<mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>'
)
FADE_XML = '<p:transition spd="med"><p:fade/></p:transition>'
PUSH_XML = '<p:transition spd="med"><p:push dir="u"/></p:transition>'
WIPE_XML = '<p:transition spd="med"><p:wipe dir="r"/></p:transition>'

SLIDE_RE = re.compile(r"^ppt/slides/slide\d+\.xml$")
THEME_RE = re.compile(r"^ppt/theme/theme\d+\.xml$")
NAMA_MORPH_RE = re.compile(r'<p:cNvPr[^>]*\bname="(!![^"]*)"')
TRANSISI = ("morph", "fade", "kombinasi")


def jenis_slide(xml):
    """Tebak jenis slide dari nama objek yang diberikan bangun_ppt.js."""
    if 'name="nomorBagian"' in xml:
        return "bagian"
    if 'name="grafikKartu"' in xml or "drawingml/2006/chart" in xml:
        return "grafik"
    return "lain"


def pilih_xml(mode, jenis):
    if mode == "fade":
        return FADE_XML
    if mode == "kombinasi":
        if jenis == "bagian":
            return PUSH_XML
        if jenis == "grafik":
            return WIPE_XML
    return MORPH_XML


def sisipkan(xml, mode="morph"):
    if "p159:morph" in xml or "<p:transition" in xml:
        return xml, False
    blok = pilih_xml(mode, jenis_slide(xml))
    # Urutan elemen p:sld: cSld, clrMapOvr, transition, timing, extLst
    if "</p:clrMapOvr>" in xml:
        return xml.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + blok, 1), True
    for penanda in ("<p:timing", "<p:extLst", "</p:sld>"):
        if penanda in xml:
            return xml.replace(penanda, blok + penanda, 1), True
    raise ValueError("Struktur slide tidak dikenali")


def tulis_tema(xml, g):
    """Ganti warna dan nama tema PowerPoint dengan warna gaya.

    lt1 = latar, dk1 = teks, supaya slide baru (bg1/tx1) mengikuti gaya, termasuk tema gelap.
    Font sudah diatur oleh pptxgenjs (headFontFace/bodyFontFace)."""
    seri = (g.get("seri") or []) + [g["utama"]] * 4
    warna = {
        "dk1": g["ink"], "lt1": g["bg"], "dk2": g["muted"], "lt2": g["card"],
        "accent1": seri[0], "accent2": seri[1], "accent3": seri[2], "accent4": seri[3],
        "accent5": g["muted"], "accent6": g["judul"], "hlink": g["aksen"], "folHlink": g["muted"],
    }
    for k, v in warna.items():
        xml = re.sub(rf"<a:{k}>.*?</a:{k}>", f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>', xml, count=1, flags=re.S)
    nama = f"Dokumen ke PPT - {g.get('nama', 'Polos')}"
    xml = re.sub(r'(<a:theme\b[^>]*\bname=")[^"]*', r"\g<1>" + nama, xml, count=1)
    return xml


def main(masuk, keluar, mode="morph", gaya=None):
    if masuk == keluar:
        raise SystemExit("File keluaran harus beda dari file masukan.")
    terpasang = dilewati = tema = 0
    nama_per_slide = {}
    with zipfile.ZipFile(masuk) as zin, zipfile.ZipFile(keluar, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if SLIDE_RE.match(info.filename):
                xml, berubah = sisipkan(data.decode("utf-8"), mode)
                nama_per_slide[info.filename] = set(NAMA_MORPH_RE.findall(xml))
                data = xml.encode("utf-8")
                terpasang += berubah
                dilewati += not berubah
            elif gaya and THEME_RE.match(info.filename):
                data = tulis_tema(data.decode("utf-8"), gaya).encode("utf-8")
                tema += 1
            zout.writestr(info, data)
    print(f"Transisi '{mode}' terpasang di {terpasang} slide, dilewati {dilewati} slide: {keluar}")
    if gaya:
        print(f"Tema PowerPoint diselaraskan dengan gaya '{gaya.get('nama', '')}' ({tema} berkas tema).")
    if mode != "fade":
        periksa_nama(nama_per_slide)


def periksa_nama(nama_per_slide):
    """Peringatkan slide tanpa objek '!!' atau yang tidak berbagi nama dengan slide lain."""
    urut = sorted(nama_per_slide, key=lambda f: int(re.search(r"(\d+)", f.rsplit("/", 1)[1]).group(1)))
    jumlah = 0
    for i, f in enumerate(urut):
        nama = nama_per_slide[f]
        label = f.rsplit("/", 1)[1]
        if not nama:
            print(f"PERINGATAN: {label} tidak punya objek bernama '!!...'; Morph kemungkinan jatuh ke fade.")
            jumlah += 1
            continue
        tetangga = set()
        if i > 0:
            tetangga |= nama_per_slide[urut[i - 1]]
        if i < len(urut) - 1:
            tetangga |= nama_per_slide[urut[i + 1]]
        if len(urut) > 1 and not (nama & tetangga):
            print(f"PERINGATAN: nama '!!' di {label} tidak sama dengan slide di sebelahnya.")
            jumlah += 1
    if jumlah == 0:
        print("Nama objek '!!' konsisten di semua slide.")


def baca_argumen(argv):
    posisi, mode, gaya = [], "morph", None
    for a in argv:
        if a.startswith("--transisi="):
            mode = a.split("=", 1)[1].lower()
        elif a.startswith("--gaya="):
            gaya = json.load(open(a.split("=", 1)[1], encoding="utf-8"))
        elif a.startswith("--"):
            raise SystemExit(f"Opsi tidak dikenal: {a}\n\n{__doc__}")
        else:
            posisi.append(a)
    if len(posisi) != 2:
        raise SystemExit(__doc__)
    if mode not in TRANSISI:
        raise SystemExit(f"--transisi harus salah satu dari: {', '.join(TRANSISI)}")
    return posisi[0], posisi[1], mode, gaya


if __name__ == "__main__":
    main(*baca_argumen(sys.argv[1:]))
