---
name: "dokumen-ke-ppt"
description: Ubah dokumen akademik (makalah, tugas, studi kasus, laporan; .docx, .pdf, .md, teks) jadi PPT presentasi berbahasa Indonesia dengan transisi Morph, kutipan APA, dan speaker notes terpisah (.docx). Pakai saat pengguna minta bikin PPT, slide, atau presentasi kelompok dari dokumen apa pun. Warna dipilih lewat flag (--hijau, --navy, --marun, --teal, --cokelat, --hitam, atau --warna=...), plus --bagi, --pustaka, --slide=N.
---

# Dokumen ke PPT

Skill ini mengubah dokumen akademik (makalah, tugas, studi kasus, laporan) menjadi file .pptx siap presentasi, plus dokumen .docx berisi speaker notes. Dipakai ketika pengguna meminta "buatkan PPT dari makalah", "bikin slide presentasi", atau memberikan dokumen apa pun dan minta dibuatkan slide.

Folder skill ini berisi script pendukung di `scripts/`. Di bawah, `<skill>` berarti folder skill ini.

| Script | Fungsi |
|---|---|
| `palette.py` | Ubah flag warna jadi palet (JSON) dan cek kontras |
| `add_morph.py` | Pasang transisi Morph di semua slide |
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
| `--slide=N` | Jumlah slide total, tepat N |

Jika ada lebih dari satu flag warna, pakai yang pertama dan beri tahu pengguna.

## Langkah 0: Tanyakan yang belum diketahui

Kumpulkan semua pertanyaan yang jawabannya belum ada, lalu ajukan dalam satu kali AskUserQuestion. Jangan menanyakan hal yang sudah dijawab lewat flag atau kalimat pengguna.

- Warna: tanyakan hanya jika pengguna tidak memberi flag atau permintaan warna. Opsi yang ditampilkan: hijau, navy, marun, teal. Sebutkan di teks pertanyaan bahwa cokelat, hitam, atau warna sendiri bisa diketik lewat pilihan "Other".
- Jumlah slide: tanyakan hanya jika belum disebut dan (a) sumbernya bukan makalah berstruktur bab, atau (b) sub-materinya lebih dari 8.
- Struktur slide untuk sumber non-makalah: lihat Langkah 1.

Jika tidak ada tool untuk bertanya atau pengguna tidak sedang memantau (sesi berjalan sendiri): pakai `--navy` dan aturan jumlah slide bawaan, lalu sebutkan pilihan itu di balasan akhir.

## Langkah 1: Baca sumber dan ambil data pembuka

Baca seluruh sumber.

**Jika sumbernya makalah:** ambil dari cover dan bagian awal: judul makalah, nama kelompok, nama anggota, nama mata kuliah, dan nama dosen pengampu. Ambil daftar sub-materi dari Bab II (Pembahasan). Jumlahnya menentukan jumlah slide.

**Jika sumbernya bukan makalah** (tugas, studi kasus, laporan praktikum, jurnal): tidak ada Bab II, jadi tentukan alur dari isi sumber, misalnya latar/kasus, proses atau metode, hasil atau analisis, kesimpulan. Kecuali pengguna sudah memberi struktur, tawarkan 1 sampai 2 opsi struktur lewat AskUserQuestion, masing-masing dengan jumlah slidenya.

**Identitas:** judul, kelompok, anggota, mata kuliah, dosen. Jika ada yang tidak ditemukan di sumber, tanyakan dan tunggu jawaban. Jangan mengarang nama. Untuk tugas individu, pakai nama pembuat dan lewati kelompok.

Dari identitas, tentukan teks footer: `[Mata kuliah] | Kelompok [N]`, atau `[Mata kuliah] | [Nama pembuat]` untuk tugas individu. Jika nama mata kuliah lebih dari 4 kata, ringkas.

## Langkah 2: Tentukan jumlah slide

Struktur dasar:
- Slide pembuka: judul, nama kelompok, anggota, mata kuliah, dan dosen.
- Slide isi: satu slide untuk tiap sub-materi (judul bab, pengertian, ciri, asas, dan seterusnya).
- Slide penutup: satu slide "Terima Kasih" dengan tulisan di tengah dan keterangan "Tanya Jawab". Slide ini berdiri sendiri, tidak digabung dengan kesimpulan. Jika pengguna melampirkan atau menyebut foto dokumentasi, foto boleh ditaruh di slide ini.

