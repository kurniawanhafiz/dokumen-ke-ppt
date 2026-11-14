# Isi slide: kepadatan, layout, gambar, tabel, rumus, teks Arab, Referensi

Rujukan untuk Langkah 4 di `SKILL.md`.

Aturan umum:
- Judul slide memakai nama bagian saja, tanpa nomor sub-bab seperti 2.4.1. Contoh: "Judul", "Pendahuluan", "Tinjauan Pustaka".
- **Slide ringkas, penjelasan di notes.** Kepadatan mengikuti gaya kata (tanyakan di Langkah 2 atau flag), tanpa menghitung judul, caption, dan footer:

| Gaya kata | Poin per slide isi | Isi tiap poin | Total kata per slide |
|---|---|---|---|
| `--singkat` (bawaan) | 3 sampai 4 | satu kalimat singkat, sekitar 15 kata atau kurang | sekitar 50 |
| `--padat` | 4 sampai 5 | kalimat utuh, sekitar 20 kata atau kurang | sekitar 80 |
| `--poin` | 3 | frasa, 6 kata atau kurang, tanpa kalimat utuh | sekitar 20 |

  Jangan menaruh dua kalimat dalam satu poin. Pengecualian: slide berlayout definisi, angka, statistik, grafik, tabel, atau kutipan boleh berisi satu elemen utama. Penjelasan, alasan, dan contoh lengkap pindah ke speaker notes (Langkah 5), yang tetap lengkap di semua gaya kata. Jika sebuah poin tidak bisa dipersingkat tanpa mengubah makna, pecah jadi dua slide (bila jumlah slide bebas) atau pindahkan sisanya ke notes. Jangan memperkecil huruf demi muat. Skala huruf (diatur otomatis oleh `bangun_ppt.js`): judul slide 32pt; isi utama 16 sampai 24pt menurut jumlah dan panjang item, satu ukuran untuk item sejenis dalam satu slide; label kecil non-kalimat (footer, nomor halaman, label bab, sumber) 11 sampai 12pt. Isi kalimat tidak pernah di bawah 16pt; jika `cek_isi.py` atau build memberi peringatan 16pt, persingkat teksnya.
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
- `langkah`: alur proses 2 sampai 5 tahap, kepala berpanah bernomor dan kartu penjelasan di bawahnya. Pakai untuk prosedur atau tahapan kerja; pakai `garis` untuk urutan waktu atau urutan bagian.
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
