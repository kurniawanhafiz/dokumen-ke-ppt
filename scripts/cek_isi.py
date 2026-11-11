#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Periksa dan rapikan isi.json sebelum PPT dibangun (dry-run, tanpa membuat file PPT).

Pemakaian:
  python3 cek_isi.py isi.json                          # hanya periksa dan laporkan
  python3 cek_isi.py isi.json --tulis                  # simpan hasil rapi ke isi.json (menimpa)
  python3 cek_isi.py isi.json --tulis isi.rapi.json    # simpan ke berkas lain
  python3 cek_isi.py isi.json --pecah --tulis          # slide yang kelebihan item dipecah "(lanjutan)"
  python3 cek_isi.py isi.json --gaya-kata=padat --durasi=10 --slide=12

Yang dikerjakan
  - Menyeragamkan bentuk isi: kartu, langkah, titik, statistik, dua kolom (daftar atau objek) -> bentuk baku.
  - Menebak 'tipe' yang hilang dari bidang yang ada; tipe tak dikenal dijadikan 'poin' dengan peringatan.
  - Grafik: jumlah nilai harus sama dengan jumlah label (ERROR); angka format Indonesia (1.234,5) dibaca benar.
  - Batas item per slide (poin 5, kartu 6, langkah 5, garis 5, statistik 4, tabel 5 baris x 4 kolom).
    Tanpa --pecah hanya dilaporkan; dengan --pecah slide dipecah. Pakai --pecah hanya jika jumlah slide bebas.
  - Kepadatan kata menurut gaya kata (singkat, padat, poin), tiga slide isi berurutan bertipe sama,
    catatan kosong, total kata naskah terhadap durasi (130 kata per menit), berkas gambar dan rumus, nama ikon.
  - Menghitung total slide (pembuka + slide + Referensi + penutup) dan membandingkannya dengan --slide=N.

Kode keluar: 0 jika tidak ada ERROR, 1 jika ada. Peringatan tidak menggagalkan.
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASET = os.path.normpath(os.path.join(HERE, "..", "aset"))

TIPE = ("agenda", "bagian", "poin", "kartu", "langkah", "garis", "dua", "definisi", "contoh", "angka",
        "statistik", "grafik", "tabel", "kutipan", "gambar")
BATAS = {"poin": 5, "kartu": 6, "langkah": 5, "garis": 5, "statistik": 4, "tabel": 5}
KUNCI_LIST = {"poin": "poin", "kartu": "kartu", "langkah": "langkah", "garis": "titik", "tabel": "baris"}
# gaya kata: (maks poin disarankan, maks kata per poin, maks kata per slide)
GAYA_KATA = {"singkat": (4, 15, 50), "padat": (5, 20, 80), "poin": (3, 6, 20)}
WPM = 130
TOLERANSI_KATA = 1.3  # peringatan kepadatan baru muncul jika melebihi batas x 1,3

ERRORS, WARNS = [], []


def err(m):
    ERRORS.append(m)
    print("ERROR:", m)


def warn(m):
    WARNS.append(m)
    print("PERINGATAN:", m)


def kata(t):
    return len(re.findall(r"\S+", t or ""))


def angka(v, bahasa="id"):
    """Ubah teks angka jadi float. Mengerti 1.234,5 (Indonesia), 1,234.5 (Inggris), 12,5%, dan 1.234 (ribuan)."""
    if isinstance(v, bool):
        raise ValueError("bukan angka")
    if isinstance(v, (int, float)):
        return float(v)
    t = re.sub(r"[^0-9,.\-]", "", str(v))
    if t in ("", "-", ".", ","):
        raise ValueError(f"'{v}' bukan angka")
    if "," in t and "." in t:  # pemisah terakhir adalah desimal
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")
        else:
            t = t.replace(",", "")
    elif "," in t:
        bag = t.split(",")
        ribuan = len(bag) > 2 or (len(bag[-1]) == 3 and 0 < len(bag[0].lstrip("-")) <= 3 and bahasa == "en")
        t = t.replace(",", "") if ribuan else t.replace(",", ".")
    elif "." in t:
        bag = t.split(".")
        ribuan = len(bag) > 2 or (len(bag[-1]) == 3 and 0 < len(bag[0].lstrip("-")) <= 3 and bahasa != "en" and bag[0].lstrip("-") != "0")
        if ribuan:
            t = t.replace(".", "")
    return float(t)


