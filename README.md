# dokumen-ke-ppt

[English](README.en.md) | Bahasa Indonesia

Skill untuk mengubah dokumen akademik (makalah, tugas, studi kasus, laporan) menjadi PPT presentasi berbahasa Indonesia. Sumber boleh berupa .docx, .pdf, .md, atau teks biasa. Hasilnya dua file: PPT dengan transisi Morph dan kutipan APA, serta dokumen .docx berisi speaker notes.

Versi saat ini: v2.2. Skill ini melanjutkan `makalah-ke-ppt` (v1 sampai v3). Karena namanya baru, penomoran dimulai lagi dari v1 saat berganti nama menjadi `dokumen-ke-ppt`, lalu naik ke v2, v2.1, dan v2.2. Daftar lengkap perubahan tiap versi ada di [CHANGELOG.md](CHANGELOG.md).

## Daftar isi

- [Yang dihasilkan](#yang-dihasilkan)
- [Cara kerja singkat](#cara-kerja-singkat)
- [Persyaratan](#persyaratan)
- [Cara pasang](#cara-pasang)
- [Cara pakai](#cara-pakai)
- [Isi repo](#isi-repo)
- [Riwayat versi](#riwayat-versi)
- [Batasan yang diketahui](#batasan-yang-diketahui)
- [Pemecahan masalah](#pemecahan-masalah)
- [Pembuat](#pembuat)
- [Lisensi](#lisensi)

## Yang dihasilkan

- `PPT - [judul].pptx`: slide pembuka, slide isi per sub-materi, dan slide Terima Kasih. Slide dibuat ringkas (3 sampai 4 poin, satu kalimat singkat per poin) dan setiap slide punya naskah speaker notes lengkap.
- `Speaker Notes - [judul].docx`: naskah semua slide dalam satu dokumen (Times New Roman 12) untuk presentasi maksimal 15 menit (atau durasi lain yang kamu sebut), ditambah bagian Pertanyaan Antisipasi (3 sampai 5 tanya jawab untuk sesi tanya jawab). `[judul]` adalah judul sumber (maksimal 70 karakter). Jika lebih panjang, subjudul dibuang dulu, lalu diringkas jadi frasa inti yang utuh, dan judul yang dipakai disebut di balasan.

## Cara kerja singkat

1. Skill membaca sumber (termasuk OCR untuk PDF scan dan konversi rumus Word) dan mengambil identitas: judul, kelompok, anggota, mata kuliah, dosen. Nama universitas, fakultas, dan program studi dari cover dipakai sebagai teks di slide pembuka (tanpa logo).
2. Hal yang belum diketahui (identitas yang hilang, struktur dan jumlah slide, warna, font) ditanyakan sekaligus dalam satu kali tanya. Data yang tidak ditemukan ditanyakan, tidak dikarang.
3. Rencana slide dituliskan lebih dulu: judul dan sub-materi yang dicakup tiap slide. Tanpa angka dari kamu, jumlah slide mengikuti materi: maksimal 10 (boleh kurang), dan lebih dari 10 jika sub-materi lebih dari 8.
4. Slide dibuat dengan palet pilihan, font Poppins dan Lato (atau Calibri), ikon, dan layout yang bervariasi. Elemen dekoratif memakai nama objek berawalan `!!` yang sama di setiap slide supaya Morph memasangkannya dan bergerak halus. Gambar, tabel, rumus, dan teks Arab ditangani sesuai jenisnya.
5. Naskah speaker notes ditulis lengkap per slide (patokan 130 kata per menit, total maksimal 15 menit), lalu dikumpulkan ke dalam file .docx bersama pertanyaan antisipasi.
6. Transisi Morph dipasang, PPT divalidasi, lalu setiap slide dirender menjadi gambar dan diperiksa: teks terpotong, elemen tumpang tindih, gambar melar, kesesuaian isi dengan sumber.

## Persyaratan

Skill ini dipakai di Claude (Anthropic) yang mendukung skill. Lingkungan tempat skill berjalan membutuhkan:

- Skill bawaan `pptx` dan `docx` (untuk validasi PPT dan membuat dokumen notes).
- Python 3 dengan `matplotlib` dan `Pillow` (untuk `render_rumus.py` dan memotong gambar).
- Node.js dengan `pptxgenjs`, `react`, `react-dom`, `react-icons`, dan `sharp` (untuk membuat slide dan ikon).
- LibreOffice dan `pdftoppm` (untuk merender slide menjadi gambar saat pemeriksaan).
- Font Poppins, Lato, dan Amiri (Amiri hanya untuk teks Arab) di komputer yang dipakai membuka PPT. Jika tidak yakin, pakai `--fontaman`.
- Opsional: `pandoc` (konversi rumus Word) dan `tesseract` (OCR untuk PDF scan).
- PowerPoint 2019++ atau 365 untuk melihat transisi Morph.

## Cara pasang

Repo ini adalah folder skill itu sendiri: `SKILL.md` ada di akar repo.

**Dengan git**:

```
git clone https://github.com/kurniawanhafiz/dokumen-ke-ppt.git ~/.claude/skills/dokumen-ke-ppt
```

**Dengan ZIP:** unduh ZIP dari GitHub, ekstrak, lalu ganti nama foldernya menjadi `dokumen-ke-ppt` (nama folder harus sama dengan nama skill). Salin folder itu ke lokasi skill yang dipakai lingkunganmu. Untuk aplikasi Claude, unggah ZIP-nya lewat pengaturan skill sesuai petunjuk resmi Anthropic.

Pastikan folder `scripts/` ikut tersalin, karena `SKILL.md` memanggil script di dalamnya. Jika kamu masih punya skill lama `makalah-ke-ppt`, hapus supaya tidak ada dua skill yang bersaing.

## Cara pakai

Panggil skill dengan perintah `/dokumen-ke-ppt` atau cukup minta dibuatkan PPT dari dokumenmu. Tulis flag di prompt, atau minta hal yang sama dengan kalimat biasa ("warnanya ungu", "10 slide saja", "presentasinya 10 menit").

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
| `--slide=N` | Jumlah slide total tepat N (minimal 5, termasuk slide Referensi dan zoom diagram) |
| `--fontaman` | Pakai Calibri (dan Traditional Arabic untuk teks Arab) supaya tampil benar di komputer mana pun |
| `--en` | Slide, notes, dan dokumen notes dalam Bahasa Inggris |

Jika tidak ada flag warna, skill bertanya warna yang diinginkan (bersama pertanyaan lain dalam satu putaran). Warna sendiri yang terlalu terang digelapkan otomatis agar teks tetap terbaca, dan skill menyebutkannya di balasan.

### Contoh prompt

Makalah biasa:

```
/dokumen-ke-ppt buatkan PPT dari makalah terlampir --navy
```

Tugas non-makalah (studi kasus, laporan). Skill menawarkan struktur slide lebih dulu karena sumbernya tidak berbab:

```
/dokumen-ke-ppt buatkan PPT dari tugas studi kasus BPMN terlampir --hijau --slide=10
```

Presentasi kelompok dengan pembagian pembicara. Setiap slide mendapat baris `Pembicara: [Nama] | Durasi: ±N menit`, dan .docx notes memuat tabel ringkasan pembagiannya. Durasi 15 menit adalah bawaan, dan angka lain bisa disebut di prompt:

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
├── CHANGELOG.md        Riwayat perubahan tiap versi
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

**add_morph.py** memasang transisi Morph di semua slide sebuah .pptx dan memberi peringatan jika objek tidak bernama `!!...`. Aman dijalankan ulang, dan file keluaran harus berbeda dari file masukan.

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

## Riwayat versi

Versi saat ini adalah **v2.2**. Perubahan tiap versi (v1, v2, v2.1, v2.2) dicatat di [CHANGELOG.md](CHANGELOG.md), dari yang terbaru.

## Batasan yang diketahui

- **Morph:** hanya tampil di PowerPoint 2019++ dan 365. Objek yang sama di antar slide dipasangkan lewat nama berawalan `!!`; `add_morph.py` memberi peringatan jika nama itu tidak ada. Aplikasi lain memakai efek fade. Pratinjau di LibreOffice juga tidak menampilkan Morph, jadi geraknya hanya bisa diperiksa langsung di PowerPoint.
- **Font:** Poppins, Lato, dan Amiri harus terpasang di komputer yang membuka PPT. Jika tidak, PowerPoint memakai font pengganti dan tampilan bisa bergeser. Pakai `--fontaman` untuk Calibri. Di sesi tanpa pemantauan, skill otomatis memakai font aman. File PPT tidak menyematkan font.
- **Bahasa:** slide dan notes berbahasa Indonesia, termasuk untuk sumber berbahasa Inggris (istilah teknis dipertahankan). Pakai `--en` untuk hasil berbahasa Inggris.
- **Rumus:** dirender menjadi gambar sehingga tidak bisa diedit di PowerPoint. Rumus satu baris tanpa pecahan atau akar ditulis sebagai teks biasa.
- **Palet:** latar slide isi selalu krem (#F5EFE0). Yang berganti hanya warna utama. Tata letak slide juga tetap, tanpa tema alternatif.
- **Jaringan:** memasang paket npm butuh akses ke registry. Di lingkungan tanpa akses itu, paket harus sudah terpasang.
- **Sesi tanpa pemantauan:** jika skill berjalan tanpa bisa bertanya, ia memakai `--navy`, font aman, dan aturan jumlah slide bawaan, lalu menyebutkannya di balasan.
- **PDF scan:** hasil OCR bisa salah di angka, nama, dan ayat. Skill menandainya "perlu dicek manual".
- **Ketepatan isi:** skill menjaga angka, definisi, nama, dan ayat tetap sama dengan sumber, tetapi periksa ulang sebelum presentasi.

## Pemecahan masalah

| Gejala | Penyebab | Cara mengatasi |
|---|---|---|
| Tampilan font berantakan atau berbeda | Font belum terpasang | Pasang Poppins, Lato, dan Amiri dari Google Fonts, atau buat ulang dengan `--fontaman` |
| Transisi tidak bergerak | Bukan PowerPoint 2019++/365 | Buka di PowerPoint, lalu cek tab Transitions: harus tertulis Morph |
| Morph jalan tapi objek tidak bergeser mulus | Nama objek tidak berawalan `!!` atau berbeda antar slide | Perhatikan peringatan `add_morph.py`, samakan nama `!!judul`, `!!ikon`, dan seterusnya |
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
