# Menentukan jumlah slide

Rujukan untuk Langkah 3 di `SKILL.md`.

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
