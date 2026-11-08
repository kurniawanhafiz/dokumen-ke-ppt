---
name: "dokumen-ke-ppt"
description: Ubah dokumen akademik (makalah, tugas, studi kasus, laporan; .docx, .pdf, .md, teks) jadi PPT presentasi berbahasa Indonesia dengan 30 tema visual, transisi Morph, grafik dan tabel native, kutipan APA, dan naskah speaker notes lengkap terpisah (.docx) untuk presentasi sekitar 15 menit, plus pertanyaan antisipasi. Pakai saat pengguna minta bikin PPT, slide, atau presentasi kelompok dari dokumen apa pun. Gaya lewat flag (--tema=<nama|nomor|rekomendasi> atau --warna=<nama|hex>), gaya kata (--padat, --singkat, --poin), plus --bagi, --pustaka, --slide=N, --fontaman, --en.
---

# Dokumen ke PPT

Skill ini mengubah dokumen akademik (makalah, tugas, studi kasus, laporan) menjadi file .pptx siap presentasi, plus dokumen .docx berisi naskah speaker notes lengkap dan pertanyaan antisipasi. Slide dibuat ringkas, penjelasan lengkapnya ada di notes. Dipakai ketika pengguna meminta "buatkan PPT dari makalah", "bikin slide presentasi", atau memberikan dokumen apa pun dan minta dibuatkan slide.

Folder skill ini berisi script di `scripts/` dan aset di `aset/`. Di bawah, `<skill>` berarti folder skill ini. Alurnya: baca sumber, tulis satu berkas `isi.json` (identitas, gaya, slide, naskah, tanya jawab), lalu jalankan pembuat PPT dan pembuat notes dari `isi.json` yang sama.

| Script | Fungsi |
|---|---|
| `gaya.py` | Satu pintu gaya: `--tema=...` (30 tema) atau `--warna=...` (polos) menjadi JSON gaya; rekomendasi tema dari topik; `--daftar` |
| `bangun_ppt.js` | Membangun .pptx mentah dari `isi.json` (semua tipe slide, ikon, grafik, tabel, notes, objek `!!`) |
| `buat_notes.js` | Membuat dokumen Speaker Notes (.docx) dari `isi.json` yang sama |
| `add_morph.py` | Pasang transisi Morph di semua slide dan periksa nama objek `!!` |
| `render_rumus.py` | Render rumus matematika ke PNG transparan (satuan atau `--batch`) |
| `ikon.py` | Warnai ikon Lucide, pilih ikon otomatis dari kata kunci (`--auto`, `--daftar`) |
| `palette.py`, `susun.js` | Modul dalam (palet polos; penyusun daftar slide). Tidak dipanggil langsung |

Aset: `aset/tema.json` (30 tema), `aset/latar` dan `aset/poster` (gambar latar isi dan sampul per tema), `aset/ikon` (102 ikon Lucide putih, lisensi di `aset/ikon/LICENSE-lucide.txt`).

## Flag yang dikenali

Pengguna boleh menulis flag di prompt, atau meminta hal yang sama dengan kalimat biasa ("warnanya ungu", "10 slide aja"). Perlakukan keduanya sama.

| Flag | Arti |
|---|---|
| `--tema=<nama atau nomor>` | Tema visual lengkap (warna, gambar latar, font judul). Lihat `python3 <skill>/scripts/gaya.py --daftar` |
| `--tema=rekomendasi` | Tema dipilih otomatis dari topik sumber (lihat Langkah 6) |
| `--warna=<nama atau hex>` | Gaya polos tanpa gambar latar: `hijau`, `navy`, `marun`, `teal`, `cokelat`, `hitam`, nama lain (`ungu`), atau hex (`--warna=#7A1F5C`) |
| `--singkat` `--padat` `--poin` | Gaya kata di slide (lihat Langkah 4). Bawaan `--singkat` |
| `--bagi` | Speaker notes memuat pembicara per anggota dan durasi |
| `--pustaka` | Tambah slide Referensi |
| `--slide=N` | Jumlah slide total, tepat N (minimal 5) |
| `--fontaman` | Pakai Calibri (dan Traditional Arabic untuk teks Arab) supaya tampil benar di komputer mana pun |
| `--en` | Slide, notes, dan dokumen notes dalam Bahasa Inggris |

Jika `--tema` dan `--warna` sama-sama ada, pakai `--tema` dan beri tahu pengguna. Jika ada lebih dari satu `--warna` atau `--tema`, pakai yang pertama dan beri tahu. Bentuk lama `--hijau`, `--navy`, dan seterusnya sudah tidak dipakai; jika pengguna menulisnya, perlakukan sebagai `--warna=hijau`, dan seterusnya.

## Langkah 1: Baca sumber dan ambil data pembuka

Baca seluruh sumber sebelum bertanya apa pun, supaya pertanyaan di Langkah 2 hanya untuk hal yang benar-benar belum ada.

