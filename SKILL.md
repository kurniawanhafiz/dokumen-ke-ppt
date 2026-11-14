---
name: "dokumen-ke-ppt"
description: Ubah dokumen akademik (makalah, tugas, studi kasus, laporan; .docx, .pdf, .md, teks) jadi PPT presentasi berbahasa Indonesia dengan 30 tema visual, transisi Morph, grafik dan tabel native, kutipan APA, dan naskah speaker notes lengkap terpisah (.docx) untuk presentasi sekitar 15 menit, plus pertanyaan antisipasi. Pakai saat pengguna minta bikin PPT, slide, atau presentasi kelompok dari dokumen apa pun. Gaya lewat flag (--tema=nama, nomor, atau rekomendasi; atau --warna=nama atau hex), gaya kata (--padat, --singkat, --poin), plus --transisi, --bagi, --pustaka, --slide=N, --fontaman, --en.
---

# Dokumen ke PPT

Skill ini mengubah dokumen akademik (makalah, tugas, studi kasus, laporan) menjadi file .pptx siap presentasi, plus dokumen .docx berisi naskah speaker notes lengkap dan pertanyaan antisipasi. Slide dibuat ringkas, penjelasan lengkapnya ada di notes. Dipakai ketika pengguna meminta "buatkan PPT dari makalah", "bikin slide presentasi", atau memberikan dokumen apa pun dan minta dibuatkan slide.

Folder skill ini berisi script di `scripts/`, aset di `aset/`, dan rujukan rinci di `references/`. Di bawah, `<skill>` berarti folder skill ini. Alurnya: baca sumber, tulis satu berkas `isi.json` (identitas, gaya, slide, naskah, tanya jawab), periksa dengan `cek_isi.py`, lalu jalankan pembuat PPT dan pembuat notes dari `isi.json` yang sama.

**Hemat konteks:** file ini hanya memuat alur dan aturan inti. Rincian ada di `references/`; baca berkas yang disebut di langkah terkait hanya saat langkah itu dikerjakan, jangan membaca semuanya di awal.

| Script | Fungsi |
|---|---|
| `baca_sumber.py` | Membaca .docx, .pdf, .md, .txt: teks bersih, daftar pustaka dipisah, logo cover, gambar, deteksi template, OCR otomatis untuk PDF scan |
| `gaya.py` | Satu pintu gaya: `--tema=...` (30 tema, nama, nomor, atau kata biasa seperti "kesehatan") atau `--warna=...` (polos) menjadi JSON gaya; rekomendasi tema dari topik; `--daftar` per kategori |
| `cek_isi.py` | Dry-run `isi.json`: seragamkan bentuk, cek grafik, batas item, kepadatan, naskah vs durasi, berkas, total slide; `--pecah`, `--tulis` |
| `bangun_ppt.js` | Membangun .pptx mentah dari `isi.json` (semua tipe slide, ikon, grafik, tabel, notes, objek `!!`) |
| `buat_notes.js` | Membuat dokumen Speaker Notes (.docx) dari `isi.json` yang sama |
| `add_morph.py` | Memasang transisi (`--transisi`), animasi masuk opsional (`--animasi`, hanya bila diminta; belum teruji di PowerPoint asli), menggabungkan media kembar, menyelaraskan tema PowerPoint (`--gaya`), memeriksa nama objek `!!` |
| `render_rumus.py` | Render rumus matematika ke PNG transparan (satuan atau `--batch`) |
| `ikon.py` | Warnai ikon Lucide, pilih ikon otomatis dari kata kunci (`--auto`, `--daftar`) |
| `palette.py`, `susun.js` | Modul dalam (palet polos; penyusun daftar slide). Tidak dipanggil langsung |

Aset: `aset/tema.json` (30 tema), `aset/latar` dan `aset/poster` (gambar latar isi dan sampul per tema), `aset/ikon` (ikon Lucide putih, lisensi di `aset/ikon/LICENSE-lucide.txt`), `docs/katalog_30_tema.jpg` (katalog gambar semua tema).

## Flag yang dikenali

Pengguna boleh menulis flag di prompt, atau meminta hal yang sama dengan kalimat biasa ("warnanya ungu", "10 slide aja"). Perlakukan keduanya sama.

