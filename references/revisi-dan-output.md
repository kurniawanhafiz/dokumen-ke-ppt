# Revisi dan aturan output

Rujukan untuk bagian Revisi dan Output di `SKILL.md`.

Simpan `isi.json` (dan `gaya.json`, gambar, rumus) di folder kerja, jangan dibuang. Dengan begitu:
- Ganti tema, warna, font, footer, atau teks satu slide: ubah `gaya.json` atau `isi.json`, jalankan ulang `bangun_ppt.js`, `buat_notes.js`, dan `add_morph.py` (dengan `--gaya=gaya.json` dan `--transisi` yang sama), lalu ulangi Langkah 8. Jika memakai ulang rumus, render ulang dengan warna `ink` baru karena warnanya mengikuti tema.
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
