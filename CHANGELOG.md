# Changelog

Riwayat perubahan skill `dokumen-ke-ppt`, dari yang terbaru. Skill ini melanjutkan `makalah-ke-ppt` (v1 sampai v3). Karena namanya baru, penomoran dimulai lagi dari v1.

Kembali ke [README](README.md) | [README (English)](README.en.md)

## v3.0

**Baru**
- 30 tema visual dengan gambar latar (`--tema=<nama atau nomor>`), lengkap dengan palet, font judul, dan cek kontras. `--tema=rekomendasi` memilih tema dari topik (judul dan mata kuliah). Daftar tema: `python3 scripts/gaya.py --daftar`.
- Tipe slide baru: grafik native (batang, batang horizontal, garis, donat, pie), tabel native, statistik, kutipan, `contoh` (soal, langkah atau rumus, kesimpulan), pembatas bab, dan Agenda yang bisa diklik ke tiap bab.
- Agenda dan pembatas bab dibuat otomatis jika sumber punya 3 bab atau lebih dan tidak ada `--slide=N`. Keduanya slide tambahan dan wajib disebut di balasan.
- Gaya kata ditanyakan dan bisa lewat flag: `--singkat` (bawaan, 3 sampai 4 poin sekitar 50 kata), `--padat` (4 sampai 5 poin kalimat utuh sekitar 80 kata), `--poin` (3 poin, 6 kata atau kurang). Speaker notes tetap lengkap di semua gaya kata.
- 102 ikon Lucide yang dipilih otomatis dari kata kunci dan diwarnai mengikuti tema (`scripts/ikon.py`). Lisensi ikon di `aset/ikon/LICENSE-lucide.txt`.
- Pembuat otomatis dari satu berkas `isi.json`: `bangun_ppt.js` (PPT) dan `buat_notes.js` (dokumen Speaker Notes). Pembuat memberi peringatan untuk slide tanpa catatan, gambar tanpa alt text, tabel kebesaran, dan slide `contoh` yang meluap.
- Logo dipakai jika ada: dilampirkan pengguna, atau diambil dari cover sumber hasil `makalah-unri` atau `makalah-unri-si`. Tampil kecil di slide pembuka. Tanpa logo, tidak ada placeholder.
- `render_rumus.py --batch` untuk merender banyak rumus sekaligus.

**Berubah**
- Flag warna disatukan menjadi `--warna=<nama atau hex>` (`--warna=hijau`, `--warna=navy`, dan seterusnya). Bentuk lama `--hijau` dan sejenisnya tidak lagi didokumentasikan, tetapi masih diterima diam-diam oleh `palette.py`.
- `--tema` mengalahkan `--warna` jika keduanya ada, dan pengguna diberi tahu.
- Pertanyaan di Langkah 2 menjadi: identitas, struktur dan jumlah slide, gaya visual (tema atau warna), gaya kata, lalu font. Tool bertanya tetap maksimal 3 pertanyaan per putaran, sisanya memakai bawaan.
- Rumus dirender dengan warna `ink` tema, bukan warna utama.
- Sampul memakai panel sehingga judul tidak tertimpa gambar latar.
- README memuat cara pasang di Claude Code, OpenClaw, dan Hermes Agent, dan daftar persyaratan diperbarui (`pptxgenjs`, `docx`, `sharp`, `python-pptx`; react-icons tidak lagi dipakai).
- Di agen selain aplikasi Claude: pertanyaan boleh dikirim sebagai satu pesan bernomor jika tidak ada tool bertanya, dan hasil disimpan di folder kerja jika `/mnt/user-data/outputs/` tidak ada.

**Dihapus**
- `scripts/make_icons.mjs` (ikon react-icons) diganti ikon Lucide dan `scripts/ikon.py`.

**Catatan**
- Video latar sengaja tidak dipakai: file jadi berat dan tidak tampil di Google Slides atau Canva.
- Sesi tanpa pemantauan memakai `--warna=navy` polos, font aman, dan `--singkat`.

## v2.2

**Berubah**
- Aturan `[judul]` pada nama file diganti. Batasnya 70 karakter, dan judul yang lebih panjang tidak lagi dipotong di batas kata.
  - Judul 70 karakter atau kurang dipakai apa adanya.
  - Jika lebih panjang, subjudul (bagian setelah titik dua, " - ", atau "–") dibuang dulu.
  - Jika masih panjang, judul diringkas jadi frasa inti yang utuh, maksimal 70 karakter, tanpa tanda titik tiga dan tanpa berakhir pada kata sambung atau kata depan.