| Flag | Arti |
|---|---|
| `--tema=<nama atau nomor>` | Tema visual lengkap (warna, gambar latar, font judul). Lihat `python3 <skill>/scripts/gaya.py --daftar` |
| `--tema=rekomendasi` | Tema dipilih otomatis dari topik sumber (lihat Langkah 6) |
| `--warna=<nama atau hex>` | Gaya polos tanpa gambar latar: `hijau`, `navy`, `marun`, `teal`, `cokelat`, `hitam`, nama lain (`ungu`), atau hex (`--warna=#7A1F5C`) |
| `--singkat` `--padat` `--poin` | Gaya kata di slide (lihat Langkah 4). Bawaan `--singkat` |
| `--transisi=<morph, fade, kombinasi>` | Transisi antar slide. `morph` (bawaan) di semua slide; `fade` paling aman untuk Google Slides, Keynote, dan Canva; `kombinasi` Morph dengan Push di pembatas bab dan Wipe di slide grafik |
| `--bagi` | Speaker notes memuat pembicara per anggota dan durasi |
| `--pustaka` | Tambah slide Referensi |
| `--slide=N` | Jumlah slide total, tepat N (minimal 5) |
| `--fontaman` | Pakai Calibri (dan Traditional Arabic untuk teks Arab) supaya tampil benar di komputer mana pun |
| `--en` | Slide, notes, dan dokumen notes dalam Bahasa Inggris |

Jika `--tema` dan `--warna` sama-sama ada, pakai `--tema` dan beri tahu pengguna. Jika ada lebih dari satu `--warna` atau `--tema`, pakai yang pertama dan beri tahu. Bentuk lama `--hijau`, `--navy`, dan seterusnya sudah dihapus dan tidak dikenali; jika pengguna menulisnya, anggap tidak ada flag warna dan tanyakan warnanya seperti biasa (Langkah 2). Jika pengguna memilih Google Slides atau Canva sebagai tujuan dan tidak menyebut `--transisi`, pakai `fade`.

## Langkah 1: Baca sumber dan ambil data pembuka

Baca seluruh sumber sebelum bertanya apa pun, supaya pertanyaan di Langkah 2 hanya untuk hal yang benar-benar belum ada.

```
python3 <skill>/scripts/baca_sumber.py "<berkas sumber>" --keluar=kerja
```

Lalu baca `kerja/sumber.txt` (per bagian jika panjang) dan `kerja/ringkasan.json` (bab terdeteksi, awal dokumen atau cover, rumus, placeholder template, gambar dan tebakan keterangan, logo, OCR). Daftar pustaka ada di `kerja/pustaka.txt`. Jika script gagal atau jenis berkas tidak didukung, ikuti cara manual di `references/membaca-sumber.md`.

- **Makalah:** ambil dari cover dan bagian awal: judul, kelompok, anggota, mata kuliah, dosen. Daftar sub-materi dari Bab II menentukan jumlah slide.
- **Bukan makalah** (tugas, studi kasus, laporan praktikum, jurnal): tentukan alur dari isi sumber (latar atau kasus, proses atau metode, hasil atau analisis, kesimpulan) dan siapkan 1 sampai 2 opsi struktur beserta jumlah slidenya untuk Langkah 2, kecuali pengguna sudah memberi struktur.
- **Identitas:** judul, kelompok, anggota, mata kuliah, dosen. Yang tidak ditemukan masuk ke pertanyaan Langkah 2. Jangan mengarang nama. Tugas individu: pakai nama pembuat, lewati kelompok.
- **Universitas, fakultas, program studi:** catat dari cover jika ada, tampil sebagai teks di slide pembuka. **Logo** hanya jika ada (lampiran pengguna, atau cover hasil `makalah-unri` atau `makalah-unri-si`; `baca_sumber.py` mengambilnya sebagai `logo.png`). Pengguna bilang "tanpa logo": jangan dipakai.
- **Footer:** `[Mata kuliah] | Kelompok [N]` (bernomor), `[Mata kuliah] | Kelompok [Nama]` (bernama), `[Mata kuliah] | [Nama pembuat]` (individu), atau hanya `[Mata kuliah]`. Nama mata kuliah lebih dari 4 kata: ringkas.
- **Bahasa:** slide dan notes Bahasa Indonesia baku tapi tidak kaku, termasuk untuk sumber berbahasa Inggris (istilah teknis dipertahankan; nama, judul rujukan, dan kutipan langsung tidak diterjemahkan). Dengan `--en`, semua teks Bahasa Inggris.
- Jika `template_placeholder` di ringkasan tidak kosong (isi masih `[Tuliskan ...]`), berhenti dan beri tahu pengguna sebelum membuat slide.

