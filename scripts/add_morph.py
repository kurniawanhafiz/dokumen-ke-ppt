#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pasang transisi antar-slide dan (opsional) tema warna di sebuah .pptx.

Pemakaian:
  python3 add_morph.py masuk.pptx keluar.pptx [--transisi=morph|fade|kombinasi] [--gaya=gaya.json] [--animasi]

--transisi (bawaan morph)
  morph      Morph di semua slide (cadangan fade untuk PowerPoint lama)
  fade       Fade di semua slide (paling aman untuk Google Slides, Keynote, Canva)
  kombinasi  Morph di sebagian besar slide, Push (dari bawah) di pembatas bab,
             Wipe di slide grafik (grafik tidak ikut Morph, jadi dibuka dari sisi)
--gaya     gaya.json dari gaya.py. Warna dan font tema dituliskan ke tema PowerPoint
           (Design > Variants), sehingga slide yang ditambah pengguna ikut serasi.

--animasi  (opsional, bawaan mati) Isi slide muncul bertahap dengan Fade, otomatis tanpa klik,
           kelompok per nomor (kartu 1, kartu 2, ...). Dilewati di sampul, penutup, pembatas bab
           dan agenda. Dibuat dari XML tangan dan belum teruji di PowerPoint asli, jadi pratinjau dulu.

Selain itu, gambar kembar di ppt/media digabung otomatis (ikon yang sama tidak disimpan berkali-kali).

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


# ---------- animasi masuk (opsional) ----------
ELEM_RE = re.compile(r"<p:(sp|pic)>.*?</p:\1>", re.S)
CNV_RE = re.compile(r'<p:cNvPr id="(\d+)" name="([^"]*)"')
DIGIT_RE = re.compile(r"(\d+)")
ABAIKAN_ANIMASI = ("agenda", "kembaliAgenda")


def kelompok_animasi(xml):
    """Kumpulkan objek per nomor di namanya (poinKartu1, poinTeks1 -> kelompok 1). Hasil: [(nomor, [(id, punyaTeks)])]."""
    grup = {}
    for m in ELEM_RE.finditer(xml):
        el = m.group(0)
        c = CNV_RE.search(el)
        if not c:
            continue
        sid, nama = c.group(1), c.group(2)
        if nama.startswith("!!") or nama.startswith(ABAIKAN_ANIMASI):
            continue
        d = DIGIT_RE.search(nama)
        if not d:
            continue
        grup.setdefault(int(d.group(1)), []).append((sid, "<p:txBody>" in el and m.group(1) == "sp"))
    return sorted(grup.items())[:8]


def buat_timing(grup, jeda=220, durasi=450):
    n = [4]  # id 1-2 untuk root/mainSeq, 3-4 untuk pembungkus, efek mulai dari 5

    def nid():
        n[0] += 1
        return n[0]

    efek, bld, pertama = [], [], True
    for k, (_, objs) in enumerate(grup):
        for sid, teks in objs:
            a, b, c = nid(), nid(), nid()
            gid = ' grpId="0"' if teks else ""
            tipe = "afterEffect" if pertama else "withEffect"
            pertama = False
            efek.append(
                f'<p:par><p:cTn id="{a}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold"{gid} nodeType="{tipe}">'
                f'<p:stCondLst><p:cond delay="{k * jeda}"/></p:stCondLst><p:childTnLst>'
                f'<p:set><p:cBhvr><p:cTn id="{b}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
                f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
                f'<p:to><p:strVal val="visible"/></p:to></p:set>'
                f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{c}" dur="{durasi}"/>'
                f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>'
            )
            if teks:
                bld.append(f'<p:bldP spid="{sid}" grpId="0" animBg="1"/>')
    return (
        '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
        '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
        '<p:par><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
        '<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
        '<p:par><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>%s</p:childTnLst></p:cTn></p:par>'
        '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
        '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
        '</p:childTnLst></p:cTn></p:par></p:tnLst>%s</p:timing>'
    ) % (3, 4, "".join(efek), ("<p:bldLst>" + "".join(bld) + "</p:bldLst>") if bld else "")