- Judul yang dipakai untuk nama file disebut di balasan jika berbeda dari judul sumber. Judul di slide pembuka tetap lengkap.
- Langkah cek hasil ikut memeriksa panjang nama file dan memastikan kedua file memakai `[judul]` yang sama.

## v2.1

**Berubah**
- `--slide=N` minimal 5 (sebelumnya 3). Jika kurang dari 5, dipakai 5 dan pengguna diberi tahu.
- Tanpa angka dari pengguna, jumlah slide mengikuti materi: maksimal 10 untuk sub-materi sampai 8 (boleh kurang), dan boleh lebih dari 10 jika sub-materi lebih dari 8.
- Slide dibuat lebih ringkas: 3 sampai 4 poin, satu kalimat singkat per poin, sekitar 50 kata per slide isi (sebelumnya sekitar 70 kata).
- Speaker notes menjadi naskah lengkap untuk presentasi maksimal 15 menit (atau durasi lain dari pengguna), dengan patokan 130 kata per menit dan pembagian porsi per slide. Aturan lama "3 sampai 5 kalimat" dihapus. Dokumen notes memuat perkiraan total durasi.
- Nama file output menjadi `PPT - [judul].pptx` dan `Speaker Notes - [judul].docx` dengan judul lengkap, dipotong di batas kata jika lebih dari 60 karakter (aturan pemotongan ini diganti di v2.2).

**Dihapus**
- Logo kampus tidak lagi dimasukkan. Nama universitas, fakultas, dan program studi tetap tampil sebagai teks di slide pembuka.

## v2

**Perbaikan aturan**
- Teks di atas warna utama selalu memakai `teks_di_utama`.
- Slide inti (pembuka, isi, penutup) dipisah dari slide tambahan (Referensi, zoom diagram). Batas 10 slide hanya untuk slide inti.
- Aturan kepadatan teks diselaraskan, dan kelebihan isi dipindah ke speaker notes.
- Semua pertanyaan ke pengguna digabung dalam satu putaran dengan prioritas: identitas yang hilang, struktur atau jumlah slide, warna, lalu font.
- `--slide=N` diberi batas minimal dan urutan pemangkasan (gabung sub-materi, buang slide zoom, lewati Referensi). Footer punya fallback jika nomor kelompok tidak ada.
- Aturan penamaan file dibersihkan dari karakter bermasalah dan tidak menimpa file lain.

**Perbaikan teknis**
- Nama objek Morph diawali `!!` (`!!judul`, `!!ikon`, dan seterusnya) agar PowerPoint memasangkan objek lewat nama. `add_morph.py` memberi peringatan jika nama itu tidak ada atau tidak konsisten antar slide.
- Flag baru `--fontaman` (Calibri dan Traditional Arabic) dan pertanyaan font. Di sesi tanpa pemantauan, font default menjadi font aman.
- Rumus dari .docx (OMML) dikonversi lewat pandoc, dan PDF scan dibaca lewat OCR tesseract.
- Fallback validasi file jika `validate.py` dari skill pptx tidak ada.

**Fitur baru**
- Bagian Pertanyaan Antisipasi (3 sampai 5 tanya jawab) di dokumen notes.
- Layout tambahan (dua kolom, definisi besar, angka besar) dan aturan variasi: tidak ada tiga slide isi berturut-turut dengan layout sama.
- Alur revisi: script build disimpan supaya perubahan kecil tidak perlu membangun ulang semuanya.
- Sumber berbahasa Inggris tetap menghasilkan slide Indonesia, dan flag `--en` untuk hasil berbahasa Inggris.
- Alt text wajib untuk semua gambar, diagram, dan rumus.
- Logo, fakultas, dan program studi dari cover UNRI dipakai di slide pembuka (logo dihapus di v2.1).

## v1

Rilis pertama dengan nama `dokumen-ke-ppt`, melanjutkan skill `makalah-ke-ppt` (v1 sampai v3). Nama diganti karena sumbernya tidak lagi terbatas pada makalah.

- Palet dipilih lewat flag (hijau, navy, marun, teal, cokelat, hitam, atau warna sendiri) dan ditanyakan jika tidak disebut.
- Footer dinamis dari mata kuliah dan kelompok.
- Jumlah slide dari pengguna selalu menang.
- Alur untuk sumber non-makalah.
- Panduan gambar, tabel, rumus, dan teks Arab.
- Flag `--bagi`, `--pustaka`, dan `--slide=N`.
- Batas kepadatan teks dan cek kesetiaan isi terhadap sumber.
- Script `palette.py`, `add_morph.py`, `make_icons.mjs`, dan `render_rumus.py`.
