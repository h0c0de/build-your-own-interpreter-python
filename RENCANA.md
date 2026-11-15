# RENCANA — Build 6: Interpreter dengan Python (DIPOTONG)

Sumber: daftar build-your-own-x (fork h0c0de), seksi "Build your own
`Programming Language`", entri Python:

- Ruslan Spivak, *Let's Build A Simple Interpreter* (LSBASI) —
  https://ruslanspivak.com/lsbasi-part1/ — seri **19 bagian** menuju
  interpreter Pascal subset lengkap + debugger.

Dipilih Vero 15 Nov 2026 dengan cakupan DIPOTONG (pilihan sadar sejak
awal): kami ambil busur fondasinya, **Bagian 1–10**, dan berhenti di
"program Pascal mini dengan variabel". Wasit: `eval` Python untuk
irisan kalkulator; hasil program contoh yang dihitung independen
untuk irisan bahasa.

## Di dalam potongan

- Bagian 1–2: lexer/token, kalkulator + dan −, integer multi-digit, spasi.
- Bagian 3–5: × dan ÷, presedensi via tata bahasa, unary, tanda kurung.
- Bagian 7: refaktor besar — Lexer / Parser / Interpreter terpisah,
  AST + NodeVisitor (evaluasi tidak lagi menyatu dengan parsing).
- Bagian 9–10 (dibatasi): program Pascal mini — `PROGRAM`, blok
  `BEGIN ... END`, penugasan `:=`, variabel, ekspresi penuh.

## Di luar potongan (dicatat, bukan disembunyikan)

Deklarasi `VAR` bertipe & analisis semantik/tabel simbol (Bagian
11/13), prosedur & fungsi (12/14), tumpukan panggilan (15/16),
`IF`/`FOR`/`WHILE` dan contoh faktorial lengkap seri ini, serta
debugger sumber (19). Seri penuh adalah proyek berminggu-minggu;
potongan ini mengambil fondasi yang dipakai semua build bahasa.

## Irisan

- [x] Irisan 1 — selesai & terverifikasi 15 Nov 2026 (lihat CATATAN.md). Lexer + kalkulator +/− (Bagian 1–2). Uji: contoh
      panduan + diferensial acak vs `eval`.
- [x] Irisan 2 — selesai & terverifikasi 15 Nov 2026 (lihat CATATAN.md). Tata bahasa penuh (Bagian 3–5): × ÷, presedensi,
      unary, kurung. Uji: diferensial acak vs `eval` yang lebih liar.
- [x] Irisan 3 — selesai & terverifikasi 15 Nov 2026 (lihat CATATAN.md). Refaktor AST (Bagian 7): tiga komponen terpisah.
      Uji: diferensial yang sama harus tetap hijau + bentuk AST diperiksa.
- [x] Irisan 4 — selesai & terverifikasi 15 Nov 2026 (lihat CATATAN.md). Bahasa mini (Bagian 9–10 dibatasi) + final: program
      contoh multi-pernyataan terverifikasi; tutup + terbit.

## Pagar selesai

- [x] Kalkulator terbukti oleh diferensial vs `eval`; program mini
      terbukti oleh hasil yang dihitung independen.
- [x] `CATATAN.md` satu halaman per irisan: konsep inti + temuan.
- [ ] Repo GitHub publik `build-your-own-interpreter-python` terbit & terverifikasi.