**Membaca per jenis sumber:**
- `.docx`: ambil teks dan gambar (buka zip-nya, folder `word/media`). Rumus Word (OMML, elemen `m:oMath`) tidak ikut terambil sebagai gambar. Jika `pandoc` tersedia, jalankan `pandoc sumber.docx -t markdown` supaya rumus keluar sebagai LaTeX; jika tidak, baca `word/document.xml` dan tulis ulang rumusnya ke sintaks mathtext. Cocokkan hasilnya dengan teks sumber.
- `.pdf`: coba `pdftotext`. Jika hasilnya kosong atau berantakan (PDF hasil scan), jalankan OCR (`pdftoppm -r 300 -png` lalu `tesseract <gambar> - -l ind+eng`). Jika OCR tidak tersedia, beri tahu pengguna dan minta .docx atau teks. Angka, nama, dan ayat dari hasil OCR wajib diperiksa ulang dan disebut di balasan akhir sebagai "perlu dicek manual".
- `.md` atau teks: baca langsung.

**Jika sumbernya makalah:** ambil dari cover dan bagian awal: judul makalah, nama kelompok, nama anggota, nama mata kuliah, dan nama dosen pengampu. Ambil daftar sub-materi dari Bab II (Pembahasan). Jumlahnya menentukan jumlah slide.

**Jika sumbernya bukan makalah** (tugas, studi kasus, laporan praktikum, jurnal): tidak ada Bab II, jadi tentukan alur dari isi sumber, misalnya latar/kasus, proses atau metode, hasil atau analisis, kesimpulan. Siapkan 1 sampai 2 opsi struktur, masing-masing dengan jumlah slidenya, untuk ditawarkan di Langkah 2 (kecuali pengguna sudah memberi struktur).

**Identitas:** judul, kelompok, anggota, mata kuliah, dosen. Jika ada yang tidak ditemukan di sumber, masukkan ke pertanyaan Langkah 2. Jangan mengarang nama. Untuk tugas individu, pakai nama pembuat dan lewati kelompok.

**Universitas, fakultas, dan program studi:** jika cover sumber memuat nama universitas, fakultas, atau program studi (misalnya hasil skill `makalah-unri` atau `makalah-unri-si`), catat untuk slide pembuka (lihat Langkah 4). **Logo:** dipakai hanya jika ada. Sumbernya (a) file logo yang dilampirkan atau disebut pengguna, atau (b) logo di cover sumber .docx atau .pdf hasil skill `makalah-unri` atau `makalah-unri-si`. Untuk (b), ambil dari halaman cover (.docx: `word/media`; .pdf: `pdfimages -png -f 1 -l 1`, lalu gabungkan dengan gambar mask hitam-putih yang ikut keluar sebagai kanal alpha dengan PIL supaya latar logo transparan). Simpan sebagai `logo.png` dan isi `meta.logo` dan `meta.logo_alt`. Logo tampil kecil di kiri atas slide pembuka saja. Tanpa logo, tidak ada placeholder. Jika pengguna bilang "tanpa logo", jangan dipakai. Gambar lain di cover tidak diambil sebagai gambar isi.

**Teks footer**, dari identitas:
- `[Mata kuliah] | Kelompok [N]` jika kelompok bernomor.
- `[Mata kuliah] | Kelompok [Nama]` jika kelompok bernama.
- `[Mata kuliah] | [Nama pembuat]` untuk tugas individu.
- Hanya `[Mata kuliah]` jika sumber tidak menyebut kelompok dan pengguna tidak menjawab.

Jika nama mata kuliah lebih dari 4 kata, ringkas.

**Bahasa:** slide dan notes memakai Bahasa Indonesia baku tapi tidak kaku. Jika sumber berbahasa Inggris, tetap tulis slide dalam Bahasa Indonesia, pertahankan istilah teknis asing (dengan padanannya bila ada), dan jangan menerjemahkan nama, judul rujukan, atau kutipan langsung. Dengan `--en`, semua teks (termasuk heading "Slide N" di dokumen notes) memakai Bahasa Inggris.

## Langkah 2: Tanyakan yang belum diketahui (satu putaran)

Semua pertanyaan diajukan dalam satu kali tanya (AskUserQuestion jika ada), dan tidak ada putaran tanya kedua. Jika agen tidak punya tool bertanya tetapi pengguna ada di chat (misalnya OpenClaw, Hermes Agent, atau Claude Code tanpa tool itu), kirim semua pertanyaan sebagai satu pesan biasa bernomor dengan pilihan jawaban, lalu tunggu balasannya. Jangan menanyakan hal yang sudah dijawab lewat flag atau kalimat pengguna. Tool ini membatasi 3 pertanyaan; jika yang belum diketahui lebih banyak, pilih 3 berdasarkan prioritas di bawah, dan untuk sisanya pakai bawaan lalu sebutkan di balasan akhir.