def pasang_animasi(xml):
    """Sisipkan p:timing di slide isi. Mengembalikan (xml, True) bila terpasang."""
    if "<p:timing" in xml or 'name="nomorBagian"' in xml or 'name="agendaKartu1"' in xml:
        return xml, False
    grup = kelompok_animasi(xml)
    if len(grup) < 2:
        return xml, False
    blok = buat_timing(grup)
    akhir = xml.rfind("</p:sld>")
    ext = xml.rfind("<p:extLst")
    titik = ext if ext > xml.rfind("</p:cSld>") else akhir
    return xml[:titik] + blok + xml[titik:], True


# ---------- gabungkan media kembar ----------
def gabung_media(isi):
    """isi: dict nama->bytes. Gabungkan berkas ppt/media yang isinya identik dan perbarui .rels."""
    import hashlib
    kanon, ganti = {}, {}
    for nama in sorted(isi):
        if nama.startswith("ppt/media/"):
            h = hashlib.md5(isi[nama]).hexdigest()
            if h in kanon:
                ganti[nama.rsplit("/", 1)[1]] = kanon[h].rsplit("/", 1)[1]
            else:
                kanon[h] = nama
    if not ganti:
        return isi, 0
    pola = re.compile(r"(media/)(" + "|".join(re.escape(x) for x in ganti) + r")(?=[\"'])")
    baru = {}
    for nama, data in isi.items():
        if nama.startswith("ppt/media/") and nama.rsplit("/", 1)[1] in ganti:
            continue
        if nama.endswith(".rels"):
            data = pola.sub(lambda m: m.group(1) + ganti[m.group(2)], data.decode("utf-8")).encode("utf-8")
        baru[nama] = data
    return baru, len(ganti)


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


def main(masuk, keluar, mode="morph", gaya=None, animasi=False):
    if masuk == keluar:
        raise SystemExit("File keluaran harus beda dari file masukan.")
    terpasang = dilewati = tema = anim = 0
    nama_per_slide = {}
    with zipfile.ZipFile(masuk) as zin:
        info_list = zin.infolist()
        isi = {i.filename: zin.read(i.filename) for i in info_list}
    urut_slide = sorted((f for f in isi if SLIDE_RE.match(f)), key=lambda f: int(re.search(r"(\d+)", f.rsplit("/", 1)[1]).group(1)))
    for f in urut_slide:
        xml, berubah = sisipkan(isi[f].decode("utf-8"), mode)
        nama_per_slide[f] = set(NAMA_MORPH_RE.findall(xml))
        # animasi: lewati slide pertama (sampul) dan terakhir (penutup/referensi)
        if animasi and f not in (urut_slide[0], urut_slide[-1]):
            xml, ok = pasang_animasi(xml)
            anim += ok
        isi[f] = xml.encode("utf-8")
        terpasang += berubah
        dilewati += not berubah
    if gaya:
        for f in isi:
            if THEME_RE.match(f):
                isi[f] = tulis_tema(isi[f].decode("utf-8"), gaya).encode("utf-8")
                tema += 1
    isi, kembar = gabung_media(isi)
    with zipfile.ZipFile(keluar, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in info_list:  # pertahankan urutan asli ([Content_Types].xml harus pertama)
            if info.filename in isi:
                zout.writestr(info, isi[info.filename])
    print(f"Transisi '{mode}' terpasang di {terpasang} slide, dilewati {dilewati} slide: {keluar}")
    if kembar:
        print(f"Media kembar digabung: {kembar} berkas dihapus.")
    if animasi:
        print(f"Animasi masuk terpasang di {anim} slide (opsional; pratinjau di PowerPoint sebelum dipakai).")
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
    posisi, mode, gaya, animasi = [], "morph", None, False
    for a in argv:
        if a.startswith("--transisi="):
            mode = a.split("=", 1)[1].lower()
        elif a == "--animasi":
            animasi = True
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
    return posisi[0], posisi[1], mode, gaya, animasi


if __name__ == "__main__":
    main(*baca_argumen(sys.argv[1:]))
