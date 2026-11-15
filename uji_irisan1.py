# uji_irisan1.py — Bukti Irisan 1: lexer benar, kalkulator +/- == eval.
# A: token persis seperti sesi contoh Bagian 1. B: contoh panduan.
# C: diferensial acak melawan eval Python.

import random
import sys

# INTEGER berganti nama INTEGER_CONST di Irisan 4 — persis penggantian
# nama Bagian 10 seri ini, karena INTEGER menjadi kata kunci tipe.
from spi import EOF, INTEGER_CONST as INTEGER, PLUS, Lexer, Token, hitung

gagal = []


def cek(nama, kondisi, detail=''):
    print(('PASS' if kondisi else 'FAIL'), nama, detail)
    if not kondisi:
        gagal.append(nama)


# --- A: aliran token Bagian 1, apa adanya ---
# (Sejak refaktor AST Irisan 3, get_next_token tinggal di kelas Lexer —
#  persis pemindahan yang dilakukan Bagian 7 seri ini.)
lx = Lexer('3+5')
toks = [lx.get_next_token() for _ in range(4)]
cek('token "3+5" persis contoh panduan',
    [(t.type, t.value) for t in toks] ==
    [(INTEGER, 3), (PLUS, '+'), (INTEGER, 5), (EOF, None)],
    str(toks))
cek('repr Token sesuai panduan', str(Token(INTEGER, 3)) == 'Token(INTEGER_CONST, 3)')

# --- B: contoh & perluasan Bagian 2 ---
for teks, harap in [('3+4', 7), ('3+5', 8), ('3+9', 12),
                     ('12+24', 36), ('  7 - 3 ', 4), ('100-1-1', 98),
                     ('5', 5), ('1+2+3+4', 10), ('20-5+3', 18)]:
    got = hitung(teks)
    cek(f'hitung {teks!r}', got == harap == eval(teks), f'dapat {got}')

# kesalahan harus meledak, bukan diam
# ('3++5' dulu error di Irisan 1; sejak unary Irisan 2 ia SAH = 8 —
#  evolusi bahasa yang disengaja, dicatat di CATATAN Irisan 2.)
for teks in ('3+', 'a+1', '3+*5', ''):
    try:
        hitung(teks)
        cek(f'error {teks!r}', False, 'tidak meledak')
    except Exception:
        cek(f'error {teks!r}', True)

# --- C: diferensial acak vs eval ---
random.seed(20261115)
beda = 0
for _ in range(1000):
    suku = [str(random.randint(0, 999)) for _ in range(random.randint(1, 6))]
    teks = suku[0]
    for s in suku[1:]:
        teks += random.choice(['+', '-']) + random.choice(['', ' ']) + s
    if hitung(teks) != eval(teks):
        beda += 1
        if beda <= 5:
            print('  BEDA:', repr(teks))
cek('diferensial acak 1000 ekspresi +/-', beda == 0, f'beda={beda}')

print()
if gagal:
    print('GAGAL:', ', '.join(gagal))
    sys.exit(1)
print('SEMUA PASS — Irisan 1 terbukti: lexer & kalkulator +/- setara eval.')