Prioritas dan isi pertanyaan:
1. **Identitas yang hilang** (judul, anggota, mata kuliah, dosen, nama atau nomor kelompok): pertanyaan terbuka, jawaban lewat pilihan "Other". Tunggu jawaban, jangan mengarang.
2. **Struktur dan jumlah slide:** tanyakan hanya jika belum disebut dan (a) sumbernya bukan makalah berstruktur bab, atau (b) sub-materinya lebih dari 8. Untuk (a), opsi yang ditampilkan adalah 1 sampai 2 struktur dari Langkah 1 beserta jumlah slidenya.
3. **Gaya visual (tema atau warna):** tanyakan hanya jika pengguna tidak memberi `--tema`, `--warna`, atau permintaan warna. Opsi: "Rekomendasi otomatis dari topik" (sebut nama tema hasil `gaya.py --tema=rekomendasi --topik "..."` di teks pertanyaan), "Polos hijau", "Polos navy", "Polos marun". Sebutkan di teks pertanyaan bahwa tema lain (nama atau nomor 1 sampai 30), cokelat, hitam, atau warna sendiri bisa diketik lewat "Other".
4. **Gaya kata:** tanyakan hanya jika belum disebut lewat flag atau kalimat. Opsi: "Singkat tapi jelas (3 sampai 4 poin, sekitar 50 kata)", "Padat kata (4 sampai 5 poin kalimat utuh, sekitar 80 kata)", "Poin saja (3 poin, tiap poin 6 kata atau kurang)".
5. **Font:** tanyakan hanya jika belum disebut dan tidak ada `--fontaman`. Opsi: "Font tema atau Poppins + Lato (laptop sendiri, font sudah terpasang)" atau "Calibri (komputer kampus, Canva, atau tidak yakin)".

Jika tidak ada tool untuk bertanya atau pengguna tidak sedang memantau (sesi berjalan sendiri): pakai `--warna=navy` polos, font aman (Calibri, seperti `--fontaman`), gaya kata `--singkat`, dan aturan jumlah slide bawaan, lalu sebutkan pilihan itu di balasan akhir. Jika identitas penting tidak ditemukan, kosongkan bagian itu dan sebutkan, jangan dikarang.

## Langkah 3: Tentukan jumlah slide

Dua istilah:
- **Slide inti:** pembuka, slide isi, penutup.
- **Slide tambahan:** slide Referensi (`--pustaka`), slide gambar penuh atau zoom untuk diagram, slide Agenda, dan slide pembatas bab (`bagian`).

Struktur dasar:
- Slide pembuka: judul, nama kelompok, anggota, mata kuliah, dan dosen.
- Slide isi: satu slide untuk tiap sub-materi (judul bab, pengertian, ciri, asas, dan seterusnya).
- Slide penutup: satu slide "Terima Kasih" dengan tulisan di tengah dan keterangan "Tanya Jawab". Slide ini berdiri sendiri, tidak digabung dengan kesimpulan. Jika pengguna melampirkan atau menyebut foto dokumentasi, foto boleh ditaruh di slide ini.

**Agenda dan pembatas bab.** Jika sumber punya 3 bab atau lebih dan pengguna tidak memberi `--slide=N`, tambahkan satu slide Agenda (setelah pembuka, judul "Alur Presentasi", tiap bab bisa diklik langsung ke slide pembatasnya) dan satu slide pembatas di awal tiap bab. Keduanya slide tambahan: tidak memakan batas 10, tetapi total slide yang dihasilkan wajib disebut di balasan. Pembatas bab membawa naskah pengantar bab. Bab yang tidak punya slide isi sendiri (misalnya Penutup berisi kesimpulan dan saran) tetap boleh punya pembatas yang naskahnya memuat kesimpulan dan saran, sedangkan slide "Terima Kasih" tetap berdiri sendiri. Sumber kurang dari 3 bab, atau ada `--slide=N`: tanpa Agenda dan pembatas.

Urutan prioritas aturan jumlah:
1. **Jumlah dari pengguna** (`--slide=N` atau kalimat biasa) selalu menang dan total semua slide (inti + tambahan) harus tepat N. N minimal 5 (pembuka, tiga slide isi, penutup); jika kurang, pakai 5 dan beri tahu. Jika isi tidak muat, kurangi dengan urutan ini: buang Agenda dan pembatas bab, gabungkan sub-materi yang berdekatan, buang slide zoom diagram, lalu lewati slide Referensi dan beri tahu pengguna. Pembuka dan penutup tidak pernah dibuang. Jika ada isi penting yang terpaksa dipangkas, sebutkan apa yang dipangkas.
2. **Tanpa angka dari pengguna:** jumlah mengikuti materi.
   - Sub-materi sampai 8: slide inti maksimal 10 (pembuka + sub-materi + penutup) dan boleh kurang dari 10 jika materinya memang sedikit. Jangan menambah atau memadatkan slide demi mengejar angka 10. Slide inti tidak kurang dari 5; jika sub-materi sangat sedikit dan isinya padat, pecah sub-materi jadi 2 slide supaya mencapai 5.
   - Sub-materi lebih dari 8: slide inti boleh lebih dari 10, mengikuti jumlah sub-materi. Beri tahu pengguna total slide yang dihasilkan.
   - Slide tambahan (Agenda, pembatas bab, Referensi, zoom diagram) boleh menambah total di atas batas 10 dan wajib disebut di balasan.

Tulis rencana slide (judul, sub-materi yang dicakup, dan layout tiap slide) sebelum membuat file. Jika pengguna meminta revisi jumlah slide, susun rencana baru dari awal, jangan menambal slide lama.

## Langkah 4: Isi slide

Aturan umum:
- Judul slide memakai nama bagian saja, tanpa nomor sub-bab seperti 2.4.1. Contoh: "Judul", "Pendahuluan", "Tinjauan Pustaka".
- **Slide ringkas, penjelasan di notes.** Kepadatan mengikuti gaya kata (tanyakan di Langkah 2 atau flag), tanpa menghitung judul, caption, dan footer:

