# uji_irisan3.py — Bukti Irisan 3: refaktor AST tidak mengubah vonis.
# A: bentuk AST persis seperti yang dijanjikan tata bahasa.
# B: diferensial pohon acak yang IDENTIK dengan Irisan 2 (benih sama)
#    harus tetap hijau di arsitektur baru.
# C: satu pohon, dua penafsir — penilai & pencetak RPN (NodeVisitor lain).
# D: regresi Irisan 1-2.

import random
import sys

from spi import (BinOp, Interpreter, Lexer, NodeVisitor, Num, Parser,
                 UnaryOp, hitung)

gagal = []


def cek(nama, kondisi, detail=''):
    print(('PASS' if kondisi else 'FAIL'), nama, detail)
    if not kondisi:
        gagal.append(nama)


def bentuk(node):
    if isinstance(node, Num):
        return str(node.value)
    if isinstance(node, UnaryOp):
        return f"({node.op.value}{bentuk(node.expr)})"
    if isinstance(node, BinOp):
        return f"({bentuk(node.left)}{node.op.value}{bentuk(node.right)})"
    raise TypeError(node)


# --- A: bentuk AST ---
for teks, harap in [('2+3*4', '(2+(3*4))'),
                     ('(2+3)*4', '((2+3)*4)'),
                     ('10-2-3', '((10-2)-3)'),
                     ('-5', '(-5)'),
                     ('2*-3', '(2*(-3))'),
                     ('18/3/2', '((18/3)/2)')]:
    pohon = Parser(Lexer(teks)).parse()
    cek(f'AST {teks!r}', bentuk(pohon) == harap, bentuk(pohon))

# --- B: diferensial identik Irisan 2 ---
random.seed(20261115)
PRES = {'+': 1, '-': 1, '*': 2, '/': 2}


def pohon_acak(dalam):
    if dalam == 0 or random.random() < 0.3:
        return ('num', random.randint(1, 20))
    if random.random() < 0.15:
        return ('un', random.choice('+-'), pohon_acak(dalam - 1))
    op = random.choice('+-*/')
    return ('bin', op, pohon_acak(dalam - 1), pohon_acak(dalam - 1))


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


beda = total = 0
for _ in range(1500):
    p = pohon_acak(3)
    try:
        harap = nilai(p)
    except ZeroDivisionError:
        continue
    teks = render(p)
    total += 1
    if abs(hitung(teks) - harap) > 1e-9:
        beda += 1
        if beda <= 5:
            print('  BEDA:', teks)
cek(f'diferensial identik Irisan 2 di arsitektur AST ({total} ekspresi)',
    beda == 0 and total == 1488, f'beda={beda} total={total}')


# --- C: pengunjung kedua — pencetak RPN atas pohon yang sama ---
class PencetakRPN(NodeVisitor):
    def visit_BinOp(self, node):
        return f'{self.visit(node.left)} {self.visit(node.right)} {node.op.value}'

    def visit_Num(self, node):
        return str(node.value)

    def visit_UnaryOp(self, node):
        return f'{self.visit(node.expr)} {node.op.value}1'


for teks, rpn in [('2+3*4', '2 3 4 * +'), ('(2+3)*4', '2 3 + 4 *'),
                  ('-5+3', '5 -1 3 +')]:
    pohon = Parser(Lexer(teks)).parse()
    cek(f'RPN {teks!r}', PencetakRPN().visit(pohon) == rpn,
        PencetakRPN().visit(pohon))
    cek(f'nilai tetap {teks!r}', Interpreter(Parser(Lexer(teks))).interpret() == eval(teks))

# --- D: regresi ---
import os, subprocess
for nm in ('uji_irisan1.py', 'uji_irisan2.py'):
    rr = subprocess.run(['python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), nm)],
                        capture_output=True, timeout=180)
    cek(f'regresi {nm}', rr.returncode == 0)

print()
if gagal:
    print('GAGAL:', ', '.join(gagal))
    sys.exit(1)
print('SEMUA PASS — Irisan 3 terbukti: refaktor AST, vonis tak berubah, pohon bisa dipakai ulang.')
