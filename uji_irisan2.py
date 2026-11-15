# uji_irisan2.py — Bukti Irisan 2: tata bahasa penuh == eval.
# Diferensialnya berbasis POHON ekspresi acak yang dirender dengan
# aturan presedensi (kurung hanya bila perlu) — jadi yang diuji
# benar-benar presedensi interpreter kami, bukan kurung yang menolong.

import random
import sys

from spi import hitung

gagal = []


def cek(nama, kondisi, detail=''):
    print(('PASS' if kondisi else 'FAIL'), nama, detail)
    if not kondisi:
        gagal.append(nama)


# --- A: kurasi presedensi & bentuk ---
KASUS = [
    ('2+3*4', 14), ('(2+3)*4', 20), ('2*3+4*5', 26),
    ('10-2*3', 4), ('10/4', 2.5), ('7/2', 3.5), ('18/3/2', 3.0),
    ('-5+3', -2), ('--5', 5), ('-(3+2)', -5), ('2*-3', -6),
    ('1+2*3-4/2', 5.0), ('((1+2)*(3+4))', 21), (' 14 + 2 * 3 - 6 / 2 ', 17.0),
    ('5', 5), ('- 8', -8), ('2*(3+(4*5))', 46),
]
for teks, harap in KASUS:
    got = hitung(teks)
    cek(f'hitung {teks!r}', got == harap == eval(teks), f'dapat {got}')

for teks in ('2+', '(3+2', '3+2)', '2**3', '()', '2(3)', '/5'):
    try:
        hitung(teks)
        cek(f'error {teks!r}', False, 'tidak meledak')
    except Exception:
        cek(f'error {teks!r}', True)

# --- B: pohon acak, render sadar-presedensi ---
random.seed(20261115)
PRES = {'+': 1, '-': 1, '*': 2, '/': 2}


def pohon(dalam):
    if dalam == 0 or random.random() < 0.3:
        return ('num', random.randint(1, 20))
    if random.random() < 0.15:
        return ('un', random.choice('+-'), pohon(dalam - 1))
    op = random.choice('+-*/')
    return ('bin', op, pohon(dalam - 1), pohon(dalam - 1))


def nilai(p):
    if p[0] == 'num':
        return float(p[1])
    if p[0] == 'un':
        return +nilai(p[2]) if p[1] == '+' else -nilai(p[2])
    a, b = nilai(p[2]), nilai(p[3])
    return {'+': a + b, '-': a - b, '*': a * b, '/': a / b}[p[1]]


def render(p, induk=0, kanan=False):
    if p[0] == 'num':
        return str(p[1])
    if p[0] == 'un':
        s = p[1] + render(p[2], 3)
        return f'({s})' if 3 < induk else s
    pres = PRES[p[1]]
    kiri = render(p[2], pres)
    kanan_s = render(p[3], pres, kanan=True)
    if p[1] in '-/' and p[3][0] == 'bin' and PRES[p[3][1]] <= pres:
        kanan_s = f'({render(p[3])})'
    s = f'{kiri}{p[1]}{kanan_s}'
    return f'({s})' if pres < induk or (kanan and pres == induk and induk == 3) else s


beda = 0
total = 0
for _ in range(1500):
    p = pohon(3)
    try:
        harap = nilai(p)
    except ZeroDivisionError:
        continue
    teks = render(p)
    total += 1
    try:
        got = hitung(teks)
    except Exception as e:
        beda += 1
        print('  LEDAK:', teks, e)
        continue
    if abs(got - harap) > 1e-9 or abs(eval(teks) - harap) > 1e-9:
        beda += 1
        if beda <= 5:
            print('  BEDA:', teks, 'kami', got, 'eval', eval(teks), 'pohon', harap)
cek(f'diferensial pohon acak {total} ekspresi', beda == 0, f'beda={beda}')

# regresi Irisan 1
import os, subprocess
rr = subprocess.run(['python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uji_irisan1.py')],
                    capture_output=True, timeout=120)
cek('regresi uji_irisan1.py', rr.returncode == 0)

print()
if gagal:
    print('GAGAL:', ', '.join(gagal))
    sys.exit(1)
print('SEMUA PASS — Irisan 2 terbukti: presedensi dari tata bahasa, setara eval.')
