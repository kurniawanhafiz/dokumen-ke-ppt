// Menyusun daftar slide akhir dari isi.json (dipakai bangun_ppt.js dan buat_notes.js).
// SPDX-License-Identifier: GPL-3.0-or-later
// Urutan: sampul, slide isi (agenda, bagian, ...), referensi (dipecah otomatis), penutup.
const EN = (D) => (D.meta && D.meta.bahasa === "en");

function perkiraTinggiRef(teks) {
  return Math.ceil(teks.length / 135) * 0.2 + 0.12;
}

function susunSlide(D) {
  const M = D.meta;
  const en = EN(D);
  const hasil = [];
  hasil.push({ tipe: "sampul", judul: M.judul, catatan: M.catatan_sampul || "", pembicara: M.pembicara_sampul, durasi: M.durasi_sampul });
  for (const s of D.slide || []) hasil.push(s);
  if (D.pustaka && D.pustaka.length) {
    let chunk = [], tinggi = 0;
    const potong = [];
    for (const e of D.pustaka) {
      const h = perkiraTinggiRef(e);
      if (chunk.length && (tinggi + h > 4.7 || chunk.length >= 8)) { potong.push(chunk); chunk = []; tinggi = 0; }
      chunk.push(e); tinggi += h;
    }
    if (chunk.length) potong.push(chunk);
    potong.forEach((c, i) => hasil.push({
      tipe: "referensi", judul: en ? "References" : "Referensi", entri: c,
      catatan: (D.catatan_referensi && i === 0) ? D.catatan_referensi : "",
    }));
  }
  hasil.push({ tipe: "penutup", judul: en ? "Thank You" : "Terima Kasih", catatan: M.catatan_penutup || "", pembicara: M.pembicara_penutup, durasi: M.durasi_penutup });
  return hasil;
}

function teksNotes(s, en) {
  const baris = [];
  if (s.pembicara) baris.push(en ? `Speaker: ${s.pembicara} | Duration: ±${s.durasi} min` : `Pembicara: ${s.pembicara} | Durasi: ±${s.durasi} menit`);
  baris.push(s.catatan || "");
  return baris.join("\n\n");
}

function hitungKata(teks) {
  return (teks || "").trim().split(/\s+/).filter(Boolean).length;
}

module.exports = { susunSlide, teksNotes, hitungKata, EN };