| Gaya kata | Poin per slide isi | Isi tiap poin | Total kata per slide |
|---|---|---|---|
| `--singkat` (bawaan) | 3 sampai 4 | satu kalimat singkat, sekitar 15 kata atau kurang | sekitar 50 |
| `--padat` | 4 sampai 5 | kalimat utuh, sekitar 20 kata atau kurang | sekitar 80 |
| `--poin` | 3 | frasa, 6 kata atau kurang, tanpa kalimat utuh | sekitar 20 |

  Jangan menaruh dua kalimat dalam satu poin. Pengecualian: slide berlayout definisi, angka, statistik, grafik, tabel, atau kutipan boleh berisi satu elemen utama. Penjelasan, alasan, dan contoh lengkap pindah ke speaker notes (Langkah 5), yang tetap lengkap di semua gaya kata. Jika sebuah poin tidak bisa dipersingkat tanpa mengubah makna, pecah jadi dua slide (bila jumlah slide bebas) atau pindahkan sisanya ke notes. Jangan memperkecil huruf demi muat.
- Ukuran huruf isi minimal 16 pt. Caption, sitasi, dan footer minimal 11 pt.
- Setia pada sumber: angka, definisi, istilah, nama, dan ayat harus sama dengan sumber. Meringkas boleh, menambah fakta baru atau mengubah makna tidak.
- Ayat, definisi, atau contoh penting boleh ditulis utuh di kotak contoh.
- Kutipan di slide memakai format APA (Nama, tahun) atau (Nama & Nama, tahun) atau (Nama dkk., tahun). Jika sumber tidak memberi rujukan untuk suatu poin, jangan menambahkan sitasi.
- Daftar pustaka lengkap tidak ditampilkan di slide, kecuali pengguna memakai `--pustaka` (lihat di bawah).

**Slide pembuka:** selain judul, kelompok, anggota, mata kuliah, dan dosen, tampilkan nama universitas, fakultas, dan program studi jika ada di cover sumber, persis seperti tertulis di sumber, sebagai teks. Logo hanya jika ada (lihat Langkah 1).

**Variasi layout.** Pilih tipe slide sesuai isi, dan jangan pakai tipe yang sama tiga slide isi berturut-turut. Nama tipe dipakai di `isi.json` (Langkah 6):
- `poin`: baris bernomor, daftar poin berurutan.
- `kartu`: kartu dengan ikon, daftar sejajar 2 sampai 4 hal.
- `garis`: timeline, urutan tahap atau bagian (2 sampai 5).
- `dua`: dua kolom, perbandingan dua konsep.
- `definisi`: satu definisi penting dengan huruf besar di kotak warna utama.
- `contoh`: soal atau definisi di kotak utama, langkah atau rumus di kartu, kesimpulan di kotak bawah.
- `angka`: satu statistik besar dengan keterangan, boleh dengan poin pendukung.
- `statistik`: 2 sampai 4 angka sejajar.
- `grafik`: grafik native yang bisa diedit di PowerPoint (`batang`, `batang-h`, `garis`, `donat`, `pie`), boleh dengan poin di samping.
- `tabel`: tabel native, maksimal 5 baris dan 4 kolom.
- `kutipan`: kutipan atau pernyataan penting dengan nama pengucap.
- `gambar`: gambar atau diagram dalam kartu, dengan caption dan alt text.
- `agenda`, `bagian`, `referensi`: otomatis dari struktur (lihat Langkah 3 dan slide Referensi). Pembuka dan penutup dibuat otomatis dari `meta`.

Angka, statistik, grafik, dan tabel hanya dari data yang ada di sumber. Jangan membuat data, dan jangan membulatkan di luar sumber.

Gambar dan diagram:
- Ambil dari .docx dengan membuka zip-nya (folder `word/media`), atau dari PDF dengan `pdftoppm -r 200 -png -f N -l N` lalu crop dengan PIL.
- Jaga rasio, jangan di-stretch. Resolusi minimal sekitar 150 dpi pada ukuran tampil.
- Taruh gambar di kartu dengan garis warna utama dan beri caption "Gambar N. ..." sesuai sumber.
- Diagram besar: satu slide untuk gambar penuh, lalu slide atau potongan zoom per bagian dengan kotak penanda di gambar penuh.
- Semua gambar, diagram, foto, dan rumus wajib punya alt text (`altText` di pptxgenjs) yang menjelaskan isinya dalam satu kalimat. Ikon dekoratif tidak perlu.

Tabel: maksimal 5 baris dan 4 kolom per slide, dibuat native (`tabel`). Header berupa sel warna utama dengan teks `teks_di_utama`. Tabel yang lebih besar diringkas jadi kartu atau dipecah.

Rumus:
- Rumus sederhana satu baris (misalnya `n! = n x (n-1) x ... x 1`) ditulis sebagai teks biasa di kotak contoh.
- Rumus dengan pecahan, akar, atau binomial dirender dengan warna `ink` dari JSON gaya (bukan warna utama, karena rumus berada di atas kartu): `python3 <skill>/scripts/render_rumus.py --color <ink> --size 32 --out rumus1.png "\binom{n}{k}=\frac{n!}{k!(n-k)!}"`. Banyak rumus sekaligus: `--batch rumus.json`. Tempel sebagai gambar di slide `contoh`, satu rumus per baris, dan beri alt text berisi rumusnya dalam kata-kata. Jika pembuat memberi peringatan slide `contoh` terlalu panjang, kecilkan `skalaRumus` (bawaan 0.85) atau pecah slide.
- Rumus dari .docx (OMML) dikonversi dulu ke sintaks mathtext, lihat Langkah 1.

