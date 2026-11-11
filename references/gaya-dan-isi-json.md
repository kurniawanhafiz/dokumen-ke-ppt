# Gaya visual, format isi.json, dan pembangunan

Rujukan untuk Langkah 6 di `SKILL.md`.

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
| `langkah` | `judul`, `langkah[{j, t}]` (2 sampai 5 tahap) |
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
python3 <skill>/scripts/cek_isi.py isi.json --gaya-kata=singkat --durasi=15 --tulis   # periksa dan rapikan dulu
node <skill>/scripts/bangun_ppt.js isi.json PPT-mentah.pptx
node <skill>/scripts/buat_notes.js isi.json "Speaker Notes - [judul].docx"
```

`cek_isi.py` adalah dry-run: menyeragamkan bentuk isi, memeriksa jumlah nilai grafik terhadap label (angka format Indonesia seperti `1.234,5` dibaca benar), batas item per slide, kepadatan kata menurut gaya kata, catatan yang kosong, total kata naskah terhadap durasi, berkas gambar, rumus, dan ikon, lalu menghitung total slide (bandingkan dengan `--slide=N` jika ada). Tambahkan `--pecah` hanya jika jumlah slide bebas: slide yang kelebihan item dipecah jadi "(lanjutan)" dan catatannya harus ditulis. Perbaiki semua ERROR sebelum membangun.

Jika `require('pptxgenjs')` atau `require('docx')` gagal, jalankan node dengan `NODE_PATH=$(npm root -g)`. Pembuat PPT menulis peringatan (stderr) untuk slide tanpa catatan, gambar tanpa alt text, ikon tidak ada, tabel melebihi 5 x 4, poin melebihi 5, dan slide `contoh` yang melebihi kartu. Perbaiki di `isi.json` lalu bangun ulang.

Komposisi yang dibuat otomatis: judul kiri atas dengan garis pendek warna aksen, ikon kanan atas, lingkaran dekoratif transparan, footer kiri bawah dan nomor slide, kartu untuk isi, sampul dengan panel (logo, jenis dokumen, judul, keterangan, dosen, kelompok, anggota, institusi), pembatas bab bernomor, penutup "Terima Kasih" dengan "Tanya Jawab" dan foto bila ada. Tidak ada gradasi, emoji, atau clipart. Nomor halaman di slide isi bisa diklik untuk kembali ke Agenda (jika ada Agenda; objek `kembaliAgenda`). Kartu, ikon, dan elemen lain diberi nama unik per slide.

**Penamaan objek untuk Morph.** PowerPoint hanya memasangkan objek berdasarkan nama jika namanya diawali `!!`. Tanpa awalan itu, Morph menebak pasangan dari kemiripan dan bisa jatuh ke efek fade. `bangun_ppt.js` sudah memberi `objectName` persis berikut di setiap slide: `!!judul`, `!!garisJudul`, `!!ikon`, `!!orb`, `!!orbKecil`, `!!footer`. Posisi dan ukurannya berbeda antar slide (sampul, pembatas, dan penutup lebih besar), sehingga Morph menggeser dan mengubah ukurannya secara halus. Gambar, tabel, dan rumus diberi nama unik per slide tanpa awalan `!!`.