## Langkah 2: Tanyakan yang belum diketahui (satu putaran)

Semua pertanyaan diajukan dalam satu kali tanya (AskUserQuestion jika ada), dan tidak ada putaran tanya kedua. Jika agen tidak punya tool bertanya tetapi pengguna ada di chat (misalnya OpenClaw, Hermes Agent, atau Claude Code tanpa tool itu), kirim semua pertanyaan sebagai satu pesan biasa bernomor dengan pilihan jawaban, lalu tunggu balasannya. Jangan menanyakan hal yang sudah dijawab lewat flag atau kalimat pengguna. Tool ini membatasi 3 pertanyaan; jika yang belum diketahui lebih banyak, pilih 3 berdasarkan prioritas di bawah, dan untuk sisanya pakai bawaan lalu sebutkan di balasan akhir.

Prioritas dan isi pertanyaan:
1. **Identitas yang hilang** (judul, anggota, mata kuliah, dosen, nama atau nomor kelompok): pertanyaan terbuka, jawaban lewat pilihan "Other". Tunggu jawaban, jangan mengarang.
2. **Struktur dan jumlah slide:** tanyakan hanya jika belum disebut dan (a) sumbernya bukan makalah berstruktur bab, atau (b) sub-materinya lebih dari 8. Untuk (a), opsi yang ditampilkan adalah 1 sampai 2 struktur dari Langkah 1 beserta jumlah slidenya.
3. **Gaya visual (tema atau warna):** tanyakan hanya jika pengguna tidak memberi `--tema`, `--warna`, atau permintaan warna. Sebelum bertanya, kirim `<skill>/docs/katalog_30_tema.jpg` ke pengguna (SendUserFile atau present_files) supaya bisa memilih sambil melihat, dan tulis kategori dari `gaya.py --daftar` di teks pertanyaan (Gelap dan mewah, Alam, Bersih dan formal, Ceria dan kreatif, Budaya). Opsi: "Rekomendasi otomatis dari topik" (sebut nama tema hasil `gaya.py --tema=rekomendasi --topik "..."` di teks pertanyaan), "Polos hijau", "Polos navy", "Polos marun". Sebutkan di teks pertanyaan bahwa tema lain (nama, nomor 1 sampai 30, atau kata biasa seperti "kesehatan" atau "galaxy"), cokelat, hitam, atau warna sendiri bisa diketik lewat "Other".
4. **Gaya kata:** tanyakan hanya jika belum disebut lewat flag atau kalimat. Opsi: "Singkat tapi jelas (3 sampai 4 poin, sekitar 50 kata)", "Padat kata (4 sampai 5 poin kalimat utuh, sekitar 80 kata)", "Poin saja (3 poin, tiap poin 6 kata atau kurang)".
5. **Font:** tanyakan hanya jika belum disebut dan tidak ada `--fontaman`. Opsi: "Font tema atau Poppins + Lato (laptop sendiri, font sudah terpasang)" atau "Calibri (komputer kampus, Canva, atau tidak yakin)".

Jika tidak ada tool untuk bertanya atau pengguna tidak sedang memantau (sesi berjalan sendiri): pakai `--warna=navy` polos, font aman (Calibri, seperti `--fontaman`), gaya kata `--singkat`, `--transisi=morph`, dan aturan jumlah slide bawaan, lalu sebutkan pilihan itu di balasan akhir. Jika identitas penting tidak ditemukan, kosongkan bagian itu dan sebutkan, jangan dikarang.

## Langkah 3: Tentukan jumlah slide