Teks Arab (ayat, doa):
- Font Amiri (cadangan: Traditional Arabic; dengan font aman atau `--fontaman` langsung pakai Traditional Arabic), ukuran minimal 24 pt, rata kanan, dengan `rtlMode: true` dan `lang: "ar-SA"` di pptxgenjs.
- Terjemahan di bawahnya memakai font isi, lalu sumber (QS. Nama: ayat).
- Salin teks Arab persis dari sumber, jangan diketik ulang dari ingatan.

Slide Referensi (hanya jika `--pustaka`): letakkan sebelum slide Terima Kasih, judul "Referensi". Tampilkan hanya referensi yang dikutip di slide, format APA persis seperti di sumber, huruf minimal 11 pt, maksimal 8 entri per slide (lebih dari itu jadi 2 slide).

## Langkah 5: Speaker notes (naskah lengkap) dan pertanyaan antisipasi

Slide dibuat ringkas, jadi speaker notes adalah naskah lengkap yang bisa dipakai pembicara agar presentasinya berjalan baik.

**Durasi dan panjang naskah**
- Total durasi **maksimal 15 menit**. Jika pengguna menyebut durasi lain (misalnya "10 menit" atau "20 menit"), pakai durasi itu.
- Patokan bicara: 130 kata per menit. Total semua naskah kira-kira durasi × 130 kata (15 menit ≈ 1.950 kata) dan tidak boleh melewati batas lebih dari 10%.
- Pembagian: pembuka dan penutup masing-masing sekitar 30 detik (sekitar 65 kata). Sisanya dibagi ke slide isi sebanding bobot materinya; slide yang berisi penjelasan atau contoh lebih banyak mendapat porsi lebih besar.
- Jika materi memang sedikit, naskah boleh lebih pendek dari batas. Jangan memanjangkan dengan pengulangan atau hal di luar sumber.

**Isi naskah per slide.** Satu sampai beberapa paragraf bahasa lisan yang mengalir, disimpan di kolom notes slide (bukan kotak teks di slide):
1. Kalimat pengantar yang menyambung dari slide sebelumnya.
2. Penjelasan lengkap tiap poin di slide: pengertian, alasan, dan contoh dari sumber. Bukan sekadar mengulang kalimat slide.
3. Kalimat penghubung ke slide berikutnya.

Tetap setia pada sumber: angka, definisi, nama, dan ayat diambil dari sumber. Boleh memakai analogi singkat atau cara bicara yang lebih mudah dipahami selama tidak mengubah makna dan tidak menambah fakta atau angka baru. Naskah slide pembuka memuat salam, perkenalan, dan tujuan presentasi. Naskah slide penutup memuat ringkasan inti, ucapan terima kasih, dan ajakan tanya jawab.

**Dokumen .docx** dibuat oleh `buat_notes.js` dari `isi.json` (bukan ditulis manual), Times New Roman 12, kertas A4:
- Judul dokumen, lalu baris "Perkiraan total durasi: ±N menit (±K kata)". Jumlah kata naskah dihitung otomatis oleh pembuat PPT dan pembuat notes.
- Per slide: heading "Slide N: [judul slide]" dan naskahnya.
- Di akhir: bagian **Pertanyaan Antisipasi**.

**Pertanyaan Antisipasi:** 3 sampai 5 pasang pertanyaan dan jawaban yang kemungkinan muncul saat tanya jawab (definisi yang sering disalahpahami, "kenapa", "apa bedanya", contoh penerapan). Jawaban 1 sampai 3 kalimat dan berdasar sumber. Jika jawaban perlu informasi di luar sumber, beri tanda "(di luar sumber, periksa ulang)". Bagian ini hanya di .docx, tidak masuk slide. Dengan `--bagi`, tulis di tiap pertanyaan anggota yang sebaiknya menjawab (yang membawakan slide terkait).

Jika `--bagi` aktif:
- Pakai daftar anggota dari sumber. Jika tidak ada, sudah ditanyakan di Langkah 2.
- Pembuka dibawakan anggota pertama, penutup oleh anggota terakhir. Slide isi dibagi berurutan dan sebisa mungkin merata menurut durasi. Slide bersambung dalam satu sub-materi sebaiknya dibawakan orang yang sama. Jika anggota lebih banyak dari slide, sebagian anggota tidak kebagian slide; sebutkan itu ke pengguna.
- Durasi tiap slide diambil dari pembagian di atas, dibulatkan ke 0,5 menit, dan totalnya tetap sesuai batas durasi.
- Isi `pembicara` dan `durasi` pada tiap slide di `isi.json` (termasuk `pembicara_sampul`, `durasi_sampul`, `pembicara_penutup`, `durasi_penutup` di `meta`). Pembuat menulis baris pertama notes `Pembicara: [Nama] | Durasi: ±N menit` di PPT dan .docx secara otomatis, lalu naskahnya.
- Di .docx, tabel ringkasan (Slide, Judul, Pembicara, Durasi) muncul otomatis tepat setelah judul dokumen, berikut total durasi.

