---
name: "dokumen-ke-ppt"
description: Ubah dokumen akademik (makalah, tugas, studi kasus, laporan; .docx, .pdf, .md, teks) jadi PPT presentasi berbahasa Indonesia dengan transisi Morph, kutipan APA, dan naskah speaker notes lengkap terpisah (.docx) untuk presentasi sekitar 15 menit, plus pertanyaan antisipasi. Pakai saat pengguna minta bikin PPT, slide, atau presentasi kelompok dari dokumen apa pun. Warna dipilih lewat flag (--hijau, --navy, --marun, --teal, --cokelat, --hitam, atau --warna=...), plus --bagi, --pustaka, --slide=N, --fontaman, --en.
---

# Dokumen ke PPT

Skill ini mengubah dokumen akademik (makalah, tugas, studi kasus, laporan) menjadi file .pptx siap presentasi, plus dokumen .docx berisi naskah speaker notes lengkap dan pertanyaan antisipasi. Slide dibuat ringkas, penjelasan lengkapnya ada di notes. Dipakai ketika pengguna meminta "buatkan PPT dari makalah", "bikin slide presentasi", atau memberikan dokumen apa pun dan minta dibuatkan slide.

Folder skill ini berisi script pendukung di `scripts/`. Di bawah, `<skill>` berarti folder skill ini.

| Script | Fungsi |
|---|---|
| `palette.py` | Ubah flag warna jadi palet (JSON) dan cek kontras |
| `add_morph.py` | Pasang transisi Morph di semua slide dan periksa nama objek `!!` |
| `make_icons.mjs` | Render ikon react-icons ke PNG berwarna |
| `render_rumus.py` | Render rumus matematika ke PNG transparan |

## Flag yang dikenali

Pengguna boleh menulis flag di prompt, atau meminta hal yang sama dengan kalimat biasa ("warnanya ungu", "10 slide aja"). Perlakukan keduanya sama.

| Flag | Arti |
|---|---|
| `--hijau` `--navy` `--marun` `--teal` `--cokelat` `--hitam` | Palet bawaan (warna utama + latar krem) |
| `--warna=<hex atau nama>` | Warna sendiri, contoh `--warna=#7A1F5C` atau `--warna=ungu` |
| `--bagi` | Speaker notes memuat pembicara per anggota dan durasi |
| `--pustaka` | Tambah slide Referensi |
| `--slide=N` | Jumlah slide total, tepat N (minimal 5) |
| `--fontaman` | Pakai Calibri (dan Traditional Arabic untuk teks Arab) supaya tampil benar di komputer mana pun |
| `--en` | Slide, notes, dan dokumen notes dalam Bahasa Inggris |

Jika ada lebih dari satu flag warna, pakai yang pertama dan beri tahu pengguna.

## Langkah 1: Baca sumber dan ambil data pembuka

Baca seluruh sumber sebelum bertanya apa pun, supaya pertanyaan di Langkah 2 hanya untuk hal yang benar-benar belum ada.

**Membaca per jenis sumber:**
- `.docx`: ambil teks dan gambar (buka zip-nya, folder `word/media`). Rumus Word (OMML, elemen `m:oMath`) tidak ikut terambil sebagai gambar. Jika `pandoc` tersedia, jalankan `pandoc sumber.docx -t markdown` supaya rumus keluar sebagai LaTeX; jika tidak, baca `word/document.xml` dan tulis ulang rumusnya ke sintaks mathtext. Cocokkan hasilnya dengan teks sumber.
- `.pdf`: coba `pdftotext`. Jika hasilnya kosong atau berantakan (PDF hasil scan), jalankan OCR (`pdftoppm -r 300 -png` lalu `tesseract <gambar> - -l ind+eng`). Jika OCR tidak tersedia, beri tahu pengguna dan minta .docx atau teks. Angka, nama, dan ayat dari hasil OCR wajib diperiksa ulang dan disebut di balasan akhir sebagai "perlu dicek manual".
- `.md` atau teks: baca langsung.

