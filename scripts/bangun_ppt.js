#!/usr/bin/env node
// SPDX-License-Identifier: GPL-3.0-or-later
// Membangun .pptx mentah dari isi.json (lihat SKILL.md, "Format isi.json").
//   node bangun_ppt.js isi.json PPT-mentah.pptx
// Sesudahnya jalankan add_morph.py. Jika require('pptxgenjs') gagal: NODE_PATH=$(npm root -g)
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const sharp = require("sharp");
const { susunSlide, teksNotes, hitungKata, EN } = require("./susun.js");

const ASET = path.join(__dirname, "..", "aset");
const W = 13.333, H = 7.5, MX = 0.7, CW = W - 2 * MX;
const Y0 = 1.85, Y1 = 6.75;
const PERINGATAN = [];
const peringatan = (m) => { PERINGATAN.push(m); console.error("PERINGATAN: " + m); };

// ---------- ikon ----------
const cacheIkon = {};
let petaIkon = null;
function pilihIkon(teks, bawaan = "lightbulb") {
  if (!petaIkon) petaIkon = JSON.parse(fs.readFileSync(path.join(ASET, "kata_ikon.json"), "utf8"));
  const t = (teks || "").toLowerCase();
  let best = bawaan, skor = 0;
  for (const [nama, kata] of petaIkon) {
    const s = kata.split(" ").filter((k) => t.includes(k)).length;
    if (s > skor) { best = nama; skor = s; }
  }
  return best;
}
async function ikonData(nama, hex) {
  const key = nama + hex;
  if (cacheIkon[key]) return cacheIkon[key];
  let file = path.join(ASET, "ikon", nama + ".png");
  if (!fs.existsSync(file)) { peringatan(`ikon '${nama}' tidak ada, dipakai 'lightbulb'`); file = path.join(ASET, "ikon", "lightbulb.png"); }
  const meta = await sharp(file).metadata();
  const buf = await sharp({ create: { width: meta.width, height: meta.height, channels: 4, background: "#" + hex } })
    .composite([{ input: file, blend: "dest-in" }]).png().toBuffer();
  return (cacheIkon[key] = "image/png;base64," + buf.toString("base64"));
}
async function ukuranGambar(file) {
  const m = await sharp(file).metadata();
  return { w: m.width, h: m.height };
}