Tanpa `--bagi`, jangan tambahkan baris pembicara atau durasi per slide.

## Langkah 6: Gaya visual dan `isi.json`

### Gaya

Jalankan satu perintah dan simpan JSON-nya sebagai `gaya.json`:

```
python3 <skill>/scripts/gaya.py --tema=batik                       # nama, nomor, atau kunci tema
python3 <skill>/scripts/gaya.py --tema=rekomendasi --topik "judul dan mata kuliah"
python3 <skill>/scripts/gaya.py "--warna=#7A1F5C" --fontaman        # polos
```

Tambahkan `--fontaman` jika font aman dipilih. JSON berisi `bg`, `card`, `ink`, `muted`, `judul`, `utama`, `aksen`, `teks_di_utama`, `font_judul`, `font_isi`, `font_arab`, `latar`, `poster`, `seri`. Script adalah sumber kebenaran warna; jangan menulis kode warna sendiri.

- **Tema (30):** memakai gambar latar (`poster` untuk sampul, pembatas, dan penutup; `latar` untuk slide isi), kartu semi-solid di atas gambar, dan warna hasil cek kontras. Teks di atas kotak `utama` memakai `teks_di_utama`, judul di atas kartu memakai warna yang lolos kontras. Daftar: `gaya.py --daftar`.
- **Rekomendasi tema:** `--topik` diisi judul dan mata kuliah (bukan nama program studi). Aturan kata kunci ada di `gaya.py` (contoh: matematika, statistik, pendidikan menjadi Papan Tulis; kriptografi, pemrograman menjadi Cyberpunk; kesehatan menjadi Medis); tanpa kecocokan dipakai Modern. Sebutkan tema terpilih di balasan akhir.
- **Polos (`--warna`):** tanpa gambar latar. Latar isi krem, latar sampul, pembatas, dan penutup warna utama. Warna dari pengguna digelapkan otomatis jika kontras terhadap krem di bawah 4.5 (sebutkan hasilnya di balasan).

| `--warna` | Utama | Catatan |
|---|---|---|
| `hijau` | #1E4D3B | |
| `navy` | #1B2A4A | |
| `marun` | #6B1E2E | |
| `teal` | #134E4A | |
| `cokelat` | #4A2F1F | |
| `hitam` | #1C1C1E | aksen emas #B08D3C hanya untuk garis judul |

Selain warna dari `gaya.py`, jangan menambah warna lain.

Font:
- Tema: judul memakai font tema (mis. Palatino Linotype, Century Gothic), isi Calibri. Polos: judul Poppins (bold), isi Lato, teks Arab Amiri.
- Font aman (`--fontaman`, pilihan "Calibri" di Langkah 2, pengguna bilang tidak bisa memasang font seperti di Canva atau laptop kampus, atau sesi tanpa pemantauan): judul dan isi Calibri, teks Arab Traditional Arabic.
- File PPT dari pptxgenjs tidak menyematkan font. Jika memakai font bawaan (bukan font aman), ingatkan pengguna di balasan akhir bahwa fontnya harus terpasang di komputer yang membuka PPT. Cek mesin render dengan `fc-list`; jika font tidak ada, hasil render hanya perkiraan.

### Format `isi.json`

```json
{
  "gaya": { "...isi gaya.json..." },
  "meta": {
    "judul": "", "jenis": "Makalah", "keterangan": "Disusun untuk memenuhi tugas mata kuliah ...",
    "dosen": "", "kelompok": "Kelompok 11", "anggota": ["..."],
    "institusi": ["Fakultas ...", "Program Studi ...", "Universitas ..."],
    "logo": "logo.png", "logo_alt": "Logo ...", "foto": "dokumentasi.jpg", "foto_alt": "...",
    "footer": "Mata Kuliah | Kelompok 11", "bahasa": "id",
    "catatan_sampul": "naskah", "catatan_penutup": "naskah"
  },
  "slide": [ { "tipe": "...", "judul": "...", "catatan": "naskah slide ini" } ],
  "pustaka": ["entri APA", "..."],
  "tanya": [ { "q": "pertanyaan", "a": "jawaban", "oleh": "anggota (hanya --bagi)" } ]
}
```

`meta.bahasa` diisi `"en"` untuk `--en`. `logo`, `foto`, dan `institusi` boleh dikosongkan. Isi `slide` hanya slide di antara pembuka dan penutup, dalam urutan tampil. `pustaka` diisi hanya jika `--pustaka` (dipecah otomatis jadi beberapa slide Referensi dan diletakkan sebelum penutup).

| `tipe` | Bidang |
|---|---|
| `agenda` | `judul` (opsional); item diambil otomatis dari semua slide `bagian` |
| `bagian` | `judul`, `sub`, `ikon` |
| `poin` | `judul`, `poin[]`, `ikon` |
| `kartu` | `judul`, `kartu[{j, t, ikon}]` |
| `garis` | `judul`, `titik[{j, t}]` |
| `dua` | `judul`, `kiri{j, poin[]}`, `kanan{j, poin[]}` |
| `definisi` | `judul`, `teks`, `sumber` |
| `contoh` | `judul`, `soal`, `isi[]` (teks, atau `{rumus: "png", alt, skala}`), `jawab`, `skalaRumus` |
| `angka` | `judul`, `angka`, `label`, `poin[]`, `sumber` |
| `statistik` | `judul`, `data[[angka, label]]`, `sumber` |
| `grafik` | `judul`, `jenis`, `label[]`, `seri[{nama, nilai[]}]`, `satuan`, `poin[]`, `sumber` |
| `tabel` | `judul`, `kolom[]`, `baris[][]`, `sumber` |
| `kutipan` | `judul`, `teks`, `oleh` |
| `gambar` | `judul`, `file`, `alt`, `keterangan`, `poin[]` |

