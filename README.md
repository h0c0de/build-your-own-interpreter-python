# build-your-own-interpreter-python

Membangun **interpreter** dari nol dengan Python: dari kalkulator
satu operasi sampai bahasa mini Pascal dengan program, blok, dan
variabel. Bagian dari seri
[build-your-own-x](https://github.com/codecrafters-io/build-your-own-x)
(fork: [h0c0de/build-your-own-x](https://github.com/h0c0de/build-your-own-x)).

Panduan: Ruslan Spivak, *Let's Build A Simple Interpreter* —
https://ruslanspivak.com/lsbasi-part1/

**Cakupan sengaja dipotong.** Seri aslinya 19 bagian menuju
interpreter Pascal lengkap + debugger. Build ini mengambil busur
fondasinya, Bagian 1–10: kalkulator → tata bahasa penuh → refaktor
AST → program Pascal mini. Di luar potongan (tercatat di RENCANA):
deklarasi bertipe penuh & tabel simbol, prosedur/fungsi, tumpukan
panggilan, `IF`/`FOR`, dan debugger.

## Isi

- `spi.py` — Lexer, Parser (→ AST), dan Interpreter (NodeVisitor):
  `hitung(teks)` untuk ekspresi, `jalankan(teks)` untuk program.
- `uji_irisan1.py` … `uji_irisan4.py` — bukti per irisan: diferensial
  ribuan ekspresi acak melawan `eval`, bentuk AST struktural,
  pengunjung kedua (pencetak RPN), dan 200 program acak yang memori
  akhirnya dibandingkan dengan model Python.
- `CATATAN.md` — satu halaman per irisan: konsep inti + temuan
  (termasuk bug EOF yang tertangkap uji dan ganti nama token
  `INTEGER` → `INTEGER_CONST` mengikuti Bagian 10 seri ini).
- `RENCANA.md` — rencana irisan, batas potongan & pagar selesai.

## Contoh program yang bisa dijalankan

```pascal
PROGRAM Hitung;
VAR
  a, b, c : INTEGER;
BEGIN
  a := 20;
  b := 3;
  c := a + b * 2
END.
```

Memori akhir: `{'a': 20, 'b': 3, 'c': 26}` — blok bersarang, unary,
tanda kurung, dan pembagian nyata semuanya bekerja di dalam ekspresi.

## Cara menjalankan

```sh
python3 uji_irisan1.py   # lexer + kalkulator +/-
python3 uji_irisan2.py   # tata bahasa penuh vs eval
python3 uji_irisan3.py   # refaktor AST, diferensial identik
python3 uji_irisan4.py   # program Pascal mini + regresi penuh
```

Python ≥ 3.10, pustaka standar saja.
