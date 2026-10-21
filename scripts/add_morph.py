#!/usr/bin/env python3
"""Pasang transisi Morph di semua slide sebuah .pptx.

Pemakaian:
  python3 add_morph.py masuk.pptx keluar.pptx

pptxgenjs tidak punya opsi Morph, jadi blok XML disisipkan langsung ke
ppt/slides/slideN.xml. Aman dijalankan ulang (slide yang sudah punya Morph dilewati).
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
    with zipfile.ZipFile(masuk) as zin, zipfile.ZipFile(keluar, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if SLIDE_RE.match(info.filename):
                xml, berubah = sisipkan(data.decode("utf-8"))
                data = xml.encode("utf-8")
                terpasang += berubah
                dilewati += not berubah
            zout.writestr(info, data)
    print(f"Morph terpasang di {terpasang} slide, dilewati {dilewati} slide: {keluar}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
