# Speaker notes dan pertanyaan antisipasi

Rujukan untuk Langkah 5 di `SKILL.md`.

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