def baku_item(x, kunci_judul=("j", "judul", "title"), kunci_teks=("t", "isi", "teks", "text", "deskripsi")):
    """Bentuk baku {j, t, ikon?} dari daftar [j, t, ikon] atau objek."""
    if isinstance(x, dict):
        j = next((x[k] for k in kunci_judul if k in x), "")
        t = next((x[k] for k in kunci_teks if k in x), "")
        o = {"j": str(j), "t": str(t)}
        if x.get("ikon"):
            o["ikon"] = x["ikon"]
        return o
    if isinstance(x, (list, tuple)):
        o = {"j": str(x[0]) if len(x) > 0 else "", "t": str(x[1]) if len(x) > 1 else ""}
        if len(x) > 2 and x[2]:
            o["ikon"] = x[2]
        return o
    return {"j": str(x), "t": ""}


def baku_statistik(x):
    if isinstance(x, dict):
        return [str(x.get("angka", x.get("a", ""))), str(x.get("label", x.get("l", x.get("t", ""))))]
    if isinstance(x, (list, tuple)):
        return [str(x[0]) if len(x) > 0 else "", str(x[1]) if len(x) > 1 else ""]
    return [str(x), ""]


def tebak_tipe(sd):
    for k, v in (("kartu", "kartu"), ("langkah", "langkah"), ("seri", "grafik"), ("baris", "tabel"), ("titik", "garis"),
                 ("data", "statistik"), ("file", "gambar"), ("angka", "angka"), ("kiri", "dua"), ("soal", "contoh"),
                 ("poin", "poin")):
        if k in sd:
            return v
    if "teks" in sd:
        return "kutipan" if "oleh" in sd else "definisi"
    return None


def pecah(items, mx):
    n = max(1, math.ceil(len(items) / mx))
    per = math.ceil(len(items) / n)
    return [items[k:k + per] for k in range(0, len(items), per)], per


def kata_slide(sd):
    t = sd["tipe"]
    if t == "poin":
        return sum(kata(p) for p in sd.get("poin", []))
    if t in ("kartu", "langkah", "garis"):
        return sum(kata(x.get("j")) + kata(x.get("t")) for x in sd.get({"garis": "titik"}.get(t, t), []))
    if t == "dua":
        return sum(kata(p) for k in ("kiri", "kanan") for p in sd.get(k, {}).get("poin", []))
    return 0


