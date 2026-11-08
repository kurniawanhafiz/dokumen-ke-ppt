#!/usr/bin/env node
// Membuat dokumen Speaker Notes (.docx) dari isi.json yang sama dengan PPT.
//   node buat_notes.js isi.json "Speaker Notes - [judul].docx"
// Isi: judul, perkiraan durasi, (tabel pembicara jika --bagi), naskah per slide, Pertanyaan Antisipasi.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, HeadingLevel, BorderStyle,
} = require("docx");
const { susunSlide, hitungKata, EN } = require("./susun.js");

async function main(isi, keluar) {
  const D = JSON.parse(fs.readFileSync(isi, "utf8"));
  const en = EN(D), M = D.meta;
  const slides = susunSlide(D);
  const F = "Times New Roman";
  const total = slides.reduce((a, s) => a + hitungKata(s.catatan), 0);
  const menit = Math.round(total / 130);
  const bagi = slides.some((s) => s.pembicara);
  const L = en
    ? { judul: "Speaker Notes", est: "Estimated total duration", min: "minutes", w: "words", sl: "Slide", pb: "Speaker", du: "Duration", tj: "Title", qa: "Anticipated Questions", t: "Total", q: "Q", a: "A", who: "Suggested answerer", slideT: "Title", closeT: "Thank You" }
    : { judul: "Speaker Notes", est: "Perkiraan total durasi", min: "menit", w: "kata", sl: "Slide", pb: "Pembicara", du: "Durasi", tj: "Judul", qa: "Pertanyaan Antisipasi", t: "Total", q: "Tanya", a: "Jawab", who: "Sebaiknya dijawab oleh", slideT: "Judul", closeT: "Terima Kasih" };
  const anak = [];
  anak.push(new Paragraph({ heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, children: [new TextRun({ text: `${L.judul}: ${M.judul}`, font: F, bold: true, size: 32 })] }));
  anak.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: `${L.est}: ±${menit} ${L.min} (±${total} ${L.w})`, font: F, size: 24, italics: true })] }));

  if (bagi) {
    const cw = [900, 4700, 2300, 1126];
    const sel = (t, i, o = {}) => new TableCell({ width: { size: cw[i], type: WidthType.DXA }, shading: o.head ? { fill: "D9D9D9", type: ShadingType.CLEAR, color: "auto" } : undefined, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ children: [new TextRun({ text: String(t), font: F, size: 22, bold: !!o.head })] })] });
    const rows = [new TableRow({ tableHeader: true, children: [L.sl, L.tj, L.pb, L.du].map((t, i) => sel(t, i, { head: true })) })];
    let totD = 0;
    slides.forEach((s, i) => { totD += Number(s.durasi) || 0; rows.push(new TableRow({ children: [String(i + 1), s.judul || "", s.pembicara || "", s.durasi ? `±${s.durasi} ${L.min}` : ""].map((t, k) => sel(t, k)) })); });
    rows.push(new TableRow({ children: ["", L.t, "", `±${totD} ${L.min}`].map((t, k) => sel(t, k, { head: true })) }));
    anak.push(new Table({ width: { size: 9026, type: WidthType.DXA }, columnWidths: cw, rows }));
    anak.push(new Paragraph({ children: [] }));
  }

  slides.forEach((s, i) => {
    const nama = s.tipe === "sampul" ? L.slideT : s.judul;
    anak.push(new Paragraph({ heading: HeadingLevel.HEADING_1, keepNext: true, children: [new TextRun({ text: `${L.sl} ${i + 1}: ${nama}`, font: F, bold: true, size: 26 })] }));
    if (s.pembicara) anak.push(new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: en ? `Speaker: ${s.pembicara} | Duration: ±${s.durasi} min` : `Pembicara: ${s.pembicara} | Durasi: ±${s.durasi} menit`, font: F, size: 24, bold: true })] }));
    (s.catatan || "").split(/\n\s*\n/).filter(Boolean).forEach((para) => anak.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 120, line: 360 }, children: [new TextRun({ text: para.trim(), font: F, size: 24 })] })));
  });

  if (D.tanya && D.tanya.length) {
    anak.push(new Paragraph({ heading: HeadingLevel.HEADING_1, keepNext: true, children: [new TextRun({ text: L.qa, font: F, bold: true, size: 26 })] }));
    D.tanya.forEach((t, i) => {
      anak.push(new Paragraph({ keepNext: true, spacing: { before: 160, after: 40 }, children: [new TextRun({ text: `${L.q} ${i + 1}. ${t.q}`, font: F, size: 24, bold: true })] }));
      if (t.oleh) anak.push(new Paragraph({ keepNext: true, spacing: { after: 40 }, children: [new TextRun({ text: `${L.who}: ${t.oleh}`, font: F, size: 22, italics: true })] }));
      anak.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 120, line: 360 }, children: [new TextRun({ text: `${L.a}: ${t.a}`, font: F, size: 24 })] }));
    });
  }

  const doc = new Document({
    creator: (M.anggota || []).join(", "), title: `${L.judul}: ${M.judul}`,
    styles: {
      default: { document: { run: { font: F, size: 24 } } },
      paragraphStyles: [
        { id: "Title", name: "Title", basedOn: "Normal", run: { font: F, size: 32, bold: true }, paragraph: { spacing: { before: 0, after: 120 }, keepNext: true } },
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: F, size: 26, bold: true }, paragraph: { spacing: { before: 280, after: 120 }, keepNext: true, outlineLevel: 0 } },
      ],
    },
    sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } }, children: anak }],
  });
  fs.writeFileSync(keluar, await Packer.toBuffer(doc));
  console.log(`OK ${keluar}: ${slides.length} slide, ${total} kata (±${menit} ${L.min})`);
}
if (process.argv.length < 4) { console.error("Pemakaian: node buat_notes.js isi.json keluar.docx"); process.exit(1); }
main(process.argv[2], process.argv[3]).catch((e) => { console.error(e); process.exit(1); });