**Jika sumbernya makalah:** ambil dari cover dan bagian awal: judul makalah, nama kelompok, nama anggota, nama mata kuliah, dan nama dosen pengampu. Ambil daftar sub-materi dari Bab II (Pembahasan). Jumlahnya menentukan jumlah slide.

**Jika sumbernya bukan makalah** (tugas, studi kasus, laporan praktikum, jurnal): tidak ada Bab II, jadi tentukan alur dari isi sumber, misalnya latar/kasus, proses atau metode, hasil atau analisis, kesimpulan. Siapkan 1 sampai 2 opsi struktur, masing-masing dengan jumlah slidenya, untuk ditawarkan di Langkah 2 (kecuali pengguna sudah memberi struktur).

**Identitas:** judul, kelompok, anggota, mata kuliah, dosen. Jika ada yang tidak ditemukan di sumber, masukkan ke pertanyaan Langkah 2. Jangan mengarang nama. Untuk tugas individu, pakai nama pembuat dan lewati kelompok.

**Universitas, fakultas, dan program studi:** jika cover sumber memuat nama universitas, fakultas, atau program studi (misalnya hasil skill `makalah-unri` atau `makalah-unri-si`), catat untuk slide pembuka (lihat Langkah 4). Logo kampus tidak dimasukkan ke slide, dan gambar logo di cover tidak diambil sebagai gambar isi.

**Teks footer**, dari identitas:
- `[Mata kuliah] | Kelompok [N]` jika kelompok bernomor.
- `[Mata kuliah] | Kelompok [Nama]` jika kelompok bernama.
- `[Mata kuliah] | [Nama pembuat]` untuk tugas individu.
- Hanya `[Mata kuliah]` jika sumber tidak menyebut kelompok dan pengguna tidak menjawab.

Jika nama mata kuliah lebih dari 4 kata, ringkas.

**Bahasa:** slide dan notes memakai Bahasa Indonesia baku tapi tidak kaku. Jika sumber berbahasa Inggris, tetap tulis slide dalam Bahasa Indonesia, pertahankan istilah teknis asing (dengan padanannya bila ada), dan jangan menerjemahkan nama, judul rujukan, atau kutipan langsung. Dengan `--en`, semua teks (termasuk heading "Slide N" di dokumen notes) memakai Bahasa Inggris.

## Langkah 2: Tanyakan yang belum diketahui (satu putaran)

Semua pertanyaan diajukan dalam satu kali AskUserQuestion, dan tidak ada putaran tanya kedua. Jangan menanyakan hal yang sudah dijawab lewat flag atau kalimat pengguna. Tool ini membatasi 3 pertanyaan; jika yang belum diketahui lebih banyak, pilih 3 berdasarkan prioritas di bawah, dan untuk sisanya pakai bawaan lalu sebutkan di balasan akhir.

Prioritas dan isi pertanyaan:
1. **Identitas yang hilang** (judul, anggota, mata kuliah, dosen, nama atau nomor kelompok): pertanyaan terbuka, jawaban lewat pilihan "Other". Tunggu jawaban, jangan mengarang.
2. **Struktur dan jumlah slide:** tanyakan hanya jika belum disebut dan (a) sumbernya bukan makalah berstruktur bab, atau (b) sub-materinya lebih dari 8. Untuk (a), opsi yang ditampilkan adalah 1 sampai 2 struktur dari Langkah 1 beserta jumlah slidenya.
3. **Warna:** tanyakan hanya jika pengguna tidak memberi flag atau permintaan warna. Opsi: hijau, navy, marun, teal. Sebutkan di teks pertanyaan bahwa cokelat, hitam, atau warna sendiri bisa diketik lewat "Other".
4. **Font:** tanyakan hanya jika belum disebut dan tidak ada `--fontaman`. Opsi: "Poppins + Lato (laptop sendiri, font sudah terpasang)" atau "Calibri (komputer kampus, Canva, atau tidak yakin)".