def kerjakan(D, opsi, dasar):
    M = D.setdefault("meta", {})
    bahasa = M.get("bahasa", "id")
    en = bahasa == "en"
    lanjut = "(continued)" if en else "(lanjutan)"
    if not M.get("judul"):
        err("meta.judul wajib diisi.")
    if not M.get("footer"):
        warn("meta.footer kosong (footer slide akan kosong).")
    for kolom, nama in (("logo", "logo"), ("foto", "foto")):
        f = M.get(kolom)
        if f and not (os.path.isabs(f) and os.path.exists(f)) and not os.path.exists(f):
            alt = os.path.join(dasar, f)
            if os.path.exists(alt):
                warn(f"meta.{nama} '{f}' ada di folder isi.json tetapi tidak di folder kerja; jalankan pembuat dari folder isi.json.")
            else:
                warn(f"meta.{nama} '{f}' tidak ditemukan; akan dilewati.")
    mx_poin, mx_kata_poin, mx_kata_slide = GAYA_KATA[opsi["gaya_kata"]]

    keluar = []
    for i, sd in enumerate(D.get("slide", []), 1):
        sd = dict(sd)
        t = sd.get("tipe") or tebak_tipe(sd)
        label = f"slide {i} ({sd.get('judul', t) or t})"
        if t not in TIPE:
            warn(f"{label}: tipe '{t}' tidak dikenal, dijadikan 'poin'.")
            t = "poin"
        sd["tipe"] = t
        if isinstance(sd.get("poin"), str):
            sd["poin"] = [sd["poin"]]
        if isinstance(sd.get("ikon"), list):
            warn(f"{label}: 'ikon' berupa daftar; dipakai ikon pertama.")
            sd["ikon"] = sd["ikon"][0] if sd["ikon"] else None
            if sd["ikon"] is None:
                del sd["ikon"]

        # --- seragamkan bentuk ---
        for key in ("kartu", "langkah"):
            if key in sd:
                sd[key] = [baku_item(x) for x in sd[key]]
        if "titik" in sd:
            sd["titik"] = [{k: v for k, v in baku_item(x).items() if k != "ikon"} for x in sd["titik"]]
        if "data" in sd:
            sd["data"] = [baku_statistik(x) for x in sd["data"]]
        if t == "dua":
            for k in ("kiri", "kanan"):
                kol = sd.get(k)
                if not isinstance(kol, dict):
                    err(f"{label}: '{k}' harus berupa objek {{j, poin[]}}.")
                    continue
                if "judul" in kol and "j" not in kol:
                    kol["j"] = kol.pop("judul")
                if isinstance(kol.get("poin"), str):
                    kol["poin"] = [kol["poin"]]
                kol.setdefault("poin", [])

        # --- bidang wajib per tipe ---
        wajib = {"poin": ("poin",), "kartu": ("kartu",), "langkah": ("langkah",), "garis": ("titik",), "definisi": ("teks",),
                 "angka": ("angka", "label"), "statistik": ("data",), "grafik": ("jenis", "label", "seri"),
                 "tabel": ("kolom", "baris"), "kutipan": ("teks",), "gambar": ("file",), "contoh": ("soal",)}
        hilang = [k for k in wajib.get(t, ()) if not sd.get(k)]
        if hilang:
            err(f"{label}: bidang wajib kosong: {', '.join(hilang)}.")
            keluar.append(sd)
            continue

        # --- langkah dengan satu tahap bukan alur ---
        if t == "langkah" and len(sd["langkah"]) < 2:
            warn(f"{label}: 'langkah' butuh minimal 2 tahap; dijadikan 'poin'.")
            sd["tipe"] = t = "poin"
            sd["poin"] = [f"{x['j']}: {x['t']}".strip(": ") for x in sd.pop("langkah")]

        # --- grafik ---
        if t == "grafik":
            jenis = (sd.get("jenis") or "").lower()
            if jenis not in ("batang", "batang-h", "garis", "donat", "pie"):
                err(f"{label}: jenis grafik '{jenis}' tidak dikenal (batang, batang-h, garis, donat, pie).")
            sd["jenis"] = jenis
            for se in sd["seri"]:
                nil = se.get("nilai") or []
                if len(nil) != len(sd["label"]):
                    err(f"{label}: seri '{se.get('nama', '')}' punya {len(nil)} nilai tetapi ada {len(sd['label'])} label.")
                    continue
                try:
                    se["nilai"] = [angka(v, bahasa) for v in nil]
                except ValueError as e:
                    err(f"{label}: {e}.")
            if jenis in ("donat", "pie") and len(sd["seri"]) > 1:
                warn(f"{label}: grafik {jenis} hanya memakai seri pertama.")
                sd["seri"] = sd["seri"][:1]

        # --- statistik ---
        if t == "statistik" and not 2 <= len(sd["data"]) <= BATAS["statistik"]:
            warn(f"{label}: statistik seharusnya 2 sampai {BATAS['statistik']} angka (ada {len(sd['data'])}).")
            sd["data"] = sd["data"][:BATAS["statistik"]]

        # --- tabel ---
        if t == "tabel":
            if len(sd["kolom"]) > 4:
                warn(f"{label}: tabel punya {len(sd['kolom'])} kolom (maksimal 4); ringkas jadi kartu atau pecah manual.")
            for b in sd["baris"]:
                if len(b) != len(sd["kolom"]):
                    err(f"{label}: ada baris tabel dengan {len(b)} sel padahal kolom ada {len(sd['kolom'])}.")
                    break

        # --- berkas gambar dan rumus ---
        if t == "gambar":
            if not os.path.exists(sd["file"]) and not os.path.exists(os.path.join(dasar, sd["file"])):
                err(f"{label}: berkas gambar '{sd['file']}' tidak ditemukan.")
            if not sd.get("alt"):
                warn(f"{label}: gambar belum punya alt text.")
        if t == "contoh":
            for it in sd.get("isi", []):
                if isinstance(it, dict) and it.get("rumus"):
                    if not os.path.exists(it["rumus"]) and not os.path.exists(os.path.join(dasar, it["rumus"])):
                        err(f"{label}: berkas rumus '{it['rumus']}' tidak ditemukan.")
                    if not it.get("alt"):
                        warn(f"{label}: rumus '{it['rumus']}' belum punya alt text.")

        # --- nama ikon ---
        nama_ikon = [sd.get("ikon")] + [x.get("ikon") for k in ("kartu", "langkah") for x in sd.get(k, [])]
        for n in filter(None, nama_ikon):
            if not os.path.exists(os.path.join(ASET, "ikon", f"{n}.png")):
                warn(f"{label}: ikon '{n}' tidak ada (akan diganti 'lightbulb'). Lihat: python3 ikon.py --daftar")

        # --- batas item, pecah bila diminta ---
        if t in KUNCI_LIST:
            key = KUNCI_LIST[t]
            items = sd.get(key, [])
            mx = BATAS[t]
            if t == "tabel" and len(items) > mx:
                msg = f"{label}: {len(items)} baris melebihi batas {mx}"
            elif t != "tabel" and len(items) > mx:
                msg = f"{label}: {len(items)} item melebihi batas {mx}"
            else:
                msg = None
            if msg and opsi["pecah"]:
                bagian, per = pecah(items, mx)
                for c, ch in enumerate(bagian):
                    ns = dict(sd)
                    ns[key] = ch
                    if c:
                        ns["judul"] = f"{sd.get('judul', '')} {lanjut}".strip()
                        ns["catatan"] = ""
                        ns.pop("ikon", None)
                        warn(f"{label}: bagian {lanjut} perlu catatan (naskah) ditulis.")
                    keluar.append(ns)
                print(f"Dipecah: {label} menjadi {len(bagian)} slide.")
                continue
            if msg:
                warn(msg + " (pakai --pecah jika jumlah slide bebas, atau persingkat).")

        # --- kepadatan kata ---
        if t in ("poin", "kartu", "langkah", "garis", "dua"):
            teks_poin = list(sd.get("poin", []))
            if t == "dua":
                teks_poin = [p for k in ("kiri", "kanan") for p in sd[k].get("poin", [])]
            if t == "poin" and len(sd["poin"]) > mx_poin:
                warn(f"{label}: {len(sd['poin'])} poin, gaya '{opsi['gaya_kata']}' menyarankan maksimal {mx_poin}.")
            for p in teks_poin:
                if kata(p) > mx_kata_poin * TOLERANSI_KATA:
                    warn(f"{label}: poin {kata(p)} kata (gaya '{opsi['gaya_kata']}': sekitar {mx_kata_poin}): \"{p[:40]}...\"")
            if kata_slide(sd) > mx_kata_slide * TOLERANSI_KATA and t in ("poin", "dua"):
                warn(f"{label}: sekitar {kata_slide(sd)} kata di slide (gaya '{opsi['gaya_kata']}': sekitar {mx_kata_slide}). Pindahkan penjelasan ke catatan.")

        # --- catatan ---
        if not (sd.get("catatan") or "").strip():
            warn(f"{label}: belum ada catatan (naskah).")
        keluar.append(sd)

    D["slide"] = keluar
    return keluar


