#!/usr/bin/env python3
"""Pasang transisi Morph di semua slide sebuah .pptx.

Pemakaian:
  python3 add_morph.py masuk.pptx keluar.pptx

pptxgenjs tidak punya opsi Morph, jadi blok XML disisipkan langsung ke
ppt/slides/slideN.xml. Aman dijalankan ulang (slide yang sudah punya Morph dilewati).

PowerPoint hanya memasangkan objek antar slide berdasarkan nama jika namanya diawali
"!!" (contoh "!!judul"). Script ini memberi peringatan untuk slide yang tidak punya
objek bernama "!!...", atau yang namanya tidak muncul di slide lain, karena Morph di
slide itu kemungkinan jatuh ke tebakan kemiripan atau fade.
"""
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

SLIDE_RE = re.compile(r"^ppt/slides/slide\d+\.xml$")
NAMA_MORPH_RE = re.compile(r'<p:cNvPr[^>]*\bname="(!![^"]*)"')


def sisipkan(xml):
    if "p159:morph" in xml:
        return xml, False
    # Urutan elemen p:sld: cSld, clrMapOvr, transition, timing, extLst
    if "</p:clrMapOvr>" in xml:
        return xml.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + MORPH_XML, 1), True
    for penanda in ("<p:timing", "<p:extLst", "</p:sld>"):
        if penanda in xml:
            return xml.replace(penanda, MORPH_XML + penanda, 1), True
    raise ValueError("Struktur slide tidak dikenali")


def main(masuk, keluar):
    if masuk == keluar:
        raise SystemExit("File keluaran harus beda dari file masukan.")
    terpasang = dilewati = 0
    nama_per_slide = {}
    with zipfile.ZipFile(masuk) as zin, zipfile.ZipFile(keluar, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if SLIDE_RE.match(info.filename):
                xml, berubah = sisipkan(data.decode("utf-8"))
                nama_per_slide[info.filename] = set(NAMA_MORPH_RE.findall(xml))
                data = xml.encode("utf-8")
                terpasang += berubah
                dilewati += not berubah
            zout.writestr(info, data)
    print(f"Morph terpasang di {terpasang} slide, dilewati {dilewati} slide: {keluar}")
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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