Setiap slide boleh punya `catatan` (naskah), `pembicara`, `durasi`. Ikon dipilih otomatis dari kata kunci jika `ikon` kosong; nama ikon valid lewat `python3 <skill>/scripts/ikon.py --daftar`.

### Membangun

```
node <skill>/scripts/bangun_ppt.js isi.json PPT-mentah.pptx
node <skill>/scripts/buat_notes.js isi.json "Speaker Notes - [judul].docx"
```

Jika `require('pptxgenjs')` atau `require('docx')` gagal, jalankan node dengan `NODE_PATH=$(npm root -g)`. Pembuat PPT menulis peringatan (stderr) untuk slide tanpa catatan, gambar tanpa alt text, ikon tidak ada, tabel melebihi 5 x 4, poin melebihi 5, dan slide `contoh` yang melebihi kartu. Perbaiki di `isi.json` lalu bangun ulang.

Komposisi yang dibuat otomatis: judul kiri atas dengan garis pendek warna aksen, ikon kanan atas, lingkaran dekoratif transparan, footer kiri bawah dan nomor slide, kartu untuk isi, sampul dengan panel (logo, jenis dokumen, judul, keterangan, dosen, kelompok, anggota, institusi), pembatas bab bernomor, penutup "Terima Kasih" dengan "Tanya Jawab" dan foto bila ada. Tidak ada gradasi, emoji, atau clipart. Kartu, ikon, dan elemen lain diberi nama unik per slide.

**Penamaan objek untuk Morph.** PowerPoint hanya memasangkan objek berdasarkan nama jika namanya diawali `!!`. Tanpa awalan itu, Morph menebak pasangan dari kemiripan dan bisa jatuh ke efek fade. `bangun_ppt.js` sudah memberi `objectName` persis berikut di setiap slide: `!!judul`, `!!garisJudul`, `!!ikon`, `!!orb`, `!!orbKecil`, `!!footer`. Posisi dan ukurannya berbeda antar slide (sampul, pembatas, dan penutup lebih besar), sehingga Morph menggeser dan mengubah ukurannya secara halus. Gambar, tabel, dan rumus diberi nama unik per slide tanpa awalan `!!`.

## Langkah 7: Transisi Morph

Pasang transisi Morph di semua slide, termasuk pembuka dan penutup. Simpan PPT mentah dari pptxgenjs dengan nama sementara, lalu jalankan:

```
python3 <skill>/scripts/add_morph.py PPT-mentah.pptx "/mnt/user-data/outputs/PPT - [judul].pptx"
```

Script menyisipkan blok Morph setelah `</p:clrMapOvr>` di setiap `ppt/slides/slideN.xml`, aman dijalankan ulang, dan memberi peringatan jika ada slide yang tidak memiliki objek bernama `!!...`. Jika ada peringatan, perbaiki penamaan di build lalu ulangi. Hanya file final yang disimpan di folder outputs. Sebelum dikirim, buang entri folder dari zip agar file aman dibuka lewat layanan cloud: `zip -dq "<file>" '*/'` untuk .pptx dan .docx.

LibreOffice tidak menampilkan Morph (jatuh ke fade), jadi Morph hanya bisa diperiksa langsung di PowerPoint 2019 atau 365.

## Langkah 8: Cek hasil

- Jumlah slide sesuai Langkah 3 (`--slide=N` jika ada).
- Footer benar: mata kuliah dan kelompok sesuai sumber.
- Judul slide tidak memakai nomor sub-bab.
- Slide "Terima Kasih" berdiri sendiri di akhir (setelah Referensi jika ada).
- Setiap slide punya naskah speaker notes lengkap, dan jumlah kata total sesuai durasi (default maksimal 15 menit ≈ 1.950 kata, patokan 130 kata per menit; hitung dengan script). Dengan `--bagi`: baris Pembicara dan Durasi ada di semua slide dan total durasi masuk akal. Dokumen notes punya bagian Pertanyaan Antisipasi.
- Nama file: `[judul]` maksimal 70 karakter, berupa frasa utuh (tidak menggantung), sama untuk PPT dan notes.
- Setiap kutipan memakai format APA di slide dan ada di daftar pustaka sumber. Tidak ada daftar pustaka di slide kecuali `--pustaka`.
- Kesetiaan isi: cocokkan semua angka, definisi, nama, dan ayat di slide dengan sumber. Tidak ada fakta baru.
- Kepadatan sesuai gaya kata yang dipilih (tabel di Langkah 4), huruf isi minimal 16 pt. Grafik, tabel, dan angka cocok dengan sumber.
- Variasi: tidak ada tiga slide isi berturut-turut dengan layout sama.
- Warna hanya dari `gaya.json`. Pada tema bergambar, judul dan teks terbaca jelas di atas gambar dan kartu.
- Alt text ada di semua gambar, diagram, foto, dan rumus.
- Morph terpasang: jumlah kemunculan `p159:morph` di setiap file slide sama dengan 1, dan `add_morph.py` tidak memberi peringatan nama `!!`.
- Validasi file: jalankan `scripts/office/validate.py` dari skill pptx. Jika script itu tidak ada, minimal pastikan file terbuka dengan `python3 -c "from pptx import Presentation; Presentation('<file>.pptx')"`.
- Agenda: tiap bab menautkan ke slide pembatas yang benar (jika ada Agenda). Logo tampil hanya jika ada.
- Render ke gambar (`soffice --headless --convert-to pdf`, lalu `pdftoppm -r 80 -png`) dan periksa semua slide: teks tidak terpotong, elemen tidak tumpang tindih, gambar tidak ter-stretch, ikon tampil. Untuk teks Arab, pastikan arah kanan ke kiri benar dan harakat tidak hilang.