def jumlah_slide(D):
    isi = D.get("slide", [])
    pustaka = D.get("pustaka") or []
    nref, h, n = 0, 0.0, 0
    for e in pustaka:
        t = math.ceil(len(e) / 135) * 0.2 + 0.12
        if n and (h + t > 4.7 or n >= 8):
            nref += 1
            h, n = 0.0, 0
        h += t
        n += 1
    if n:
        nref += 1
    return 2 + len(isi) + nref, nref


def periksa_alur(slides):
    seri = 0
    prev = None
    for i, s in enumerate(slides, 1):
        t = s.get("tipe")
        if t in ("bagian", "agenda"):
            seri, prev = 0, None
            continue
        seri = seri + 1 if t == prev else 1
        prev = t
        if seri == 3:
            warn(f"slide {i}: tiga slide isi berturut-turut bertipe '{t}'; variasikan layout.")


def periksa_naskah(D, durasi, slides):
    M = D.get("meta", {})
    total = kata(M.get("catatan_sampul")) + kata(M.get("catatan_penutup")) + sum(kata(s.get("catatan")) for s in slides)
    total += kata(D.get("catatan_referensi"))
    batas = durasi * WPM
    menit = total / WPM
    print(f"Naskah: {total} kata (~{menit:.1f} menit); batas {batas} kata untuk {durasi} menit.")
    if total > batas * 1.1:
        warn(f"naskah {total} kata melewati batas {batas} (+10%) untuk {durasi} menit; persingkat catatan.")
    elif total < batas * 0.4 and slides:
        warn(f"naskah baru {total} kata, jauh di bawah {batas}; tidak apa-apa jika materi memang sedikit.")
    for k in ("catatan_sampul", "catatan_penutup"):
        if not (M.get(k) or "").strip():
            warn(f"meta.{k} kosong (naskah {'pembuka' if k.endswith('sampul') else 'penutup'}).")