Urutan prioritas aturan jumlah:
1. Jumlah dari pengguna (`--slide=N` atau kalimat biasa) selalu menang dan harus tepat. Jika isi tidak muat, gabungkan sub-materi yang berdekatan. Jika ada isi penting yang terpaksa dipangkas, beri tahu pengguna apa yang dipangkas.
2. Jika tidak ada angka dari pengguna:
   - Sub-materi 5 sampai 8: total usahakan maksimal 10 slide termasuk pembuka dan penutup.
   - Sub-materi lebih dari 8: total boleh lebih dari 10. Beri tahu pengguna total slide yang dihasilkan.
   - Sub-materi kurang dari 5 dan isinya padat: boleh 2 slide per sub-materi.

Slide tambahan dihitung dalam total: slide Referensi (`--pustaka`) dan slide gambar penuh atau zoom untuk diagram.

Tulis rencana slide (judul dan sub-materi yang dicakup) sebelum membuat file. Jika pengguna meminta revisi jumlah slide, susun rencana baru dari awal, jangan menambal slide lama.

## Langkah 3: Isi slide

Aturan umum:
- Judul slide memakai nama bagian saja, tanpa nomor sub-bab seperti 2.4.1. Contoh: "Judul", "Pendahuluan", "Tinjauan Pustaka".
- Setiap poin berisi 1 sampai 2 kalimat yang cukup informatif, bukan kata kunci saja. Maksimal 4 poin dan sekitar 70 kata per slide isi (judul, caption, dan footer tidak dihitung).
- Ukuran huruf isi minimal 16 pt. Caption, sitasi, dan footer minimal 11 pt.
- Setia pada sumber: angka, definisi, istilah, nama, dan ayat harus sama dengan sumber. Meringkas boleh, menambah fakta baru atau mengubah makna tidak.
- Ayat, definisi, atau contoh penting boleh ditulis utuh di kotak contoh.
- Kutipan di slide memakai format APA (Nama, tahun) atau (Nama & Nama, tahun) atau (Nama dkk., tahun).
- Daftar pustaka lengkap tidak ditampilkan di slide, kecuali pengguna memakai `--pustaka` (lihat di bawah).
- Bahasa slide Bahasa Indonesia baku tapi tidak kaku.

Gambar dan diagram:
- Ambil dari .docx dengan membuka zip-nya (folder `word/media`), atau dari PDF dengan `pdftoppm -r 200 -png -f N -l N` lalu crop dengan PIL.
- Jaga rasio, jangan di-stretch. Resolusi minimal sekitar 150 dpi pada ukuran tampil.
- Taruh gambar di kartu dengan garis warna utama dan beri caption "Gambar N. ..." sesuai sumber.
- Diagram besar: satu slide untuk gambar penuh, lalu slide atau potongan zoom per bagian dengan kotak penanda di gambar penuh.

Tabel: maksimal 5 baris dan 4 kolom per slide. Header berupa kotak warna utama dengan teks krem. Tabel yang lebih besar diringkas jadi kartu atau dipecah.

Rumus:
- Rumus sederhana satu baris (misalnya `n! = n x (n-1) x ... x 1`) ditulis sebagai teks biasa di kotak contoh.
- Rumus dengan pecahan, akar, atau binomial dirender: `python3 <skill>/scripts/render_rumus.py --color <utama> --size 32 --out rumus1.png "\binom{n}{k}=\frac{n!}{k!(n-k)!}"`. Tempel sebagai gambar di kotak contoh, satu rumus per baris, dan beri alt text.

Teks Arab (ayat, doa):
- Font Amiri (cadangan: Traditional Arabic), ukuran minimal 24 pt, rata kanan, dengan `rtlMode: true` dan `lang: "ar-SA"` di pptxgenjs.
- Terjemahan di bawahnya memakai font isi, lalu sumber (QS. Nama: ayat).
- Salin teks Arab persis dari sumber, jangan diketik ulang dari ingatan.

Slide Referensi (hanya jika `--pustaka`): letakkan sebelum slide Terima Kasih, judul "Referensi". Tampilkan hanya referensi yang dikutip di slide, format APA persis seperti di sumber, huruf minimal 11 pt, maksimal 8 entri per slide (lebih dari itu jadi 2 slide).