## Revisi

Simpan `isi.json` (dan `gaya.json`, gambar, rumus) di folder kerja, jangan dibuang. Dengan begitu:
- Ganti tema, warna, font, footer, atau teks satu slide: ubah `gaya.json` atau `isi.json`, jalankan ulang `bangun_ppt.js`, `buat_notes.js`, dan `add_morph.py`, lalu ulangi Langkah 8. Jika memakai ulang rumus, render ulang dengan warna `ink` baru karena warnanya mengikuti tema.
- Ganti jumlah slide: susun rencana baru dari awal (Langkah 3).
- Jika `isi.json` sudah tidak ada (sesi baru), buka PPT final dengan skill pptx, edit slide yang diminta saja, lalu jalankan ulang `add_morph.py` (aman dijalankan ulang) dan perbarui dokumen notes untuk slide yang berubah.

Revisi atas file yang sama menimpa file itu. Permintaan baru dari sumber lain mengikuti aturan nama di bagian Output.

## Output

- Folder keluaran: `/mnt/user-data/outputs/` di aplikasi Claude. Jika folder itu tidak ada (Claude Code, OpenClaw, Hermes Agent, dan agen lain), simpan di folder kerja saat ini atau folder yang disebut pengguna, dan sebutkan path lengkap kedua file di balasan akhir.
- File PPT: `/mnt/user-data/outputs/PPT - [judul].pptx`
- File notes: `/mnt/user-data/outputs/Speaker Notes - [judul].docx`
- `[judul]` diambil dari judul sumber dan sama untuk kedua file. Hapus dulu karakter yang dilarang sistem berkas (`/ \ : * ? " < > |`; titik dua pada subjudul ikut dibuang lewat aturan di bawah) dan rapikan spasi ganda. Lalu:
  1. Jika judul 70 karakter atau kurang: pakai judul lengkap apa adanya.
  2. Jika lebih dari 70 karakter: buang subjudul, yaitu bagian setelah titik dua, atau setelah " - " dan "–". Jika hasilnya 70 karakter atau kurang, pakai itu.
  3. Jika masih lebih dari 70 karakter: ringkas jadi frasa inti yang utuh, maksimal 70 karakter. Pertahankan topik utama dan kata kunci, buang keterangan tambahan (misalnya lokasi, objek studi, atau masa waktu). Hanya pakai kata dari judul asli atau singkatan baku yang dipakai di sumber, jangan menambah makna, dan jangan berakhir menggantung pada kata sambung atau kata depan (di, dan, yang, pada, berbasis, dan sejenisnya). Jangan memotong buta dan jangan memakai tanda titik tiga.
  - Contoh: "Analisis Sistem Informasi Manajemen Perpustakaan Berbasis Web: Studi Kasus di Universitas Riau" menjadi "Analisis Sistem Informasi Manajemen Perpustakaan Berbasis Web" (aturan 2). "Pengaruh Penggunaan Media Sosial terhadap Perilaku Belajar Mahasiswa Fakultas MIPA Universitas Riau pada Masa Pandemi" menjadi "Pengaruh Media Sosial terhadap Perilaku Belajar Mahasiswa" (aturan 3).
  - Jika judul diubah (aturan 2 atau 3), sebutkan judul yang dipakai untuk nama file di balasan akhir. Judul di slide pembuka tetap judul lengkap dari sumber.
  - Jika nama itu sudah dipakai file lain (bukan revisi), tambahkan " (2)", " (3)", dan seterusnya sebelum ekstensi.
- Sajikan kedua file dengan tool pengiriman file yang tersedia (SendUserFile atau present_files).

Balas pengguna dalam satu sampai tiga kalimat: jumlah slide (sebut jika slide tambahan membuat total melewati 10, atau ada isi yang dipangkas), perkiraan durasi presentasi, nama dua file (sebut judul ringkasnya jika judul diubah), tema atau palet, gaya kata, dan font yang dipakai (sebut tema hasil rekomendasi, jika warnanya digelapkan otomatis, atau jika memakai font aman karena tidak bertanya), dan satu hal yang perlu dicek manual (misalnya tampilan Morph di PowerPoint, font yang harus terpasang, atau angka hasil OCR).

## Catatan versi

Versi saat ini: v3.0. Riwayat lengkap perubahan tiap versi ada di `CHANGELOG.md` di folder skill ini.