def baca_argumen(argv):
    o = {"berkas": None, "tulis": None, "pecah": False, "gaya_kata": "singkat", "durasi": 15, "slide": None}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--pecah":
            o["pecah"] = True
        elif a == "--tulis":
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                i += 1
                o["tulis"] = argv[i]
            else:
                o["tulis"] = "__timpa__"
        elif a.startswith("--tulis="):
            o["tulis"] = a.split("=", 1)[1]
        elif a.startswith("--gaya-kata="):
            o["gaya_kata"] = a.split("=", 1)[1].lower()
        elif a.startswith("--durasi="):
            o["durasi"] = float(a.split("=", 1)[1])
        elif a.startswith("--slide="):
            o["slide"] = int(a.split("=", 1)[1])
        elif a in ("-h", "--help"):
            raise SystemExit(__doc__)
        elif a.startswith("--"):
            raise SystemExit(f"Opsi tidak dikenal: {a}\n\n{__doc__}")
        elif o["berkas"] is None:
            o["berkas"] = a
        else:
            raise SystemExit(__doc__)
        i += 1
    if not o["berkas"]:
        raise SystemExit(__doc__)
    if o["gaya_kata"] not in GAYA_KATA:
        raise SystemExit("--gaya-kata harus singkat, padat, atau poin.")
    return o


def main(argv):
    o = baca_argumen(argv)
    try:
        D = json.load(open(o["berkas"], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"ERROR: tidak bisa membaca {o['berkas']}: {e}")
    dasar = os.path.dirname(os.path.abspath(o["berkas"]))
    slides = kerjakan(D, o, dasar)
    periksa_alur(slides)
    periksa_naskah(D, o["durasi"], slides)
    total, nref = jumlah_slide(D)
    print(f"Total slide: {total} (pembuka 1 + isi {len(slides)} + Referensi {nref} + penutup 1).")
    if o["slide"] and total != o["slide"]:
        warn(f"jumlah slide {total} berbeda dari --slide={o['slide']}.")
    if o["tulis"] and not ERRORS:
        tujuan = o["berkas"] if o["tulis"] == "__timpa__" else o["tulis"]
        with open(tujuan, "w", encoding="utf-8") as f:
            json.dump(D, f, ensure_ascii=False, indent=2)
        print(f"Tersimpan: {tujuan}")
    elif o["tulis"] and ERRORS:
        print("Tidak ditulis karena ada ERROR.")
    print(f"{'GAGAL' if ERRORS else 'OK'}: {len(ERRORS)} error, {len(WARNS)} peringatan.")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