## Langkah 4: Speaker notes

- Setiap slide wajib punya speaker notes 3 sampai 5 kalimat dalam Bahasa Indonesia, disimpan di kolom notes slide (bukan kotak teks di slide).
- Notes menjelaskan poin di slide dengan kata-kata sendiri, bukan sekadar mengulang slide.
- Setelah PPT jadi, buat dokumen .docx terpisah berisi notes semua slide (pakai skill docx). Format: judul dokumen, lalu per slide ada heading "Slide N: [judul slide]" dan paragraf notes-nya. Gunakan Times New Roman 12.
- Slide pembuka dan penutup juga punya notes.

Jika `--bagi` aktif:
- Pakai daftar anggota dari sumber. Jika tidak ada, tanyakan.
- Pembuka dibawakan anggota pertama, penutup oleh anggota terakhir. Slide isi dibagi berurutan dan sebisa mungkin merata. Slide bersambung dalam satu sub-materi sebaiknya dibawakan orang yang sama.
- Durasi: jika pengguna menyebut total durasi (misalnya 15 menit), bagi sebanding jumlah slide isi dengan pembuka dan penutup sekitar 30 detik masing-masing. Jika tidak ada, pakai 1 menit per slide isi. Bulatkan ke 0,5 menit.
- Baris pertama notes tiap slide, di PPT dan di .docx: `Pembicara: [Nama] | Durasi: ±N menit`, baru 3 sampai 5 kalimat notes.
- Di .docx, taruh tabel ringkasan (Slide, Judul, Pembicara, Durasi) tepat setelah judul dokumen, berikut total durasi.

Tanpa `--bagi`, jangan tambahkan baris pembicara atau durasi.

## Langkah 5: Desain

Palet: jalankan `python3 <skill>/scripts/palette.py <flag>` (contoh `--hijau`, atau `"--warna=#7A1F5C"`) dan pakai JSON hasilnya: `bg` untuk latar isi, `utama` untuk teks dan elemen utama, `aksen` untuk garis judul, `teks_di_utama` untuk teks di atas latar utama. Script adalah sumber kebenaran; tabel di bawah hanya rujukan.

| Flag | Utama | Catatan |
|---|---|---|
| `--hijau` | #1E4D3B | |
| `--navy` | #1B2A4A | |
| `--marun` | #6B1E2E | |
| `--teal` | #134E4A | |
| `--cokelat` | #4A2F1F | |
| `--hitam` | #1C1C1E | aksen emas #B08D3C hanya untuk garis judul |
| `--warna=...` | dari pengguna | digelapkan otomatis jika kontras terhadap krem di bawah 4.5 |

Latar isi selalu krem #F5EFE0. Latar pembuka dan penutup memakai warna utama, dengan teks krem. Selain palet dari script, jangan menambah warna lain. Jika script menggelapkan warna sendiri dari pengguna, sebutkan hasilnya di balasan akhir.

Font:
- Judul: Poppins (bold).
- Isi: Lato (regular).
- Teks Arab: Amiri.
- Cek dengan `fc-list | grep -iE "poppins|lato|amiri"`. Jika tidak terpasang di mesin render, hasil render memakai font pengganti dan hanya perkiraan.
- Jika pengguna bilang tidak bisa memasang font (Canva, laptop kampus), ganti judul dan isi ke Calibri.

Komposisi slide isi:
- Judul di kiri atas, dengan garis pendek warna aksen di bawahnya.
- Ikon kecil di kanan atas, warna utama, sesuai topik slide. Render sekaligus: `node <skill>/scripts/make_icons.mjs --color <utama> --out ikon FaBook MdSchool ...`. Jika `require('pptxgenjs')` gagal saat membuat PPT, jalankan node dengan `NODE_PATH=$(npm root -g)`.
- Lingkaran dekoratif warna utama transparan (transparency sekitar 90) di pojok slide, dengan posisi berbeda di tiap slide.
- Isi berupa baris bernomor (kotak warna utama dengan nomor di kiri), kartu dengan aksen warna utama di atas (untuk perbandingan atau daftar yang sejajar), atau timeline untuk urutan bagian.
- Kotak warna utama untuk contoh judul atau contoh kalimat.
- Footer kecil di kiri bawah dengan teks dari Langkah 1 (`[Mata kuliah] | Kelompok [N]`).
- Hindari gradasi, emoji, dan clipart generik.