Aturan inti (rincian, urutan pemangkasan, dan contoh ada di `references/jumlah-slide.md`; baca jika `--slide=N` dipakai atau sub-materi lebih dari 8):
- Jumlah dari pengguna (`--slide=N`) selalu menang: total semua slide harus tepat N, minimal 5.
- Tanpa angka: slide inti (pembuka + sub-materi + penutup) maksimal 10 untuk sub-materi sampai 8, tidak kurang dari 5; lebih dari 8 sub-materi boleh lebih dari 10.
- Sumber dengan 3 bab atau lebih dan tanpa `--slide=N`: tambah Agenda yang bisa diklik dan pembatas bab. Slide tambahan (Agenda, pembatas, Referensi, zoom diagram) wajib disebut di balasan.
- Slide "Terima Kasih" berdiri sendiri di akhir. Tulis rencana slide (judul, sub-materi, layout) sebelum membuat file; revisi jumlah slide berarti rencana baru dari awal.

## Langkah 4: Isi slide

Aturan inti (rincian layout, gambar, tabel, rumus, teks Arab, dan slide Referensi ada di `references/isi-slide.md`; baca saat slide terkait dibuat):
- Judul slide memakai nama bagian saja, tanpa nomor sub-bab.
- **Slide ringkas, penjelasan di notes.** Kepadatan mengikuti gaya kata, tanpa menghitung judul, caption, dan footer:

| Gaya kata | Poin per slide isi | Isi tiap poin | Total kata per slide |
|---|---|---|---|
| `--singkat` (bawaan) | 3 sampai 4 | satu kalimat singkat, sekitar 15 kata atau kurang | sekitar 50 |
| `--padat` | 4 sampai 5 | kalimat utuh, sekitar 20 kata atau kurang | sekitar 80 |
| `--poin` | 3 | frasa, 6 kata atau kurang, tanpa kalimat utuh | sekitar 20 |

- Jangan dua kalimat dalam satu poin; sisanya pindah ke notes. Huruf isi minimal 16 pt, caption dan footer minimal 11 pt; jangan memperkecil huruf demi muat.
- Setia pada sumber: angka, definisi, istilah, nama, dan ayat sama dengan sumber. Angka, statistik, grafik, dan tabel hanya dari data di sumber.
- Kutipan di slide format APA (Nama, tahun); tanpa rujukan di sumber, jangan menambah sitasi. Daftar pustaka lengkap tidak tampil di slide kecuali `--pustaka`.
- Slide pembuka: judul, kelompok, anggota, mata kuliah, dosen, serta universitas, fakultas, dan program studi jika ada di cover.
- Variasi layout, jangan tipe yang sama tiga slide isi berturut-turut. Tipe: `poin`, `kartu`, `langkah`, `garis`, `dua`, `definisi`, `contoh`, `angka`, `statistik`, `grafik`, `tabel` (maks 5 baris dan 4 kolom), `kutipan`, `gambar`; `agenda`, `bagian`, `referensi` otomatis. Semua gambar, diagram, foto, dan rumus wajib punya alt text.

## Langkah 5: Speaker notes dan pertanyaan antisipasi

Rincian lengkap di `references/speaker-notes.md` (baca sebelum menulis naskah). Inti:
- Total durasi maksimal 15 menit (atau durasi dari pengguna), 130 kata per menit, jadi sekitar 1.950 kata untuk 15 menit, tidak lebih dari 10% di atas batas. Pembuka dan penutup masing-masing sekitar 65 kata.
- Naskah per slide: pengantar dari slide sebelumnya, penjelasan lengkap tiap poin (pengertian, alasan, contoh dari sumber), penghubung ke slide berikutnya. Setia pada sumber.
- Pertanyaan Antisipasi 3 sampai 5 pasang di .docx, tidak di slide. Dengan `--bagi`: isi `pembicara` dan `durasi` per slide; tanpa `--bagi`, jangan tambahkan baris pembicara atau durasi.

## Langkah 6: Gaya visual dan isi.json

```
python3 <skill>/scripts/gaya.py --tema=batik                       # nama, nomor, kunci, atau kata biasa
python3 <skill>/scripts/gaya.py --tema=rekomendasi --topik "judul dan mata kuliah"
python3 <skill>/scripts/gaya.py "--warna=#7A1F5C" --fontaman        # polos
```

Simpan keluarannya sebagai `gaya.json` dan masukkan ke `isi.json` (bidang `gaya`). Script adalah sumber kebenaran warna; jangan menulis kode warna sendiri. Tambahkan `--fontaman` jika font aman dipilih. Rekomendasi tema: `--topik` diisi judul dan mata kuliah (bukan nama program studi); sebutkan tema terpilih di balasan akhir.