Jika tidak ada tool untuk bertanya atau pengguna tidak sedang memantau (sesi berjalan sendiri): pakai `--navy`, font aman (Calibri, seperti `--fontaman`), dan aturan jumlah slide bawaan, lalu sebutkan pilihan itu di balasan akhir. Jika identitas penting tidak ditemukan, kosongkan bagian itu dan sebutkan, jangan dikarang.

## Langkah 3: Tentukan jumlah slide

Dua istilah:
- **Slide inti:** pembuka, slide isi, penutup.
- **Slide tambahan:** slide Referensi (`--pustaka`) dan slide gambar penuh atau zoom untuk diagram.

Struktur dasar:
- Slide pembuka: judul, nama kelompok, anggota, mata kuliah, dan dosen.
- Slide isi: satu slide untuk tiap sub-materi (judul bab, pengertian, ciri, asas, dan seterusnya).
- Slide penutup: satu slide "Terima Kasih" dengan tulisan di tengah dan keterangan "Tanya Jawab". Slide ini berdiri sendiri, tidak digabung dengan kesimpulan. Jika pengguna melampirkan atau menyebut foto dokumentasi, foto boleh ditaruh di slide ini.

Urutan prioritas aturan jumlah:
1. **Jumlah dari pengguna** (`--slide=N` atau kalimat biasa) selalu menang dan total semua slide (inti + tambahan) harus tepat N. N minimal 5 (pembuka, tiga slide isi, penutup); jika kurang, pakai 5 dan beri tahu. Jika isi tidak muat, kurangi dengan urutan ini: gabungkan sub-materi yang berdekatan, buang slide zoom diagram, lalu lewati slide Referensi dan beri tahu pengguna. Pembuka dan penutup tidak pernah dibuang. Jika ada isi penting yang terpaksa dipangkas, sebutkan apa yang dipangkas.
2. **Tanpa angka dari pengguna:** jumlah mengikuti materi.
   - Sub-materi sampai 8: slide inti maksimal 10 (pembuka + sub-materi + penutup) dan boleh kurang dari 10 jika materinya memang sedikit. Jangan menambah atau memadatkan slide demi mengejar angka 10. Slide inti tidak kurang dari 5; jika sub-materi sangat sedikit dan isinya padat, pecah sub-materi jadi 2 slide supaya mencapai 5.
   - Sub-materi lebih dari 8: slide inti boleh lebih dari 10, mengikuti jumlah sub-materi. Beri tahu pengguna total slide yang dihasilkan.
   - Slide tambahan (Referensi, zoom diagram) boleh menambah total di atas batas 10 dan wajib disebut di balasan.

Tulis rencana slide (judul, sub-materi yang dicakup, dan layout tiap slide) sebelum membuat file. Jika pengguna meminta revisi jumlah slide, susun rencana baru dari awal, jangan menambal slide lama.

## Langkah 4: Isi slide

Aturan umum:
- Judul slide memakai nama bagian saja, tanpa nomor sub-bab seperti 2.4.1. Contoh: "Judul", "Pendahuluan", "Tinjauan Pustaka".
- **Slide ringkas, penjelasan di notes.** Tiap slide isi punya 3 sampai 4 poin, dan tiap poin berupa satu kalimat singkat (sekitar 15 kata atau kurang), total sekitar 50 kata per slide isi (judul, caption, dan footer tidak dihitung). Jangan menaruh dua kalimat dalam satu poin. Pengecualian: slide berlayout definisi besar atau angka besar boleh berisi satu elemen utama. Penjelasan, alasan, dan contoh lengkap pindah ke speaker notes (Langkah 5). Jika sebuah poin tidak bisa dipersingkat tanpa mengubah makna, pecah jadi dua slide (bila jumlah slide bebas) atau pindahkan sisanya ke notes. Jangan memperkecil huruf demi muat.
- Ukuran huruf isi minimal 16 pt. Caption, sitasi, dan footer minimal 11 pt.
- Setia pada sumber: angka, definisi, istilah, nama, dan ayat harus sama dengan sumber. Meringkas boleh, menambah fakta baru atau mengubah makna tidak.
- Ayat, definisi, atau contoh penting boleh ditulis utuh di kotak contoh.
- Kutipan di slide memakai format APA (Nama, tahun) atau (Nama & Nama, tahun) atau (Nama dkk., tahun). Jika sumber tidak memberi rujukan untuk suatu poin, jangan menambahkan sitasi.
- Daftar pustaka lengkap tidak ditampilkan di slide, kecuali pengguna memakai `--pustaka` (lihat di bawah).