Untuk Morph, beri nama objek (objectName) yang sama untuk elemen yang sama di setiap slide: "judul", "garisJudul", "ikon", "orb", "orbKecil", "footer". Posisi lingkaran dan ikon boleh berbeda antar slide, sehingga Morph akan menggeser dan mengubah ukurannya secara halus. Gambar, tabel, dan rumus diberi nama unik per slide.

## Langkah 6: Transisi Morph

Pasang transisi Morph di semua slide, termasuk pembuka dan penutup. Simpan PPT mentah dari pptxgenjs dengan nama sementara, lalu jalankan:

```
python3 <skill>/scripts/add_morph.py PPT-mentah.pptx /mnt/user-data/outputs/PPT-[judul singkat].pptx
```

Script menyisipkan blok Morph setelah `</p:clrMapOvr>` di setiap `ppt/slides/slideN.xml` dan aman dijalankan ulang. Hanya file final yang disimpan di folder outputs.

LibreOffice tidak menampilkan Morph (jatuh ke fade), jadi Morph hanya bisa diperiksa langsung di PowerPoint 2019 atau 365.

## Langkah 7: Cek hasil

- Jumlah slide sesuai Langkah 2 (`--slide=N` jika ada).
- Footer benar: mata kuliah dan kelompok sesuai sumber.
- Judul slide tidak memakai nomor sub-bab.
- Slide "Terima Kasih" berdiri sendiri di akhir (setelah Referensi jika ada).
- Setiap slide punya speaker notes 3 sampai 5 kalimat. Dengan `--bagi`: baris Pembicara dan Durasi ada di semua slide dan total durasi masuk akal.
- Setiap kutipan memakai format APA di slide dan ada di daftar pustaka sumber. Tidak ada daftar pustaka di slide kecuali `--pustaka`.
- Kesetiaan isi: cocokkan semua angka, definisi, nama, dan ayat di slide dengan sumber. Tidak ada fakta baru.
- Kepadatan: maksimal 4 poin dan sekitar 70 kata per slide isi, huruf isi minimal 16 pt.
- Warna hanya dari palet hasil `palette.py`.
- Morph terpasang: jumlah kemunculan `p159:morph` di setiap file slide sama dengan 1.
- Jalankan `scripts/office/validate.py` dari skill pptx, lalu render ke gambar (`soffice --headless --convert-to pdf`, lalu `pdftoppm -r 80 -png`) dan periksa semua slide: teks tidak terpotong, elemen tidak tumpang tindih, gambar tidak ter-stretch, ikon tampil. Untuk teks Arab, pastikan arah kanan ke kiri benar dan harakat tidak hilang.

## Output

- File PPT: /mnt/user-data/outputs/PPT-[judul singkat].pptx
- File notes: /mnt/user-data/outputs/Speaker-Notes-[judul singkat].docx
- Sajikan kedua file dengan tool pengiriman file yang tersedia (SendUserFile atau present_files).

Balas pengguna dalam satu sampai tiga kalimat: jumlah slide, nama dua file, palet yang dipakai (sebut jika warnanya digelapkan otomatis), dan satu hal yang perlu dicek manual (misalnya tampilan Morph di PowerPoint, atau font yang harus terpasang).

## Catatan versi

- v1 (saat ini): rilis pertama dengan nama `dokumen-ke-ppt`, melanjutkan skill `makalah-ke-ppt` (v1 sampai v3). Isi: palet dipilih lewat flag (hijau, navy, marun, teal, cokelat, hitam, atau warna sendiri) dan ditanyakan jika tidak disebut; footer dinamis dari mata kuliah dan kelompok; jumlah slide dari pengguna selalu menang; alur untuk sumber non-makalah; panduan gambar, tabel, rumus, dan teks Arab; flag `--bagi`, `--pustaka`, `--slide=N`; batas kepadatan teks; cek kesetiaan isi; script `palette.py`, `add_morph.py`, `make_icons.mjs`, `render_rumus.py`. Nama diganti karena sumbernya tidak lagi terbatas pada makalah.
