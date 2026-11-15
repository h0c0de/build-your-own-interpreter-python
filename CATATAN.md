# CATATAN — Build 6: Interpreter dengan Python (LSBASI, dipotong)

Mengikuti Ruslan Spivak, *Let's Build A Simple Interpreter* —
https://ruslanspivak.com/lsbasi-part1/ — seri 19 bagian; build ini
mengambil Bagian 1–10 (lihat RENCANA untuk batas potongannya).
Satu halaman per irisan: konsep inti + temuan.

## Irisan 1 — Lexer + kalkulator +/− (Bagian 1–2) (15 Nov 2026, terverifikasi)

**Yang dibangun:** bentuk Bagian 1 seri ini apa adanya — satu kelas `Interpreter` yang memuat lexer (`get_next_token`) sekaligus pengenal pola (`expr`), token bertipe `INTEGER/PLUS/MINUS/EOF` — lalu perluasan Bagian 2: integer multi-digit lewat metode `integer()`, spasi dilewati, operator `MINUS`, dan rantai operasi `expr -> factor ((+|-) factor)*` yang mengonsumsi token dengan pola `eat()`.

**Bukti jalan:** `uji_irisan1.py` — semua PASS pada jalan pertama. Aliran token untuk `"3+5"` sama persis dengan sesi contoh di halaman Bagian 1 (`Token(INTEGER, 3)`, `Token(PLUS, '+')`, …); contoh hitung panduan (3+4=7, 3+5=8, 3+9=12) hijau; masukan rusak (`3+`, `a+1`, `3++5`, string kosong) meledak dengan pengecualian, bukan diam; dan **diferensial acak 1.000 ekspresi +/− multi-digit melawan `eval` Python: beda = 0**.

**Konsep inti:**
- Setiap interpreter/kompiler dimulai dari pemecahan teks menjadi *token* — pasangan (tipe, nilai). Lexer tidak tahu arti; ia hanya tahu bentuk. Pemisahan "bentuk" dari "arti" ini yang membuat tahap berikutnya mungkin.
- Di tahap ini pengenalan pola dan evaluasi masih menyatu: `expr()` memeriksa urutan token sambil langsung menghitung. Itu disengaja oleh serinya — dan justru hutang arsitektur itulah yang dilunasi refaktor AST di Bagian 7 (Irisan 3 kami), titik balik seluruh seri.

## Irisan 2 — Tata bahasa penuh (Bagian 3–5) (15 Nov 2026, terverifikasi)

**Yang dibangun:** tata bahasa berjenjang seri ini — `expr -> term ((+|-) term)*`, `term -> factor ((*|/) factor)*`, `factor -> (+|-) factor | INTEGER | ( expr )` — dengan token MUL/DIV/LPAREN/RPAREN. Tidak ada tabel presedensi dan tidak ada kode khusus: presedensi *jatuh dari bentuk tata bahasanya*, karena `expr` hanya bisa menjangkau `*` lewat `term`. Pembagian adalah pembagian nyata (float), mengikuti `/` seri ini.

**Bukti jalan:** `uji_irisan2.py` — 17 kasus kurasi presedensi/unary/kurung hijau, dan diferensial berbasis **pohon ekspresi acak yang dirender sadar-presedensi** (kurung hanya ditulis bila tata bahasa menuntutnya, jadi presedensi interpreter yang benar-benar diuji): 1.488 ekspresi valid, beda = 0 melawan nilai pohon dan `eval`. Regresi Irisan 1 hijau kembali (lihat temuan kedua).

**Temuan:**
- *Bug tertangkap uji:* jalan pertama gagal pada `3+2)` dan `2(3)` — keduanya diterima diam-diam karena titik masuk `expr()` tidak pernah memeriksa bahwa token sesudah ekspresi lengkap harus EOF. Token sisa sekarang = kesalahan. Pelajaran yang sama dengan build lain: jalan bahagia yang hijau tidak membuktikan apa-apa tentang jalan rusak.
- *Evolusi semantik yang disengaja:* `3++5` adalah kesalahan di Irisan 1, tetapi **sah (= 8)** sejak unary ada di Irisan 2 — bahasa tumbuh, uji lama disesuaikan dengan komentar yang menandai perubahan itu, bukan dihapus diam-diam.
- *Utang yang terasa:* karena evaluasi masih menyatu dengan pengenalan, `factor` untuk kurung harus memanggil varian `expr` yang tidak mengambil token awal — canggung, dan persis alasan Bagian 7 memisahkan Parser dari Interpreter (Irisan 3).

