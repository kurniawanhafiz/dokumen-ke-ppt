# dokumen-ke-ppt

[English](README.en.md) | Bahasa Indonesia

Skill untuk mengubah dokumen akademik (makalah, tugas, studi kasus, laporan) menjadi PPT presentasi berbahasa Indonesia. Sumber boleh berupa .docx, .pdf, .md, atau teks biasa. Hasilnya dua file: PPT dengan transisi Morph dan kutipan APA, serta dokumen .docx berisi speaker notes.

Versi saat ini: v1. Skill ini melanjutkan `makalah-ke-ppt` (v1 sampai v3) dan berganti nama karena sumbernya tidak lagi terbatas pada makalah.

## Daftar isi

- [Yang dihasilkan](#yang-dihasilkan)
- [Cara kerja singkat](#cara-kerja-singkat)
- [Persyaratan](#persyaratan)
- [Cara pasang](#cara-pasang)
- [Cara pakai](#cara-pakai)
- [Isi repo](#isi-repo)
- [Batasan yang diketahui](#batasan-yang-diketahui)
- [Pemecahan masalah](#pemecahan-masalah)
- [Pembuat](#pembuat)
- [Lisensi](#lisensi)

## Yang dihasilkan

- `PPT-[judul singkat].pptx`: slide pembuka, slide isi per sub-materi, dan slide Terima Kasih. Setiap slide punya speaker notes 3 sampai 5 kalimat.
- `Speaker-Notes-[judul singkat].docx`: notes semua slide dalam satu dokumen (Times New Roman 12).

## Cara kerja singkat

1. Skill membaca sumber dan mengambil identitas: judul, kelompok, anggota, mata kuliah, dosen. Data yang tidak ditemukan ditanyakan, tidak dikarang.
2. Hal yang belum diketahui (warna, jumlah slide, struktur untuk sumber non-makalah) ditanyakan sekaligus dalam satu kali tanya.
3. Rencana slide dituliskan lebih dulu: judul dan sub-materi yang dicakup tiap slide.
4. Slide dibuat dengan palet pilihan, font Poppins dan Lato, ikon, dan elemen dekoratif yang sama di setiap slide supaya Morph bergerak halus. Gambar, tabel, rumus, dan teks Arab ditangani sesuai jenisnya.
5. Speaker notes ditulis per slide, lalu dikumpulkan ke dalam file .docx.
6. Transisi Morph dipasang, PPT divalidasi, lalu setiap slide dirender menjadi gambar dan diperiksa: teks terpotong, elemen tumpang tindih, gambar melar, kesesuaian isi dengan sumber.

## Persyaratan

Skill ini dipakai di Claude (Anthropic) yang mendukung skill. Lingkungan tempat skill berjalan membutuhkan:

- Skill bawaan `pptx` dan `docx` (untuk validasi PPT dan membuat dokumen notes).
- Python 3 dengan `matplotlib` dan `Pillow` (untuk `render_rumus.py` dan memotong gambar).
- Node.js dengan `pptxgenjs`, `react`, `react-dom`, `react-icons`, dan `sharp` (untuk membuat slide dan ikon).
- LibreOffice dan `pdftoppm` (untuk merender slide menjadi gambar saat pemeriksaan).
- Font Poppins, Lato, dan Amiri (Amiri hanya untuk teks Arab) di komputer yang dipakai membuka PPT.
- PowerPoint 2019 atau 365 untuk melihat transisi Morph.

## Cara pasang

Repo ini adalah folder skill itu sendiri: `SKILL.md` ada di akar repo.

**Dengan git**:

```
git clone https://github.com/kurniawanhafiz/dokumen-ke-ppt.git ~/.claude/skills/dokumen-ke-ppt
```

**Dengan ZIP:** unduh ZIP dari GitHub, ekstrak, lalu ganti nama foldernya menjadi `dokumen-ke-ppt` (nama folder harus sama dengan nama skill). Salin folder itu ke lokasi skill yang dipakai lingkunganmu. Untuk aplikasi Claude, unggah ZIP-nya lewat pengaturan skill sesuai petunjuk resmi Anthropic.

Pastikan folder `scripts/` ikut tersalin, karena `SKILL.md` memanggil script di dalamnya. Jika kamu masih punya skill lama `makalah-ke-ppt`, hapus supaya tidak ada dua skill yang bersaing.

## Cara pakai

Panggil skill dengan perintah `/dokumen-ke-ppt` atau cukup minta dibuatkan PPT dari dokumenmu. Tulis flag di prompt, atau minta hal yang sama dengan kalimat biasa ("warnanya ungu", "10 slide saja").

### Flag

| Flag | Fungsi |
|---|---|
| `--hijau` | Palet hijau tua + krem |
| `--navy` | Palet navy + krem |
| `--marun` | Palet marun + krem |
| `--teal` | Palet teal gelap + krem |
| `--cokelat` | Palet cokelat tua + krem |
| `--hitam` | Palet hitam + krem, garis judul beraksen emas |
| `--warna=<hex atau nama>` | Warna sendiri, misalnya `--warna=#7A1F5C` atau `--warna=ungu` |
| `--bagi` | Speaker notes memuat pembicara per anggota dan durasi tiap slide |
| `--pustaka` | Menambah slide Referensi sebelum slide Terima Kasih |
| `--slide=N` | Jumlah slide total tepat N |

Jika tidak ada flag warna, skill bertanya warna yang diinginkan. Warna sendiri yang terlalu terang digelapkan otomatis agar teks tetap terbaca, dan skill menyebutkannya di balasan.

### Contoh prompt

Makalah biasa:

```
/dokumen-ke-ppt buatkan PPT dari makalah terlampir --navy
```

Tugas non-makalah (studi kasus, laporan). Skill menawarkan struktur slide lebih dulu karena sumbernya tidak berbab:

```
/dokumen-ke-ppt buatkan PPT dari tugas studi kasus BPMN terlampir --hijau --slide=10
```

Presentasi kelompok dengan pembagian pembicara. Setiap slide mendapat baris `Pembicara: [Nama] | Durasi: ±N menit`, dan .docx notes memuat tabel ringkasan pembagiannya:

```
/dokumen-ke-ppt buatkan PPT dari makalah terlampir --marun --bagi, total durasi 15 menit
```

Warna sendiri:

```
/dokumen-ke-ppt buatkan PPT dari makalah terlampir --warna=#7A1F5C
```

## Isi repo

```
dokumen-ke-ppt/
├── SKILL.md            Instruksi lengkap yang dibaca Claude
├── README.md           Dokumentasi (Indonesia)
├── README.en.md        Dokumentasi (English)
├── LICENSE             Lisensi MIT
├── .gitignore
└── scripts/
    ├── palette.py
    ├── add_morph.py
    ├── make_icons.mjs
    └── render_rumus.py
```

### scripts/

Script dipanggil otomatis oleh skill. Bagian ini untuk yang ingin menjalankannya sendiri, dari akar repo.

**palette.py** mengubah flag warna menjadi palet (JSON) dan memeriksa kontras terhadap latar krem.

```
python3 scripts/palette.py --hijau
python3 scripts/palette.py "--warna=#7A1F5C"
```

**add_morph.py** memasang transisi Morph di semua slide sebuah .pptx. Aman dijalankan ulang, dan file keluaran harus berbeda dari file masukan.

```
python3 scripts/add_morph.py PPT-mentah.pptx PPT-final.pptx
```

**make_icons.mjs** merender ikon react-icons menjadi PNG transparan berwarna ukuran 256 px. Modul dicari di folder kerja lebih dulu, lalu di folder global npm.

```
node scripts/make_icons.mjs --color 1B2A4A --out ikon FaBook MdSchool
```

**render_rumus.py** merender rumus matematika (sintaks mathtext matplotlib, subset LaTeX) menjadi PNG transparan.

```
python3 scripts/render_rumus.py --color 1B2A4A --size 32 --out rumus1.png "\binom{n}{k}=\frac{n!}{k!(n-k)!}"
```

## Batasan yang diketahui

- **Morph:** hanya tampil di PowerPoint 2019 dan 365. Aplikasi lain memakai efek fade. Pratinjau di LibreOffice juga tidak menampilkan Morph, jadi geraknya hanya bisa diperiksa langsung di PowerPoint.
- **Font:** Poppins, Lato, dan Amiri harus terpasang di komputer yang membuka PPT. Jika tidak, PowerPoint memakai font pengganti dan tampilan bisa bergeser. Skill bisa diminta memakai Calibri.
- **Bahasa:** slide dan notes hanya dalam Bahasa Indonesia.
- **Rumus:** dirender menjadi gambar sehingga tidak bisa diedit di PowerPoint. Rumus satu baris tanpa pecahan atau akar ditulis sebagai teks biasa.
- **Palet:** latar slide isi selalu krem (#F5EFE0). Yang berganti hanya warna utama. Tata letak slide juga tetap, tanpa tema alternatif.
- **Jaringan:** memasang paket npm butuh akses ke registry. Di lingkungan tanpa akses itu, paket harus sudah terpasang.
- **Sesi tanpa pemantauan:** jika skill berjalan tanpa bisa bertanya, ia memakai `--navy` dan aturan jumlah slide bawaan, lalu menyebutkannya di balasan.
- **Ketepatan isi:** skill menjaga angka, definisi, nama, dan ayat tetap sama dengan sumber, tetapi periksa ulang sebelum presentasi.

## Pemecahan masalah

| Gejala | Penyebab | Cara mengatasi |
|---|---|---|
| Tampilan font berantakan atau berbeda | Font belum terpasang | Pasang Poppins, Lato, dan Amiri dari Google Fonts, atau minta skill memakai Calibri |
| Transisi tidak bergerak | Bukan PowerPoint 2019++/365 | Buka di PowerPoint, lalu cek tab Transitions: harus tertulis Morph |
| `File keluaran harus beda dari file masukan.` | Nama file masukan dan keluaran `add_morph.py` sama | Beri nama keluaran yang berbeda |
| `Paket belum terpasang.` dari `make_icons.mjs` | `react`, `react-dom`, atau `sharp` tidak ditemukan | Jalankan `npm install react react-dom react-icons sharp` di folder kerja, atau cek `ls $(npm root -g)` |
| `npm install` gagal dengan `ENOTFOUND registry.npmjs.org` | Registry npm tidak terjangkau dari jaringan ini | Pakai paket yang sudah terpasang global, atau pasang dari jaringan lain |
| `Gagal NamaIkon: ikon tidak ada di paket` | Nama atau awalan ikon salah | Cek nama ikon di dokumentasi react-icons (awalan seperti `Fa`, `Md`, `Io5`) |
| `require('pptxgenjs')` gagal | Node tidak menemukan paket global | Jalankan dengan `NODE_PATH=$(npm root -g) node ...` |
| `render_rumus.py` mengeluarkan galat mathtext | Ada perintah LaTeX yang tidak didukung | Sederhanakan rumus; `\frac`, `\binom`, `\sqrt`, pangkat, dan indeks didukung |
| `Warna '...' tidak dikenali.` | Nama warna tidak ada di daftar | Pakai hex: `--warna=#RRGGBB` |
| Warna hasil lebih gelap dari yang diminta | Kontras terhadap krem di bawah 4.5 | Itu disengaja agar teks terbaca; pilih warna yang lebih gelap sendiri jika ingin hasil persis |

## Pembuat

Dibuat oleh **Kurniawan Hafiz**.

## Lisensi

Dirilis dengan [lisensi MIT](LICENSE).
