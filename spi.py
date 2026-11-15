"""spi — Simple Pascal Interpreter, mengikuti seri LSBASI Ruslan Spivak.

Irisan 1 (Bagian 1-2): lexer + kalkulator +/-, satu kelas yang
mengenal pola sambil langsung menghitung.
Irisan 2 (Bagian 3-5): tata bahasa berjenjang expr/term/factor —
presedensi jatuh dari bentuk tata bahasa.

Irisan 3 (Bagian 7): REFAKTOR BESAR seri ini. Tiga komponen terpisah:
  Lexer       teks -> aliran token (tahu bentuk, bukan arti)
  Parser      token -> AST (BinOp / Num / UnaryOp); TIDAK menghitung
  Interpreter AST -> nilai, berjalan di atas pohon via NodeVisitor
Satu pohon kini bisa dikunjungi banyak penafsir berbeda — penilai,
pencetak RPN, dan kelak penafsir program Pascal mini (Irisan 4).

Irisan 4 (Bagian 9-10, dibatasi): bahasa mini Pascal —
  program -> PROGRAM ID SEMI block DOT
  block   -> [VAR (deklarasi SEMI)+] compound
  compound-> BEGIN statement_list END; statement: compound |
             variable ASSIGN expr | kosong
Token angka berganti nama INTEGER_CONST -> INTEGER_TYPE persis
seperti seri ini di Bagian 10, karena INTEGER menjadi kata kunci
tipe. Angka tetap integer saja (REAL Bagian 10 di luar potongan);
'/' tetap pembagian nyata. Variabel hidup di GLOBAL_MEMORY;
deklarasi VAR diterima tata bahasa tetapi tidak mengalokasi —
persis perilaku seri ini sebelum tabel simbol (Bagian 11, di luar
potongan).
"""

(INTEGER_CONST, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF,
 PROGRAM, BEGIN, END, VAR, INTEGER_TYPE, ID, ASSIGN, SEMI, DOT,
 COLON, COMMA) = (
    'INTEGER_CONST', 'PLUS', 'MINUS', 'MUL', 'DIV', 'LPAREN', 'RPAREN',
    'EOF', 'PROGRAM', 'BEGIN', 'END', 'VAR', 'INTEGER_TYPE', 'ID',
    'ASSIGN', 'SEMI', 'DOT', 'COLON', 'COMMA')


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {self.value!r})'

    __repr__ = __str__


RESERVED_KEYWORDS = {
    'PROGRAM': Token(PROGRAM, 'PROGRAM'),
    'BEGIN': Token(BEGIN, 'BEGIN'),
    'END': Token(END, 'END'),
    'VAR': Token(VAR, 'VAR'),
    'INTEGER': Token(INTEGER_TYPE, 'INTEGER'),
}


# ---------------------------------------------------------------- Lexer
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def error(self):
        raise Exception('Invalid character')

    def peek(self):
        pos = self.pos + 1
        return self.text[pos] if pos < len(self.text) else None

    def _id(self):
        hasil = ''
        while self.current_char is not None and self.current_char.isalnum():
            hasil += self.current_char
            self.advance()
        token = RESERVED_KEYWORDS.get(hasil.upper())
        return token if token is not None else Token(ID, hasil)

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        hasil = ''
        while self.current_char is not None and self.current_char.isdigit():
            hasil += self.current_char
            self.advance()
        return int(hasil)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return Token(INTEGER_CONST, self.integer())
            if self.current_char.isalpha():
                return self._id()
            if self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ':=')
            if self.current_char == ':':
                self.advance()
                return Token(COLON, ':')
            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')
            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')
            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')
            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')
            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')
            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')
            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            self.error()
        return Token(EOF, None)