// ---------- utilitas ----------
function lum(h) { const c = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; const r = parseInt(h.slice(0, 2), 16), g = parseInt(h.slice(2, 4), 16), b = parseInt(h.slice(4, 6), 16); return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b); }
function kontras(a, b) { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
const perkiraBaris = (teks, pt, lebar) => Math.max(1, Math.ceil((teks || "").length / Math.max(1, lebar / (pt * 0.0078))));

async function main(isiPath, keluar) {
  const D = JSON.parse(fs.readFileSync(isiPath, "utf8"));
  const T = D.gaya, M = D.meta, en = EN(D);
  const FJ = T.font_judul, FI = T.font_isi;
  const slides = susunSlide(D);
  const N = slides.length;
  const agendaIdx = slides.findIndex((x) => x.tipe === "agenda");
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.title = M.judul;
  pres.author = (M.anggota || []).join(", ");
  pres.theme = { headFontFace: FJ, bodyFontFace: FI };
  const themed = T.mode === "tema";
  const JK = kontras(T.judul, T.card) >= 4.5 ? T.judul : T.ink; // warna judul di atas kartu
  const alphaKartu = T.latar ? 6 : 0;

  const orbPos = [[10.9, -1.3, 3.8], [-1.5, 5.3, 3.6], [10.4, 5.2, 4.0], [-1.2, -1.2, 3.2], [5.8, 5.9, 3.0]];
  const kecilPos = [[12.3, 6.3], [0.3, 6.4], [12.2, 1.0], [6.4, 0.25], [0.35, 3.4]];

  const ukur = {};
  async function gambarInfo(f) { return ukur[f] || (ukur[f] = await ukuranGambar(f)); }

  // ----- kerangka umum (6 objek Morph) -----
  async function kerangka(s, idx, judul, o = {}) {
    const hero = !!o.hero;
    const polosHero = hero && !themed;
    s.background = (hero && T.poster) ? { path: T.poster } : (!hero && T.latar) ? { path: T.latar } : { color: polosHero ? T.utama : T.bg };
    const warnaOrb = polosHero ? T.teks_di_utama : T.utama;
    const op = orbPos[idx % orbPos.length], kp = kecilPos[idx % kecilPos.length];
    const bigOrb = o.orb || op;
    s.addShape(pres.shapes.OVAL, { x: bigOrb[0], y: bigOrb[1], w: bigOrb[2], h: bigOrb[2], fill: { color: warnaOrb, transparency: T.latar ? 92 : 90 }, line: { type: "none" }, objectName: "!!orb" });
    s.addShape(pres.shapes.OVAL, { x: kp[0], y: kp[1], w: 0.5, h: 0.5, fill: { color: warnaOrb, transparency: 80 }, line: { type: "none" }, objectName: "!!orbKecil" });
    if (o.panel && themed) kartu(s, ...o.panel, "panel");
    const jT = o.judulPos || { x: MX, y: 0.4, w: 10.9, h: 0.9, fs: 32 };
    const warnaJ = polosHero ? T.teks_di_utama : (hero ? JK : T.judul);
    if (!o.lewatJudul) s.addText(judul || "", { x: jT.x, y: jT.y, w: jT.w, h: jT.h, fontFace: FJ, fontSize: jT.fs, bold: true, color: o.judulWarna || warnaJ, valign: "middle", margin: 0, isTextBox: true, objectName: "!!judul" });
    const gp = o.garisPos || { x: MX, y: 1.38, w: 1.1 };
    if (!o.lewatGaris) s.addShape(pres.shapes.RECTANGLE, { x: gp.x, y: gp.y, w: gp.w, h: 0.06, fill: { color: polosHero ? T.teks_di_utama : T.aksen }, line: { type: "none" }, objectName: "!!garisJudul" });
    const ip = o.ikonPos || { x: 12.0, y: 0.42, w: 0.75 };
    const ikonNama = o.ikon || pilihIkon((judul || "") + " " + (o.konteks || ""));
    if (!o.lewatIkon) s.addImage({ data: await ikonData(ikonNama, polosHero ? T.teks_di_utama : T.utama), x: ip.x, y: ip.y, w: ip.w, h: ip.w, objectName: "!!ikon", altText: "" });
    s.addText(M.footer || "", { x: MX, y: 7.0, w: 9, h: 0.3, fontFace: FI, fontSize: 11, color: polosHero ? T.teks_di_utama : T.muted, margin: 0, valign: "middle", isTextBox: true, objectName: "!!footer" });
    if (!hero) s.slideNumber = { x: 12.0, y: 7.0, w: 0.65, h: 0.3, fontFace: FI, fontSize: 11, color: T.muted, align: "right" };
    // Nomor halaman bisa diklik untuk kembali ke Agenda (hanya jika ada Agenda; bukan di Agenda itu sendiri)
    if (!hero && agendaIdx >= 0 && idx !== agendaIdx) {
      s.addShape(pres.shapes.RECTANGLE, { x: 11.75, y: 6.95, w: 1.0, h: 0.4, fill: { color: "FFFFFF", transparency: 100 }, line: { type: "none" }, hyperlink: { slide: agendaIdx + 1, tooltip: en ? "Back to Agenda" : "Kembali ke Agenda" }, objectName: "kembaliAgenda" });
    }
  }

  function kartu(s, x, y, w, h, nama) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y, w, h, rectRadius: T.radius, fill: { color: T.card, transparency: alphaKartu },
      line: T.garis ? { color: T.garis, width: 0.5 } : { color: T.utama, width: 0.5, transparency: 70 },
      objectName: nama,
    });
  }
  function kotakUtama(s, x, y, w, h, nama) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: T.radius, fill: { color: T.utama }, line: { type: "none" }, objectName: nama });
  }
  const sumberCap = (s, teks, y = 6.5) => teks && s.addText(teks, { x: MX, y, w: CW, h: 0.35, fontFace: FI, fontSize: 12, italic: true, color: T.muted, margin: 0, valign: "middle", isTextBox: true, objectName: "sumber" });
  async function lingkarIkon(s, nama, x, y, d, objName) {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: T.utama }, line: { type: "none" }, objectName: objName + "Lingkar" });
    const k = d * 0.22;
    s.addImage({ data: await ikonData(nama, T.teks_di_utama), x: x + k, y: y + k, w: d - 2 * k, h: d - 2 * k, objectName: objName, altText: "" });
  }

  // ---------- tipe slide ----------
  const tipe = {};

  tipe.sampul = async (s, d, i) => {
    const px = 0.7, py = 0.55, pw = themed ? 8.8 : 9.6, ph = 6.25;
    await kerangka(s, i, "", { hero: true, panel: [px, py, pw, ph], lewatJudul: true, lewatGaris: true, lewatIkon: true });
    const ink = themed ? T.ink : T.teks_di_utama, jud = themed ? JK : T.teks_di_utama, mut = themed ? T.muted : T.teks_di_utama;
    const ix = px + 0.5, iw = pw - 1.0;
    let y = py + 0.4;
    if (M.logo && fs.existsSync(M.logo)) {
      const g = await gambarInfo(M.logo), tinggi = 0.85, lebar = Math.min(2.2, tinggi * g.w / g.h);
      s.addImage({ path: M.logo, x: ix, y, w: lebar, h: lebar * g.h / g.w, altText: M.logo_alt || "Logo", objectName: "logo" });
      y += 1.0;
    } else y += 0.1;
    s.addText((M.jenis || (en ? "PAPER" : "MAKALAH")).toUpperCase(), { x: ix, y, w: iw, h: 0.35, fontFace: FI, fontSize: 13, bold: true, charSpacing: 4, color: mut, margin: 0, isTextBox: true, objectName: "jenis" });
    y += 0.4;
    const baris = perkiraBaris(M.judul, 32, iw);
    const hj = Math.min(2.0, 0.62 * baris + 0.15);
    s.addText(M.judul, { x: ix, y, w: iw, h: hj, fontFace: FJ, fontSize: baris > 2 ? 28 : 32, bold: true, color: jud, valign: "top", margin: 0, isTextBox: true, objectName: "!!judul" });
    // objek morph cadangan di luar layar agar nama tetap konsisten
    s.addShape(pres.shapes.RECTANGLE, { x: ix, y: y + hj + 0.05, w: 1.1, h: 0.06, fill: { color: themed ? T.aksen : T.teks_di_utama }, line: { type: "none" }, objectName: "!!garisJudul" });
    s.addImage({ data: await ikonData("presentation", themed ? T.utama : T.teks_di_utama), x: px + pw - 1.25, y: py + 0.35, w: 0.75, h: 0.75, objectName: "!!ikon", altText: "" });
    y += hj + 0.3;
    const ket = [M.keterangan, M.dosen ? (en ? "Lecturer: " : "Dosen Pengampu: ") + M.dosen : null].filter(Boolean).join("\n");
    if (ket) { s.addText(ket, { x: ix, y, w: iw, h: 0.85, fontFace: FI, fontSize: 16, color: ink, valign: "top", margin: 0, isTextBox: true, objectName: "keterangan" }); y += 0.95; }
    const nama = [M.kelompok, (M.anggota || []).join(" · ")].filter(Boolean).join("\n");
    if (nama) { s.addText(nama, { x: ix, y, w: iw, h: 1.0, fontFace: FI, fontSize: 16, bold: false, color: ink, valign: "top", margin: 0, isTextBox: true, objectName: "anggota" }); y += 1.05; }
    const inst = (M.institusi || []).join("\n");
    if (inst) s.addText(inst, { x: ix, y: py + ph - 1.1, w: iw, h: 0.85, fontFace: FI, fontSize: 13, bold: true, color: mut, valign: "top", margin: 0, isTextBox: true, objectName: "institusi" });
  };

  tipe.penutup = async (s, d, i) => {
    await kerangka(s, i, d.judul, { hero: true, panel: [0.7, 1.7, 11.93, 3.9], judulPos: { x: 1.2, y: 2.4, w: 7.5, h: 1.3, fs: 54 }, garisPos: { x: 1.2, y: 3.8, w: 1.6 }, ikonPos: { x: 10.9, y: 2.4, w: 1.2 }, ikon: "heart-handshake" });
    const ink = themed ? T.ink : T.teks_di_utama;
    s.addText(en ? "Q & A" : "Tanya Jawab", { x: 1.2, y: 4.1, w: 7.5, h: 0.7, fontFace: FI, fontSize: 28, color: ink, margin: 0, valign: "middle", isTextBox: true, objectName: "tanyaJawab" });
    if (M.foto && fs.existsSync(M.foto)) {
      const g = await gambarInfo(M.foto);
      let w = 4.3, h = w * g.h / g.w; if (h > 3.6) { h = 3.6; w = h * g.w / g.h; }
      s.addImage({ path: M.foto, x: 8.9, y: 2.3, w, h, altText: M.foto_alt || "Foto dokumentasi", objectName: "foto" });
    }
  };

  tipe.bagian = async (s, d, i) => {
    const nomor = d._nomor || "";
    await kerangka(s, i, d.judul, { hero: true, panel: [0.7, 1.5, 11.93, 4.6], judulPos: { x: 1.2, y: 3.2, w: 9.2, h: 1.2, fs: 46 }, garisPos: { x: 1.2, y: 4.5, w: 1.6 }, ikonPos: { x: 10.8, y: 2.3, w: 1.5 }, ikon: d.ikon, konteks: d.sub });
    const pol = !themed;
    s.addText(String(nomor).padStart(2, "0"), { x: 1.2, y: 1.8, w: 4, h: 1.3, fontFace: FJ, fontSize: 72, bold: true, color: pol ? T.teks_di_utama : T.utama, margin: 0, valign: "middle", isTextBox: true, objectName: "nomorBagian" });
    if (d.sub) s.addText(d.sub, { x: 1.2, y: 4.75, w: 9.2, h: 0.9, fontFace: FI, fontSize: 20, color: pol ? T.teks_di_utama : T.ink, margin: 0, valign: "top", isTextBox: true, objectName: "subBagian" });
  };

  tipe.agenda = async (s, d, i) => {
    const bagian = slides.map((x, k) => ({ x, k })).filter((o) => o.x.tipe === "bagian");
    await kerangka(s, i, d.judul || (en ? "Agenda" : "Alur Presentasi"), { ikon: "list-checks" });
    const n = bagian.length, gap = 0.2, h = Math.min(1.0, (Y1 - Y0 - gap * (n - 1)) / n);
    for (let r = 0; r < n; r++) {
      const y = Y0 + r * (h + gap), b = bagian[r];
      kartu(s, MX, y, CW, h, "agendaKartu" + (r + 1));
      s.addShape(pres.shapes.OVAL, { x: MX + 0.25, y: y + (h - 0.6) / 2, w: 0.6, h: 0.6, fill: { color: T.utama }, line: { type: "none" }, objectName: "agendaNo" + (r + 1) });
      s.addText(String(r + 1), { x: MX + 0.25, y: y + (h - 0.6) / 2, w: 0.6, h: 0.6, align: "center", valign: "middle", fontFace: FJ, fontSize: 20, bold: true, color: T.teks_di_utama, margin: 0, isTextBox: true, objectName: "agendaAngka" + (r + 1) });
      const teks = [{ text: b.x.judul, options: { fontSize: 22, bold: true, color: JK, fontFace: FJ, breakLine: !!b.x.sub } }];
      if (b.x.sub) teks.push({ text: b.x.sub, options: { fontSize: 16, color: T.ink, fontFace: FI } });
      s.addText(teks, { x: MX + 1.1, y, w: CW - 1.4, h, valign: "middle", margin: 0, isTextBox: true, objectName: "agendaTeks" + (r + 1) });
      s.addShape(pres.shapes.RECTANGLE, { x: MX, y, w: CW, h, fill: { color: "FFFFFF", transparency: 100 }, line: { type: "none" }, hyperlink: { slide: b.k + 1, tooltip: b.x.judul }, objectName: "agendaLink" + (r + 1) });
    }
  };

  tipe.poin = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon, konteks: (d.poin || []).join(" ") });
    const p = d.poin || [], n = p.length, gap = 0.22, h = Math.min(1.15, (Y1 - Y0 - gap * (n - 1)) / n);
    if (n > 5) peringatan(`slide '${d.judul}' punya ${n} poin (maksimal 5)`);
    for (let r = 0; r < n; r++) {
      const y = Y0 + r * (h + gap);
      kartu(s, MX, y, CW, h, "poinKartu" + (r + 1));
      s.addShape(pres.shapes.OVAL, { x: MX + 0.3, y: y + (h - 0.62) / 2, w: 0.62, h: 0.62, fill: { color: T.utama }, line: { type: "none" }, objectName: "poinNo" + (r + 1) });
      s.addText(String(r + 1), { x: MX + 0.3, y: y + (h - 0.62) / 2, w: 0.62, h: 0.62, align: "center", valign: "middle", fontFace: FJ, fontSize: 20, bold: true, color: T.teks_di_utama, margin: 0, isTextBox: true, objectName: "poinAngka" + (r + 1) });
      s.addText(p[r], { x: MX + 1.2, y, w: CW - 1.6, h, valign: "middle", fontFace: FI, fontSize: 20, color: T.ink, margin: 0, isTextBox: true, objectName: "poinTeks" + (r + 1) });
    }
  };

  tipe.kartu = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon, konteks: JSON.stringify(d.kartu) });
    const k = d.kartu || [], n = k.length, gap = 0.3;
    const kol = n <= 3 ? n : 2, bar = Math.ceil(n / kol);
    const w = (CW - gap * (kol - 1)) / kol, h = Math.min(bar === 1 ? 3.6 : 9, (Y1 - Y0 - gap * (bar - 1)) / bar);
    for (let r = 0; r < n; r++) {
      const cx = r % kol, cy = Math.floor(r / kol), x = MX + cx * (w + gap), y = Y0 + cy * (h + gap);
      kartu(s, x, y, w, h, "kartu" + (r + 1));
      const ik = k[r].ikon || pilihIkon(k[r].j + " " + k[r].t);
      await lingkarIkon(s, ik, x + 0.3, y + 0.28, 0.7, "kartuIkon" + (r + 1));
      s.addText(k[r].j, { x: x + 1.15, y: y + 0.28, w: w - 1.4, h: 0.7, valign: "middle", fontFace: FJ, fontSize: 20, bold: true, color: JK, margin: 0, isTextBox: true, objectName: "kartuJudul" + (r + 1) });
      s.addText(k[r].t, { x: x + 0.3, y: y + 1.1, w: w - 0.6, h: h - 1.3, valign: "top", fontFace: FI, fontSize: 18, color: T.ink, margin: 0, isTextBox: true, objectName: "kartuTeks" + (r + 1) });
    }
  };

  tipe.garis = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon || "route", konteks: JSON.stringify(d.titik) });
    const t = d.titik || [], n = t.length, gap = 0.3, w = (CW - gap * (n - 1)) / n;
    const maxBaris = Math.max(...t.map((q) => perkiraBaris(q.t, 18, w - 0.5)));
    const hKartu = Math.min(Y1 - Y0 - 0.95, Math.max(2.8, 1.5 + 0.34 * maxBaris + 0.3));
    s.addShape(pres.shapes.RECTANGLE, { x: MX + w / 2, y: Y0 + 0.28, w: CW - w, h: 0.06, fill: { color: T.utama, transparency: 40 }, line: { type: "none" }, objectName: "garisWaktu" });
    for (let r = 0; r < n; r++) {
      const x = MX + r * (w + gap);
      s.addShape(pres.shapes.OVAL, { x: x + w / 2 - 0.31, y: Y0, w: 0.62, h: 0.62, fill: { color: T.utama }, line: { type: "none" }, objectName: "titik" + (r + 1) });
      s.addText(String(r + 1), { x: x + w / 2 - 0.31, y: Y0, w: 0.62, h: 0.62, align: "center", valign: "middle", fontFace: FJ, fontSize: 20, bold: true, color: T.teks_di_utama, margin: 0, isTextBox: true, objectName: "titikAngka" + (r + 1) });
      kartu(s, x, Y0 + 0.95, w, hKartu, "tahap" + (r + 1));
      s.addText(t[r].j, { x: x + 0.25, y: Y0 + 1.1, w: w - 0.5, h: 0.7, valign: "middle", fontFace: FJ, fontSize: 20, bold: true, color: JK, margin: 0, isTextBox: true, objectName: "tahapJudul" + (r + 1) });
      s.addText(t[r].t, { x: x + 0.25, y: Y0 + 1.85, w: w - 0.5, h: hKartu - 1.05, valign: "top", fontFace: FI, fontSize: 18, color: T.ink, margin: 0, isTextBox: true, objectName: "tahapTeks" + (r + 1) });
    }
  };

  // langkah: alur proses 2 sampai 5 tahap, panah berurutan, tiap tahap punya nomor, judul, dan penjelasan
  tipe.langkah = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon || "workflow", konteks: JSON.stringify(d.langkah) });
    const t = d.langkah || [], n = t.length, gap = 0.3;
    if (n < 2 || n > 5) peringatan(`slide langkah '${d.judul}' punya ${n} tahap (seharusnya 2 sampai 5)`);
    const w = (CW - gap * (n - 1)) / n;
    const maxBaris = Math.max(...t.map((q) => perkiraBaris(q.t, 18, w - 0.5)));
    const hKepala = 1.15, hKartu = Math.min(Y1 - Y0 - hKepala - 0.2, Math.max(2.4, 0.5 + 0.34 * maxBaris + 0.3));
    for (let r = 0; r < n; r++) {
      const x = MX + r * (w + gap);
      // kepala berbentuk panah: nomor + judul tahap
      s.addShape(r === n - 1 ? pres.shapes.ROUNDED_RECTANGLE : pres.shapes.PENTAGON, { x, y: Y0, w: w + (r === n - 1 ? 0 : gap * 0.6), h: hKepala, fill: { color: T.utama }, line: { type: "none" }, rectRadius: T.radius, objectName: "langkahKepala" + (r + 1) });
      s.addText([{ text: String(r + 1).padStart(2, "0"), options: { fontSize: 22, bold: true, breakLine: true } }, { text: t[r].j, options: { fontSize: 18, bold: true } }], { x: x + 0.2, y: Y0, w: w - 0.45, h: hKepala, valign: "middle", fontFace: FJ, color: T.teks_di_utama, margin: 0, isTextBox: true, objectName: "langkahJudul" + (r + 1) });
      kartu(s, x, Y0 + hKepala + 0.2, w, hKartu, "langkahKartu" + (r + 1));
      s.addText(t[r].t, { x: x + 0.25, y: Y0 + hKepala + 0.35, w: w - 0.5, h: hKartu - 0.3, valign: "top", fontFace: FI, fontSize: 18, color: T.ink, margin: 0, isTextBox: true, objectName: "langkahTeks" + (r + 1) });
    }
  };

  tipe.dua = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon || "scale", konteks: JSON.stringify([d.kiri, d.kanan]) });
    const gap = 0.35, w = (CW - gap) / 2;
    const maxP = Math.max(d.kiri.poin.length, d.kanan.poin.length), baris = Math.max(...[...d.kiri.poin, ...d.kanan.poin].map((q) => perkiraBaris(q, 18, w - 1.0)));
    const h = Math.min(Y1 - Y0, 1.3 + maxP * (0.36 * baris + 0.2));
    [d.kiri, d.kanan].forEach((kol, r) => {
      const x = MX + r * (w + gap);
      kartu(s, x, Y0, w, h, "kolom" + (r + 1));
      s.addText(kol.j, { x: x + 0.35, y: Y0 + 0.2, w: w - 0.7, h: 0.7, valign: "middle", fontFace: FJ, fontSize: 24, bold: true, color: JK, margin: 0, isTextBox: true, objectName: "kolomJudul" + (r + 1) });
      const runs = kol.poin.map((p, q) => ({ text: p, options: { bullet: true, breakLine: q < kol.poin.length - 1, paraSpaceAfter: 10 } }));
      s.addText(runs, { x: x + 0.35, y: Y0 + 1.0, w: w - 0.7, h: h - 1.2, valign: "top", fontFace: FI, fontSize: 18, color: T.ink, margin: 0, isTextBox: true, objectName: "kolomTeks" + (r + 1) });
    });
  };

  tipe.definisi = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon || "book-open", konteks: d.teks });
    kotakUtama(s, MX, Y0 + 0.1, CW, 3.9, "definisiKotak");
    const fs_ = d.teks.length > 220 ? 24 : d.teks.length > 130 ? 28 : 32;
    s.addText(d.teks, { x: MX + 0.6, y: Y0 + 0.3, w: CW - 1.2, h: 3.5, valign: "middle", fontFace: FI, fontSize: fs_, color: T.teks_di_utama, margin: 0, isTextBox: true, objectName: "definisiTeks" });
    sumberCap(s, d.sumber, Y0 + 4.2);
  };

  tipe.angka = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon || "chart-column", konteks: d.label });
    s.addText(d.angka, { x: MX, y: Y0 + 0.2, w: 6.0, h: 2.2, valign: "middle", fontFace: FJ, fontSize: 88, bold: true, color: T.judul, margin: 0, isTextBox: true, objectName: "angkaBesar" });
    s.addText(d.label, { x: MX, y: Y0 + 2.5, w: 6.0, h: 1.4, valign: "top", fontFace: FI, fontSize: 24, color: T.ink, margin: 0, isTextBox: true, objectName: "angkaLabel" });
    if (d.poin && d.poin.length) {
      kartu(s, 7.2, Y0, W - MX - 7.2, Math.min(Y1 - Y0 - 0.6, 0.7 + d.poin.length * 0.7), "angkaKartu");
      const runs = d.poin.map((p, q) => ({ text: p, options: { bullet: true, breakLine: q < d.poin.length - 1, paraSpaceAfter: 10 } }));
      s.addText(runs, { x: 7.55, y: Y0 + 0.3, w: W - MX - 7.9, h: Y1 - Y0 - 1.2, valign: "top", fontFace: FI, fontSize: 18, color: T.ink, margin: 0, isTextBox: true, objectName: "angkaPoin" });
    }
    sumberCap(s, d.sumber);
  };

  tipe.statistik = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon || "chart-column", konteks: JSON.stringify(d.data) });
    const n = d.data.length, gap = 0.3, w = (CW - gap * (n - 1)) / n, h = 3.9;
    d.data.forEach(([a, l], r) => {
      const x = MX + r * (w + gap);
      kartu(s, x, Y0 + 0.2, w, h, "statKartu" + (r + 1));
      s.addText(a, { x: x + 0.2, y: Y0 + 0.5, w: w - 0.4, h: 1.7, align: "center", valign: "middle", fontFace: FJ, fontSize: n > 3 ? 44 : 54, bold: true, color: JK, margin: 0, isTextBox: true, objectName: "statAngka" + (r + 1) });
      s.addText(l, { x: x + 0.25, y: Y0 + 2.3, w: w - 0.5, h: 1.6, align: "center", valign: "top", fontFace: FI, fontSize: 18, color: T.ink, margin: 0, isTextBox: true, objectName: "statLabel" + (r + 1) });
    });
    sumberCap(s, d.sumber);
  };

  tipe.grafik = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon || "chart-column", konteks: d.judul });
    const adaPoin = d.poin && d.poin.length, cw = adaPoin ? 7.6 : CW, ch = Y1 - Y0 - 0.45;
    kartu(s, MX, Y0, cw, ch, "grafikKartu");
    const jenis = { batang: pres.charts.BAR, "batang-h": pres.charts.BAR, garis: pres.charts.LINE, donat: pres.charts.DOUGHNUT, pie: pres.charts.PIE }[d.jenis] || pres.charts.BAR;
    const data = d.seri.map((q) => ({ name: q.nama, labels: d.label, values: q.nilai }));
    const bulat = d.jenis === "donat" || d.jenis === "pie";
    const fmt = d.satuan ? `0.##"${d.satuan}"` : "General";
    const opt = {
      x: MX + 0.2, y: Y0 + 0.2, w: cw - 0.4, h: ch - 0.4, chartColors: bulat ? [...T.seri, ...T.seri] : T.seri,
      showLegend: bulat || d.seri.length > 1, legendPos: "b", legendColor: T.ink, legendFontFace: FI, legendFontSize: 14,
      showTitle: false, dataLabelColor: T.ink, dataLabelFontFace: FI, dataLabelFontSize: 14, dataLabelFormatCode: fmt,
      catAxisLabelColor: T.ink, valAxisLabelColor: T.ink, catAxisLabelFontFace: FI, valAxisLabelFontFace: FI,
      catAxisLabelFontSize: 14, valAxisLabelFontSize: 12, valGridLine: { color: T.muted, size: 0.25 }, catGridLine: { style: "none" },
    };
    if (bulat) { opt.showPercent = true; opt.showValue = false; opt.dataLabelColor = T.teks_di_utama; }
    else { opt.showValue = true; opt.dataLabelPosition = "outEnd"; }
    if (d.jenis === "batang" || d.jenis === "batang-h") opt.barDir = d.jenis === "batang-h" ? "bar" : "col";
    if (d.jenis === "donat") opt.holeSize = 55;
    s.addChart(jenis, data, opt);
    if (adaPoin) {
      kartu(s, 8.55, Y0, W - MX - 8.55, ch, "grafikPoinKartu");
      const runs = d.poin.map((p, q) => ({ text: p, options: { bullet: true, breakLine: q < d.poin.length - 1, paraSpaceAfter: 10 } }));
      s.addText(runs, { x: 8.85, y: Y0 + 0.3, w: W - MX - 9.15, h: ch - 0.6, valign: "top", fontFace: FI, fontSize: 18, color: T.ink, margin: 0, isTextBox: true, objectName: "grafikPoin" });
    }
    sumberCap(s, d.sumber, Y1 - 0.3);
  };

  tipe.tabel = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon || "database", konteks: d.judul });
    if (d.baris.length > 5 || d.kolom.length > 4) peringatan(`tabel '${d.judul}' melebihi 5 baris x 4 kolom`);
    const sel = (t, o = {}) => ({ text: String(t), options: { fontFace: FI, fontSize: 18, color: T.ink, fill: { color: T.card }, valign: "middle", ...o } });
    const rows = [d.kolom.map((k) => sel(k, { bold: true, color: T.teks_di_utama, fill: { color: T.utama } })), ...d.baris.map((b) => b.map((c) => sel(c)))];
    const w = CW / d.kolom.length;
    s.addTable(rows, { x: MX, y: Y0 + 0.1, w: CW, colW: d.kolom.map(() => w), rowH: 0.75, border: { type: "solid", color: T.muted, pt: 0.5 }, margin: [0, 0.15, 0, 0.15], objectName: "tabel" });
    sumberCap(s, d.sumber);
  };

  tipe.kutipan = async (s, d, i) => {
    await kerangka(s, i, d.judul || (en ? "Quote" : "Kutipan"), { ikon: "quote" });
    kartu(s, MX, Y0, CW, 3.9, "kutipanKartu");
    await lingkarIkon(s, "quote", MX + 0.4, Y0 + 0.35, 0.8, "kutipanIkon");
    s.addText(d.teks, { x: MX + 1.5, y: Y0 + 0.3, w: CW - 2.0, h: 2.8, valign: "middle", fontFace: FI, fontSize: d.teks.length > 160 ? 24 : 28, italic: true, color: T.ink, margin: 0, isTextBox: true, objectName: "kutipanTeks" });
    if (d.oleh) s.addText("— " + d.oleh, { x: MX + 1.5, y: Y0 + 3.1, w: CW - 2.0, h: 0.6, valign: "middle", fontFace: FI, fontSize: 18, bold: true, color: JK, margin: 0, isTextBox: true, objectName: "kutipanOleh" });
  };

  tipe.gambar = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon || "layers", konteks: d.keterangan });
    if (!d.alt) peringatan(`gambar di slide '${d.judul}' belum punya alt text`);
    const g = await gambarInfo(d.file), adaPoin = d.poin && d.poin.length;
    const bw = adaPoin ? 7.4 : CW, bh = Y1 - Y0 - 0.5;
    kartu(s, MX, Y0, bw, bh, "gambarKartu");
    let w = bw - 0.4, h = w * g.h / g.w; if (h > bh - 0.4) { h = bh - 0.4; w = h * g.w / g.h; }
    s.addImage({ path: d.file, x: MX + (bw - w) / 2, y: Y0 + (bh - h) / 2, w, h, altText: d.alt || "", objectName: "gambar" });
    if (d.keterangan) s.addText(d.keterangan, { x: MX, y: Y0 + bh + 0.05, w: bw, h: 0.4, fontFace: FI, fontSize: 12, italic: true, color: T.muted, margin: 0, valign: "middle", isTextBox: true, objectName: "keteranganGambar" });
    if (adaPoin) {
      kartu(s, 8.3, Y0, W - MX - 8.3, bh, "gambarPoinKartu");
      const runs = d.poin.map((p, q) => ({ text: p, options: { bullet: true, breakLine: q < d.poin.length - 1, paraSpaceAfter: 10 } }));
      s.addText(runs, { x: 8.6, y: Y0 + 0.3, w: W - MX - 8.9, h: bh - 0.6, valign: "top", fontFace: FI, fontSize: 18, color: T.ink, margin: 0, isTextBox: true, objectName: "gambarPoin" });
    }
  };

  // contoh: soal di kotak utama, langkah (teks atau rumus PNG) di kartu, jawaban di bawah
  tipe.contoh = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: d.ikon || "calculator", konteks: (d.soal || "") });
    const lSoal = perkiraBaris(d.soal, 20, CW - 1.0), hSoal = Math.min(1.5, 0.42 * lSoal + 0.3);
    kotakUtama(s, MX, Y0, CW, hSoal, "contohSoalKotak");
    s.addText(d.soal, { x: MX + 0.4, y: Y0, w: CW - 0.8, h: hSoal, valign: "middle", fontFace: FI, fontSize: 20, color: T.teks_di_utama, margin: 0, isTextBox: true, objectName: "contohSoal" });
    const yK = Y0 + hSoal + 0.2, hJ = d.jawab ? 0.8 : 0, hK = Y1 - yK - (hJ ? hJ + 0.2 : 0);
    kartu(s, MX, yK, CW, hK, "contohKartu");
    let y = yK + 0.2; const x = MX + 0.4, iw = CW - 0.8;
    const skala = d.skalaRumus || 0.85;
    let n = 0;
    for (const it of d.isi || []) {
      n++;
      if (typeof it === "string") {
        const h = perkiraBaris(it, 20, iw) * 0.4 + 0.1;
        s.addText(it, { x, y, w: iw, h, valign: "middle", fontFace: FI, fontSize: 20, color: T.ink, margin: 0, isTextBox: true, objectName: "contohTeks" + n });
        y += h + 0.08;
      } else {
        const g = await gambarInfo(it.rumus);
        let w = g.w / 300 * skala * (it.skala || 1), h = g.h / 300 * skala * (it.skala || 1);
        if (w > iw) { h *= iw / w; w = iw; }
        s.addImage({ path: it.rumus, x, y, w, h, altText: it.alt || "Rumus", objectName: "contohRumus" + n });
        y += h + 0.14;
      }
    }
    if (y > yK + hK) peringatan(`slide contoh '${d.judul}' terlalu panjang (sisa ${(y - yK - hK).toFixed(2)} inci); pecah jadi dua slide`);
    if (d.jawab) {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: Y1 - hJ, w: CW, h: hJ, rectRadius: T.radius, fill: { color: T.card, transparency: alphaKartu }, line: { color: T.utama, width: 2 }, objectName: "jawabKotak" });
      s.addText(d.jawab, { x: MX + 0.4, y: Y1 - hJ, w: CW - 0.8, h: hJ, valign: "middle", fontFace: FI, fontSize: 20, bold: true, color: JK, margin: 0, isTextBox: true, objectName: "jawabTeks" });
    }
  };

  tipe.referensi = async (s, d, i) => {
    await kerangka(s, i, d.judul, { ikon: "library" });
    const hRef = Math.min(Y1 - Y0, 0.5 + d.entri.reduce((a, e) => a + Math.ceil(e.length / 135) * 0.2 + 0.1, 0));
    kartu(s, MX, Y0, CW, hRef, "referensiKartu");
    const runs = d.entri.map((e, q) => ({ text: e, options: { breakLine: q < d.entri.length - 1, paraSpaceAfter: 6 } }));
    s.addText(runs, { x: MX + 0.35, y: Y0 + 0.2, w: CW - 0.7, h: hRef - 0.4, valign: "top", fontFace: FI, fontSize: 12, color: T.ink, margin: 0, isTextBox: true, objectName: "referensiTeks" });
  };

  // ---------- bangun ----------
  let nomorBagian = 0, totalKata = 0;
  for (let i = 0; i < N; i++) {
    const d = slides[i];
    if (d.tipe === "bagian") d._nomor = ++nomorBagian;
    const f = tipe[d.tipe];
    if (!f) throw new Error(`Tipe slide tidak dikenal: ${d.tipe}`);
    const s = pres.addSlide();
    await f(s, d, i);
    const catatan = teksNotes(d, en);
    if (!(d.catatan || "").trim() && d.tipe !== "referensi") peringatan(`slide ${i + 1} (${d.judul || d.tipe}) belum punya catatan`);
    s.addNotes(catatan);
    totalKata += hitungKata(d.catatan);
  }
  await pres.writeFile({ fileName: keluar });
  console.log(`OK ${keluar}: ${N} slide, ${totalKata} kata naskah (~${(totalKata / 130).toFixed(1)} menit)`);
  if (PERINGATAN.length) console.log(`${PERINGATAN.length} peringatan (lihat stderr).`);
}

if (process.argv.length < 4) { console.error("Pemakaian: node bangun_ppt.js isi.json PPT-mentah.pptx"); process.exit(1); }
main(process.argv[2], process.argv[3]).catch((e) => { console.error(e); process.exit(1); });