**Slide pembuka:** selain judul, kelompok, anggota, mata kuliah, dan dosen, tampilkan nama universitas, fakultas, dan program studi jika ada di cover sumber, persis seperti tertulis di sumber, sebagai teks. Tanpa logo.

**Variasi layout.** Pilih layout sesuai isi, dan jangan pakai layout yang sama tiga slide isi berturut-turut:
- baris bernomor: daftar poin berurutan.
- kartu dengan aksen: daftar sejajar atau perbandingan 2 sampai 4 hal.
- timeline: urutan tahap atau bagian.
- dua kolom: perbandingan dua konsep (misalnya kelebihan dan kekurangan).
- definisi besar: satu definisi atau kutipan penting dengan huruf besar di kotak warna utama.
- angka besar: satu atau dua statistik yang jadi inti slide, dengan keterangan singkat.

Gambar dan diagram:
- Ambil dari .docx dengan membuka zip-nya (folder `word/media`), atau dari PDF dengan `pdftoppm -r 200 -png -f N -l N` lalu crop dengan PIL.
- Jaga rasio, jangan di-stretch. Resolusi minimal sekitar 150 dpi pada ukuran tampil.
- Taruh gambar di kartu dengan garis warna utama dan beri caption "Gambar N. ..." sesuai sumber.
- Diagram besar: satu slide untuk gambar penuh, lalu slide atau potongan zoom per bagian dengan kotak penanda di gambar penuh.
- Semua gambar, diagram, foto, dan rumus wajib punya alt text (`altText` di pptxgenjs) yang menjelaskan isinya dalam satu kalimat. Ikon dekoratif tidak perlu.

Tabel: maksimal 5 baris dan 4 kolom per slide. Header berupa kotak warna utama dengan teks `teks_di_utama`. Tabel yang lebih besar diringkas jadi kartu atau dipecah.

Rumus:
- Rumus sederhana satu baris (misalnya `n! = n x (n-1) x ... x 1`) ditulis sebagai teks biasa di kotak contoh.
- Rumus dengan pecahan, akar, atau binomial dirender: `python3 <skill>/scripts/render_rumus.py --color <utama> --size 32 --out rumus1.png "\binom{n}{k}=\frac{n!}{k!(n-k)!}"`. Tempel sebagai gambar di kotak contoh, satu rumus per baris, dan beri alt text berisi rumusnya dalam kata-kata.
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

**Dokumen .docx** (pakai skill docx), Times New Roman 12:
- Judul dokumen, lalu baris "Perkiraan total durasi: ±N menit (±K kata)". Hitung jumlah kata naskah dengan script sebelum menulis dokumen.
- Per slide: heading "Slide N: [judul slide]" dan naskahnya.
- Di akhir: bagian **Pertanyaan Antisipasi**.

**Pertanyaan Antisipasi:** 3 sampai 5 pasang pertanyaan dan jawaban yang kemungkinan muncul saat tanya jawab (definisi yang sering disalahpahami, "kenapa", "apa bedanya", contoh penerapan). Jawaban 1 sampai 3 kalimat dan berdasar sumber. Jika jawaban perlu informasi di luar sumber, beri tanda "(di luar sumber, periksa ulang)". Bagian ini hanya di .docx, tidak masuk slide. Dengan `--bagi`, tulis di tiap pertanyaan anggota yang sebaiknya menjawab (yang membawakan slide terkait).