Format `isi.json` (semua tipe slide dan bidangnya), palet polos, aturan font, dan penamaan objek Morph ada di `references/gaya-dan-isi-json.md`; baca sebelum menulis `isi.json`. Lalu:

```
python3 <skill>/scripts/cek_isi.py isi.json --gaya-kata=singkat --durasi=15 --tulis
node <skill>/scripts/bangun_ppt.js isi.json PPT-mentah.pptx
node <skill>/scripts/buat_notes.js isi.json "Speaker Notes - [judul].docx"
```

Perbaiki semua ERROR dari `cek_isi.py` sebelum membangun; tambahkan `--pecah` hanya jika jumlah slide bebas. Jika `require('pptxgenjs')` atau `require('docx')` gagal, jalankan node dengan `NODE_PATH=$(npm root -g)`. Peringatan pembuat PPT (stderr) diperbaiki di `isi.json` lalu bangun ulang.

## Langkah 7: Transisi dan tema PowerPoint

Simpan PPT mentah dari pptxgenjs dengan nama sementara, lalu:

```
python3 <skill>/scripts/add_morph.py PPT-mentah.pptx "/mnt/user-data/outputs/PPT - [judul].pptx" --gaya=gaya.json [--transisi=morph|fade|kombinasi] [--animasi]
```

Script memasang transisi di semua slide termasuk pembuka dan penutup (aman dijalankan ulang), menulis warna dan nama gaya ke tema PowerPoint (slide yang ditambah pengguna ikut serasi), dan memberi peringatan jika ada slide tanpa objek `!!...` (mode `morph` dan `kombinasi`). Perbaiki penamaan di build jika ada peringatan, lalu ulangi. Hanya file final yang disimpan di folder outputs. Sebelum dikirim, buang entri folder dari zip agar aman dibuka lewat layanan cloud: `zip -dq "<file>" '*/'` untuk .pptx dan .docx.

LibreOffice tidak menampilkan Morph (jatuh ke fade), jadi Morph hanya bisa diperiksa langsung di PowerPoint 2019 atau 365. Push dan Wipe tampil di aplikasi lain, dan `fade` aman di mana saja.

## Langkah 8: Cek hasil

Jalankan seluruh daftar di `references/cek-hasil.md` (jumlah slide, footer, naskah vs durasi, kesetiaan isi ke sumber, kepadatan, variasi layout, alt text, transisi dan tema, validasi file, render semua slide ke gambar dan periksa tampilannya).

## Revisi dan output

Simpan `isi.json`, `gaya.json`, gambar, dan rumus di folder kerja; jangan dibuang. Ganti tema, warna, font, footer, atau teks: ubah JSON, jalankan ulang `cek_isi.py`, `bangun_ppt.js`, `buat_notes.js`, dan `add_morph.py`, lalu ulangi Langkah 8. Ganti jumlah slide: rencana baru dari awal. Aturan lengkap revisi, folder keluaran, dan penamaan berkas (`[judul]` maksimal 70 karakter) ada di `references/revisi-dan-output.md`.

- File PPT: `/mnt/user-data/outputs/PPT - [judul].pptx`; file notes: `/mnt/user-data/outputs/Speaker Notes - [judul].docx`. Jika folder itu tidak ada, simpan di folder kerja dan sebutkan path lengkapnya.
- Sajikan kedua file dengan tool pengiriman file yang tersedia (SendUserFile atau present_files).

Balas pengguna dalam satu sampai tiga kalimat: jumlah slide (sebut jika slide tambahan membuat total melewati 10, atau ada isi yang dipangkas), perkiraan durasi presentasi, nama dua file (sebut judul ringkasnya jika judul diubah), tema atau palet, gaya kata, transisi, dan font yang dipakai (sebut tema hasil rekomendasi, jika warnanya digelapkan otomatis, atau jika memakai font aman karena tidak bertanya), dan satu hal yang perlu dicek manual (misalnya tampilan Morph di PowerPoint, font yang harus terpasang, atau angka hasil OCR).

## Catatan versi

Versi saat ini: v3.3. Riwayat lengkap perubahan tiap versi ada di `CHANGELOG.md` di folder skill ini. Lisensi: GNU GPL v3 (lihat `LICENSE`).