# ------------------------------------------------------------------ AST
class AST:
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Program(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block


class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement


class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node


class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Compound(AST):
    def __init__(self):
        self.children = []


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class NoOp(AST):
    pass


# --------------------------------------------------------------- Parser
class Parser:
    """factor -> (PLUS|MINUS) factor | INTEGER | LPAREN expr RPAREN
       term   -> factor ((MUL|DIV) factor)*
       expr   -> term ((PLUS|MINUS) term)*   — membangun AST, bukan nilai."""

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            return UnaryOp(token, self.factor())
        if token.type == MINUS:
            self.eat(MINUS)
            return UnaryOp(token, self.factor())
        if token.type == INTEGER_CONST:
            self.eat(INTEGER_CONST)
            return Num(token)
        if token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        if token.type == ID:
            return self.variable()
        self.error()

    def term(self):
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def parse(self):
        node = self.expr()
        if self.current_token.type != EOF:
            self.error()  # token sisa = masukan rusak (pelajaran Irisan 2)
        return node

    # ---------------- tata bahasa program (Bagian 9-10) ----------------
    def program(self):
        """program -> PROGRAM ID SEMI block DOT"""
        self.eat(PROGRAM)
        prog_name = self.current_token.value
        self.eat(ID)
        self.eat(SEMI)
        block = self.block()
        self.eat(DOT)
        return Program(prog_name, block)

    def block(self):
        """block -> declarations compound_statement"""
        return Block(self.declarations(), self.compound_statement())

    def declarations(self):
        """declarations -> VAR (variable_declaration SEMI)+ | kosong"""
        hasil = []
        if self.current_token.type == VAR:
            self.eat(VAR)
            while self.current_token.type == ID:
                hasil.extend(self.variable_declaration())
                self.eat(SEMI)
        return hasil

    def variable_declaration(self):
        """variable_declaration -> ID (COMMA ID)* COLON type_spec"""
        var_nodes = [Var(self.current_token)]
        self.eat(ID)
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(ID)
        self.eat(COLON)
        type_node = self.type_spec()
        return [VarDecl(v, type_node) for v in var_nodes]

    def type_spec(self):
        """type_spec -> INTEGER (tipe lain di luar potongan)"""
        token = self.current_token
        self.eat(INTEGER_TYPE)
        return Type(token)

    def compound_statement(self):
        """compound_statement -> BEGIN statement_list END"""
        self.eat(BEGIN)
        nodes = self.statement_list()
        self.eat(END)
        root = Compound()
        root.children = nodes
        return root

    def statement_list(self):
        """statement_list -> statement (SEMI statement)*"""
        hasil = [self.statement()]
        while self.current_token.type == SEMI:
            self.eat(SEMI)
            hasil.append(self.statement())
        if self.current_token.type == ID:
            self.error()
        return hasil

    def statement(self):
        """statement -> compound_statement | assignment_statement | kosong"""
        if self.current_token.type == BEGIN:
            return self.compound_statement()
        if self.current_token.type == ID:
            return self.assignment_statement()
        return NoOp()

    def assignment_statement(self):
        """assignment_statement -> variable ASSIGN expr"""
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        return Assign(left, token, right)

    def variable(self):
        """variable -> ID"""
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def parse_program(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()
        return node


# ---------------------------------------------------------- Interpreter
class NodeVisitor:
    def visit(self, node):
        method = getattr(self, 'visit_' + type(node).__name__, None)
        if method is None:
            raise Exception(f'No visit_{type(node).__name__} method')
        return method(node)


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.GLOBAL_MEMORY = {}

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for decl in node.declarations:
            self.visit(decl)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        pass  # deklarasi tidak mengalokasi sebelum tabel simbol (Bagian 11)

    def visit_Type(self, node):
        pass

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        self.GLOBAL_MEMORY[node.left.value] = self.visit(node.right)

    def visit_Var(self, node):
        val = self.GLOBAL_MEMORY.get(node.value)
        if val is None:
            raise Exception(f'Variabel tak dikenal: {node.value}')
        return val

    def visit_NoOp(self, node):
        pass

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        if node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        if node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        if node.op.type == DIV:
            return self.visit(node.left) / self.visit(node.right)
        raise Exception(f'Operator tak dikenal: {node.op.type}')

    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        if node.op.type == PLUS:
            return +self.visit(node.expr)
        if node.op.type == MINUS:
            return -self.visit(node.expr)
        raise Exception(f'Operator unary tak dikenal: {node.op.type}')

    def interpret(self):
        return self.visit(self.parser.parse())

    def interpret_program(self):
        self.visit(self.parser.parse_program())
        return self.GLOBAL_MEMORY


def hitung(text):
    return Interpreter(Parser(Lexer(text))).interpret()


def jalankan(text):
    """Jalankan program Pascal mini; kembalikan memori global akhirnya."""
    return Interpreter(Parser(Lexer(text))).interpret_program()
