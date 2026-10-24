#!/usr/bin/env node
// Render ikon react-icons ke PNG transparan berwarna.
//
// Persiapan: cek dulu apakah paket sudah terpasang global (biasanya sudah):
//   ls $(npm root -g) | grep -E "^(react|react-dom|react-icons|sharp)$"
// Kalau belum, pasang di FOLDER KERJA (bukan di folder skill):
//   npm install react react-dom react-icons sharp
//
// Pemakaian:
//   node <folder-skill>/scripts/make_icons.mjs --color 1B2A4A --out ikon FaBook FaUsers MdSchool
//
// Modul dicari di folder kerja (process.cwd()) lebih dulu, lalu di folder global npm,
// jadi script ini boleh disimpan di mana saja.
// Nama ikon memakai awalan paket react-icons (Fa, Fa6, Md, Io5, Bs, Hi2, Lu, Tb, Ri, Pi, ...).
// Keluaran: <out>/<NamaIkon>.png ukuran 256 px.
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { createRequire } from "node:module";

const pencari = [createRequire(path.join(process.cwd(), "noop.js"))];
try {
  const globalRoot = execSync("npm root -g", { encoding: "utf8" }).trim();
  pencari.push(createRequire(path.join(globalRoot, "noop.js")));
} catch (e) {
  // npm tidak ada; hanya folder kerja yang dipakai
}

function muat(id) {
  let galat;
  for (const req of pencari) {
    try {
      return req(id);
    } catch (e) {
      galat = e;
    }
  }
  throw galat;
}

let React, renderToStaticMarkup, sharp;
try {
  React = muat("react");
  ({ renderToStaticMarkup } = muat("react-dom/server"));
  sharp = muat("sharp");
} catch (e) {
  console.error("Paket belum terpasang. Jalankan di folder kerja: npm install react react-dom react-icons sharp");
  process.exit(2);
}

const args = process.argv.slice(2);
let color = "1B2A4A";
let out = "ikon";
const names = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--color") color = args[++i].replace("#", "");
  else if (args[i] === "--out") out = args[++i];
  else names.push(args[i]);
}
if (!names.length) {
  console.error("Sebutkan minimal satu nama ikon, contoh: FaBook");
  process.exit(1);
}
fs.mkdirSync(out, { recursive: true });

let gagal = 0;
for (const name of names) {
  const m = name.match(/^([A-Z][a-z]+\d?)([A-Z0-9].*)$/);
  if (!m) {
    console.error(`Nama ikon tidak valid: ${name}`);
    gagal++;
    continue;
  }
  try {
    const mod = muat(`react-icons/${m[1].toLowerCase()}`);
    const Icon = mod[name];
    if (!Icon) throw new Error("ikon tidak ada di paket");
    const svg = renderToStaticMarkup(React.createElement(Icon, { color: `#${color}`, size: 256 }));
    const file = path.join(out, `${name}.png`);
    await sharp(Buffer.from(svg))
      .resize(256, 256, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png()
      .toFile(file);
    console.log(`OK ${file}`);
  } catch (e) {
    console.error(`Gagal ${name}: ${e.message}`);
    gagal++;
  }
}
process.exit(gagal ? 1 : 0);