Jika `--bagi` aktif:
- Pakai daftar anggota dari sumber. Jika tidak ada, sudah ditanyakan di Langkah 2.
- Pembuka dibawakan anggota pertama, penutup oleh anggota terakhir. Slide isi dibagi berurutan dan sebisa mungkin merata menurut durasi. Slide bersambung dalam satu sub-materi sebaiknya dibawakan orang yang sama. Jika anggota lebih banyak dari slide, sebagian anggota tidak kebagian slide; sebutkan itu ke pengguna.
- Durasi tiap slide diambil dari pembagian di atas, dibulatkan ke 0,5 menit, dan totalnya tetap sesuai batas durasi.
- Baris pertama notes tiap slide, di PPT dan di .docx: `Pembicara: [Nama] | Durasi: ±N menit`, baru naskahnya.
- Di .docx, taruh tabel ringkasan (Slide, Judul, Pembicara, Durasi) tepat setelah judul dokumen, berikut total durasi.

Tanpa `--bagi`, jangan tambahkan baris pembicara atau durasi per slide.

## Langkah 6: Desain

Palet: jalankan `python3 <skill>/scripts/palette.py <flag>` (contoh `--hijau`, atau `"--warna=#7A1F5C"`) dan pakai JSON hasilnya: `bg` untuk latar isi, `utama` untuk teks dan elemen utama, `aksen` untuk garis judul, `teks_di_utama` untuk **semua** teks di atas latar atau kotak warna utama (jangan menulis kode warna krem langsung). Script adalah sumber kebenaran; tabel di bawah hanya rujukan.

| Flag | Utama | Catatan |
|---|---|---|
| `--hijau` | #1E4D3B | |
| `--navy` | #1B2A4A | |
| `--marun` | #6B1E2E | |
| `--teal` | #134E4A | |
| `--cokelat` | #4A2F1F | |
| `--hitam` | #1C1C1E | aksen emas #B08D3C hanya untuk garis judul |
| `--warna=...` | dari pengguna | digelapkan otomatis jika kontras terhadap krem di bawah 4.5 |