## Irisan 3 — Refaktor AST (Bagian 7) (15 Nov 2026, terverifikasi)

**Yang dibangun:** titik balik seri ini — satu kelas yang mengenal-sambil-menghitung dibongkar menjadi tiga komponen: `Lexer` (teks → token), `Parser` (token → AST berisi `BinOp`/`Num`/`UnaryOp`; tidak menghitung apa pun), dan `Interpreter(NodeVisitor)` yang menilai pohon. Canggungnya `expr_dalam` dari Irisan 2 lenyap dengan sendirinya: parser rekursif kini wajar karena ia hanya membangun simpul.

**Bukti jalan:** `uji_irisan3.py` — semua hijau. Bentuk AST diperiksa struktural (`2+3*4` → `(2+(3*4))`, `10-2-3` asosiatif kiri, unary menjadi simpul sendiri). Diferensial Irisan 2 yang *identik* (benih & pembangkit yang sama, 1.488 ekspresi) tetap beda = 0 di arsitektur baru — refaktor terbukti tidak mengubah vonis. Dan keuntungan arsitekturnya dibuktikan, bukan diklaim: pengunjung kedua, pencetak RPN, berjalan di atas pohon yang sama (`2+3*4` → `2 3 4 * +`) tanpa menyentuh parser.

**Temuan:** regresi Irisan 1 sempat merah karena uji token lama memakai API kelas gabungan; sesudah Bagian 7, `get_next_token` memang pindah ke `Lexer` — uji disesuaikan dengan penanda, pola yang sama seperti evolusi `3++5`. Pelajarannya: dalam refaktor yang setia pada sumbernya, sebagian "kegagalan regresi" adalah API yang memang direncanakan pindah rumah; yang penting perubahan vonis = nol, dan itu yang dibuktikan diferensial.

## Irisan 4 — Bahasa mini Pascal (Bagian 9–10, dibatasi) (15 Nov 2026, terverifikasi)

**Yang dibangun:** lompatan dari kalkulator ke *bahasa*: lexer belajar kata (`_id()` + kata cadangan, tidak peka huruf besar/kecil seperti Pascal), `:=` lewat `peek`, dan tata bahasa program seri ini — `PROGRAM nama; block .`, blok dengan seksi `VAR` opsional, `BEGIN ... END` yang bisa bersarang, daftar pernyataan berpisah `;`, penugasan, dan variabel sebagai simpul AST yang dibaca dari `GLOBAL_MEMORY`. Mengikuti seri ini di Bagian 10, token angka berganti nama `INTEGER_CONST` karena `INTEGER` menjadi kata kunci tipe. Deklarasi `VAR` diterima tata bahasa tetapi tidak mengalokasi — perilaku seri ini sebelum tabel simbol (Bagian 11, di luar potongan, dicatat terbuka).

**Bukti jalan:** `uji_irisan4.py` — semua hijau. Empat program kurasi (termasuk blok bersarang dengan huruf kecil semua dan pernyataan terakhir tanpa `;`, campuran unary/kurung/bagi-nyata, dan blok kosong yang sah) menghasilkan memori akhir yang persis seperti dihitung tangan; lima bentuk program rusak meledak dengan benar; dan **200 program acak berantai** — variabel yang saling dibangun satu sama lain — memori akhirnya identik dengan model Python, beda = 0. Regresi Irisan 1–3 hijau (satu penyesuaian repr token akibat ganti nama di atas, diberi penanda).

**Konsep inti penutup:** yang berubah di irisan ini bukan mesinnya, melainkan *apa yang dianggap program*. Interpreter yang sama yang kemarin menilai `2+3*4` kini mengeksekusi urutan pernyataan yang mengubah keadaan — variabel, urutan, dan efek samping. Itulah jarak sebenarnya antara kalkulator dan bahasa pemrograman, dan ia ditempuh hanya dengan menambah simpul AST serta aturan tata bahasa, tanpa mengganti Lexer/Parser/Visitor yang sudah terbukti.
