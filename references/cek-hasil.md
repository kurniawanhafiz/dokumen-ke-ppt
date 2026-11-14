# Daftar cek hasil

Rujukan untuk Langkah 8 di `SKILL.md`. Jalankan semua butir sebelum menyerahkan file.

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
- Transisi terpasang sesuai `--transisi`: untuk `morph`, setiap file slide memuat `p159:morph` tepat satu kali. Untuk `kombinasi`, pembatas bab memuat `p:push` dan slide grafik memuat `p:wipe`, selebihnya Morph. Untuk `fade`, tidak ada `p159:morph`. `add_morph.py` tidak memberi peringatan nama `!!` (kecuali mode `fade`).
- Tema PowerPoint selaras: `add_morph.py` dijalankan dengan `--gaya=gaya.json` dan melaporkan "Tema PowerPoint diselaraskan".
- `cek_isi.py` terakhir dijalankan tanpa ERROR pada `isi.json` yang dipakai membangun.
- Agenda (jika ada): nomor halaman di slide isi menaut ke Agenda.
- Validasi file: jalankan `scripts/office/validate.py` dari skill pptx. Jika script itu tidak ada, minimal pastikan file terbuka dengan `python3 -c "from pptx import Presentation; Presentation('<file>.pptx')"`.
- Agenda: tiap bab menautkan ke slide pembatas yang benar (jika ada Agenda). Logo tampil hanya jika ada.
- Render ke gambar (`soffice --headless --convert-to pdf`, lalu `pdftoppm -r 80 -png`) dan periksa semua slide: teks tidak terpotong, elemen tidak tumpang tindih, gambar tidak ter-stretch, ikon tampil. Untuk teks Arab, pastikan arah kanan ke kiri benar dan harakat tidak hilang.