Latar isi memakai `bg` (krem #F5EFE0). Latar pembuka dan penutup memakai warna utama, dengan teks `teks_di_utama`. Selain palet dari script, jangan menambah warna lain. Jika script menggelapkan warna sendiri dari pengguna, sebutkan hasilnya di balasan akhir.

Font:
- Bawaan: judul Poppins (bold), isi Lato (regular), teks Arab Amiri.
- Font aman (`--fontaman`, pilihan "Calibri" di Langkah 2, pengguna bilang tidak bisa memasang font seperti di Canva atau laptop kampus, atau sesi tanpa pemantauan): judul dan isi Calibri (judul bold), teks Arab Traditional Arabic.
- Cek dengan `fc-list | grep -iE "poppins|lato|amiri"`. Jika tidak terpasang di mesin render, hasil render memakai font pengganti dan hanya perkiraan.
- File PPT dari pptxgenjs tidak menyematkan font. Jika memakai font bawaan, ingatkan pengguna di balasan akhir bahwa Poppins, Lato, dan Amiri harus terpasang di komputer yang membuka PPT.

Komposisi slide isi:
- Judul di kiri atas, dengan garis pendek warna aksen di bawahnya.
- Ikon kecil di kanan atas, warna utama, sesuai topik slide. Render sekaligus: `node <skill>/scripts/make_icons.mjs --color <utama> --out ikon FaBook MdSchool ...`. Jika `require('pptxgenjs')` gagal saat membuat PPT, jalankan node dengan `NODE_PATH=$(npm root -g)`.
- Lingkaran dekoratif warna utama transparan (transparency sekitar 90) di pojok slide, dengan posisi berbeda di tiap slide.
- Isi memakai salah satu layout di Langkah 4. Kotak warna utama dipakai untuk contoh judul atau contoh kalimat.
- Footer kecil di kiri bawah dengan teks dari Langkah 1.
- Hindari gradasi, emoji, dan clipart generik.

**Penamaan objek untuk Morph.** PowerPoint hanya memasangkan objek berdasarkan nama jika namanya diawali `!!`. Tanpa awalan itu, Morph menebak pasangan dari kemiripan dan bisa jatuh ke efek fade. Karena itu beri `objectName` persis berikut di setiap slide: `!!judul`, `!!garisJudul`, `!!ikon`, `!!orb`, `!!orbKecil`, `!!footer`. Posisi lingkaran dan ikon boleh berbeda antar slide, sehingga Morph akan menggeser dan mengubah ukurannya secara halus. Gambar, tabel, dan rumus diberi nama unik per slide tanpa awalan `!!`.

## Langkah 7: Transisi Morph

Pasang transisi Morph di semua slide, termasuk pembuka dan penutup. Simpan PPT mentah dari pptxgenjs dengan nama sementara, lalu jalankan:

```
python3 <skill>/scripts/add_morph.py PPT-mentah.pptx "/mnt/user-data/outputs/PPT - [judul].pptx"
```

Script menyisipkan blok Morph setelah `</p:clrMapOvr>` di setiap `ppt/slides/slideN.xml`, aman dijalankan ulang, dan memberi peringatan jika ada slide yang tidak memiliki objek bernama `!!...`. Jika ada peringatan, perbaiki penamaan di build lalu ulangi. Hanya file final yang disimpan di folder outputs.

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
- Kepadatan: 3 sampai 4 poin satu kalimat singkat, sekitar 50 kata per slide isi, huruf isi minimal 16 pt.
- Variasi: tidak ada tiga slide isi berturut-turut dengan layout sama.
- Warna hanya dari palet hasil `palette.py`.
- Alt text ada di semua gambar, diagram, foto, dan rumus.
- Morph terpasang: jumlah kemunculan `p159:morph` di setiap file slide sama dengan 1, dan `add_morph.py` tidak memberi peringatan nama `!!`.
- Validasi file: jalankan `scripts/office/validate.py` dari skill pptx. Jika script itu tidak ada, minimal pastikan file terbuka dengan `python3 -c "from pptx import Presentation; Presentation('<file>.pptx')"`.
- Render ke gambar (`soffice --headless --convert-to pdf`, lalu `pdftoppm -r 80 -png`) dan periksa semua slide: teks tidak terpotong, elemen tidak tumpang tindih, gambar tidak ter-stretch, ikon tampil. Untuk teks Arab, pastikan arah kanan ke kiri benar dan harakat tidak hilang.

## Revisi

Saat pembuatan, simpan script build (misalnya `build.js`) beserta data isi slide di folder kerja, jangan hanya menjalankan sekali lalu membuangnya. Dengan begitu:
- Ganti warna, font, footer, atau teks satu slide: ubah parameternya lalu jalankan ulang build, tidak perlu menyusun ulang semuanya. Lalu ulangi Langkah 7 sampai 8.
- Ganti jumlah slide: susun rencana baru dari awal (Langkah 3).
- Jika script build sudah tidak ada (sesi baru), buka PPT final dengan skill pptx, edit slide yang diminta saja, lalu jalankan ulang `add_morph.py` (aman dijalankan ulang) dan perbarui dokumen notes untuk slide yang berubah.

Revisi atas file yang sama menimpa file itu. Permintaan baru dari sumber lain mengikuti aturan nama di bagian Output.

## Output

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

Balas pengguna dalam satu sampai tiga kalimat: jumlah slide (sebut jika slide tambahan membuat total melewati 10, atau ada isi yang dipangkas), perkiraan durasi presentasi, nama dua file (sebut judul ringkasnya jika judul diubah), palet dan font yang dipakai (sebut jika warnanya digelapkan otomatis atau memakai font aman karena tidak bertanya), dan satu hal yang perlu dicek manual (misalnya tampilan Morph di PowerPoint, font yang harus terpasang, atau angka hasil OCR).

## Catatan versi

Versi saat ini: v2.2. Riwayat lengkap perubahan tiap versi ada di `CHANGELOG.md` di folder skill ini.
