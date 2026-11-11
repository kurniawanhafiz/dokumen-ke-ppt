# Membaca sumber dan data pembuka

Rujukan untuk Langkah 1 di `SKILL.md`. Pembacaan sumber kini dibantu `scripts/baca_sumber.py` (teks bersih, pustaka terpisah, logo, gambar, deteksi template, OCR otomatis); isi di bawah menjelaskan aturan dan cara manual bila script tidak bisa dipakai.

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
