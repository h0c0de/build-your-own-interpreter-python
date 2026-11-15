# uji_irisan4.py — Bukti Irisan 4: program Pascal mini berjalan benar.
# Memori akhir program dibandingkan dengan hasil yang dihitung
# independen (tangan / Python), termasuk program acak berantai.

import random
import sys

from spi import jalankan

gagal = []


def cek(nama, kondisi, detail=''):
    print(('PASS' if kondisi else 'FAIL'), nama, detail)
    if not kondisi:
        gagal.append(nama)


PROG1 = """
PROGRAM Hitung;
VAR
  a, b, c : INTEGER;
BEGIN
  a := 20;
  b := 3;
  c := a + b * 2
END.
"""
mem = jalankan(PROG1)
cek('program 1 (VAR + urutan + presedensi)', mem == {'a': 20, 'b': 3, 'c': 26}, str(mem))

PROG2 = """
program Bersarang;
var x, y : integer;
begin
  x := 5;
  begin
    y := x * x;
    x := y + 1
  end;
  y := y + x
end.
"""
mem = jalankan(PROG2)
cek('program 2 (blok bersarang, huruf kecil, tanpa ; sebelum END)',
    mem == {'x': 26, 'y': 51}, str(mem))

PROG3 = """
PROGRAM Campur;
VAR
  p, q, r : INTEGER;
BEGIN
  p := 7;
  q := -p + 10;
  r := (p + q) / 2;
END.
"""
mem = jalankan(PROG3)
cek('program 3 (unary + kurung + bagi nyata)', mem == {'p': 7, 'q': 3, 'r': 5.0}, str(mem))

PROG4 = 'PROGRAM Kosong; BEGIN END.'
cek('program 4 (blok kosong sah)', jalankan(PROG4) == {})

for nama, teks in [
    ('variabel tak dikenal dibaca', 'PROGRAM X; BEGIN a := b + 1 END.'),
    ('END hilang', 'PROGRAM X; BEGIN a := 1.'),
    ('titik akhir hilang', 'PROGRAM X; BEGIN a := 1 END'),
    ('PROGRAM hilang', 'BEGIN a := 1 END.'),
    ('titik dua penugasan hilang', 'PROGRAM X; BEGIN a = 1 END.'),
]:
    try:
        jalankan(teks)
        cek(f'error: {nama}', False, 'tidak meledak')
    except Exception:
        cek(f'error: {nama}', True)

# --- program acak berantai: memori dibandingkan model Python ---
random.seed(20261115)
beda = 0
for uji in range(200):
    nama_var = ['v0', 'v1', 'v2', 'v3']
    model = {}
    baris = []
    for v in nama_var:
        if model and random.random() < 0.7:
            lain = random.choice(list(model))
            k = random.randint(1, 9)
            op = random.choice(['+', '*'])
            baris.append(f'{v} := {lain} {op} {k}')
            model[v] = model[lain] + k if op == '+' else model[lain] * k
        else:
            k = random.randint(1, 50)
            baris.append(f'{v} := {k}')
            model[v] = k
    teks = ('PROGRAM Acak;\nVAR ' + ', '.join(nama_var) + ' : INTEGER;\nBEGIN\n  '
            + ';\n  '.join(baris) + '\nEND.')
    if jalankan(teks) != model:
        beda += 1
        if beda <= 3:
            print('  BEDA:', teks, jalankan(teks), model)
cek('200 program acak berantai == model Python', beda == 0, f'beda={beda}')

# regresi 1-3
import os, subprocess
for nm in ('uji_irisan1.py', 'uji_irisan2.py', 'uji_irisan3.py'):
    rr = subprocess.run(['python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), nm)],
                        capture_output=True, timeout=300)
    cek(f'regresi {nm}', rr.returncode == 0)

print()
if gagal:
    print('GAGAL:', ', '.join(gagal))
    sys.exit(1)
print('SEMUA PASS — Irisan 4 terbukti: bahasa mini Pascal berjalan, memori akhir benar.')
