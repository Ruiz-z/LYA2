# sintaxis/parser.py

from dataclasses import dataclass
from typing import List
from lexico.lexer import (
    Token as LexToken,
    Tok_Preservadas,
    Tok_OpAritmeticos,
    Tok_Relacionales,
    Tok_Logicos,
    Tok_Especiales,
    ID_TOK_BY_PREFIX,
)

NOMBRES_TOKENS = {}


def registrar(diccionario, nombre_base):
    for lexema, tok in diccionario.items():
        NOMBRES_TOKENS[tok] = f"{nombre_base} '{lexema}'"


# Reservadas
registrar(Tok_Preservadas, "palabra reservada")

# Operadores
registrar(Tok_OpAritmeticos, "operador aritmético")
registrar(Tok_Relacionales, "operador relacional")
registrar(Tok_Logicos, "operador lógico")

# Especiales
registrar(Tok_Especiales, "símbolo")

# Identificadores
NOMBRES_TOKENS[ID_TOK_BY_PREFIX['@']] = "identificador @clase"
NOMBRES_TOKENS[ID_TOK_BY_PREFIX['$']] = "identificador $cadena"
NOMBRES_TOKENS[ID_TOK_BY_PREFIX['&']] = "identificador &entero"
NOMBRES_TOKENS[ID_TOK_BY_PREFIX['%']] = "identificador %real"

# Constantes
NOMBRES_TOKENS[-52] = "constante entera"
NOMBRES_TOKENS[-53] = "constante real"
NOMBRES_TOKENS[-54] = "constante cadena"

# EOF
NOMBRES_TOKENS[0] = "EOF"

# ==========================
# TOKENS DEL LÉXICO
# ==========================

# Reservadas
TK_CLASE = Tok_Preservadas["clase"]
TK_LEER = Tok_Preservadas["leer"]
TK_SWITCH = Tok_Preservadas["switch"]
TK_ENTERO = Tok_Preservadas["entero"]
TK_VAR = Tok_Preservadas["var"]
TK_ESCRIBIR = Tok_Preservadas["escribir"]
TK_ENCASO = Tok_Preservadas["encaso"]
TK_REAL = Tok_Preservadas["real"]
TK_VACIO = Tok_Preservadas["vacio"]
TK_SI = Tok_Preservadas["si"]
TK_SINO = Tok_Preservadas["sino"]
TK_MIENTRAS = Tok_Preservadas["mientras"]
TK_REPITE = Tok_Preservadas["repite"]
TK_EJECUTAR = Tok_Preservadas["ejecutar"]
TK_REGRESAR = Tok_Preservadas["regresar"]
TK_METODO = Tok_Preservadas["metodo"]
TK_SALIR = Tok_Preservadas["salir"]
TK_CADENA = Tok_Preservadas["cadena"]

# Identificadores
TK_ID_CLASE = ID_TOK_BY_PREFIX['@']
TK_ID_STR = ID_TOK_BY_PREFIX['$']
TK_ID_INT = ID_TOK_BY_PREFIX['&']
TK_ID_REAL = ID_TOK_BY_PREFIX['%']

# Constantes
TK_CTE_INT = -52
TK_CTE_REAL = -53
TK_CTE_STR = -54

# Operadores aritméticos
TK_INC = Tok_OpAritmeticos["++"]
TK_DEC = Tok_OpAritmeticos["--"]
TK_MASIG = Tok_OpAritmeticos["+="]
TK_MENOSIG = Tok_OpAritmeticos["-="]
TK_PORIG = Tok_OpAritmeticos["*="]
TK_ENTRIG = Tok_OpAritmeticos["/="]
TK_MAS = Tok_OpAritmeticos["+"]
TK_MENOS = Tok_OpAritmeticos["-"]
TK_POR = Tok_OpAritmeticos["*"]
TK_ENTRE = Tok_OpAritmeticos["/"]
TK_MOD = Tok_OpAritmeticos["%"]
TK_ASIG = Tok_OpAritmeticos["="]

# Relacionales
TK_MENORIG = Tok_Relacionales["<="]
TK_MAYORIG = Tok_Relacionales[">="]
TK_IGUAL = Tok_Relacionales["=="]
TK_DIF = Tok_Relacionales["!="]
TK_MENOR = Tok_Relacionales["<"]
TK_MAYOR = Tok_Relacionales[">"]

# Lógicos
TK_AND = Tok_Logicos["&&"]
TK_OR = Tok_Logicos["||"]
TK_NOT = Tok_Logicos["!"]

# Especiales
TK_PYC = Tok_Especiales[";"]
TK_CORIZQ = Tok_Especiales["["]
TK_CORDER = Tok_Especiales["]"]
TK_CMA = Tok_Especiales[","]
TK_DOSP = Tok_Especiales[":"]
TK_PARIZQ = Tok_Especiales["("]
TK_PARDER = Tok_Especiales[")"]
TK_LLAVEIZQ = Tok_Especiales["{"]
TK_LLAVEDER = Tok_Especiales["}"]

TK_EOF = 0


# ERRORES


class ParserError(Exception):
    pass


# PARSER


class Parser:

    def __init__(self, tokens: List[LexToken]):
        self.tokens = tokens
        self.i = 0

    @property
    def actual(self):
        return self.tokens[self.i]

    def avanzar(self):
        if self.actual.token != TK_EOF:
            self.i += 1


    def coincidir(self, esperado, msg=None):
        if self.actual.token == esperado:
            self.avanzar()
        else:
            tok = self.actual
            nombre_esperado = NOMBRES_TOKENS.get(esperado, f"token {esperado}")
            llego = "EOF" if tok.token == TK_EOF else tok.lexema
            mensaje = msg or f"Se esperaba {nombre_esperado}, llegó {llego}"
            raise ParserError(f"[Línea {tok.linea}] {mensaje}")

    def comprobar(self, t):
        return self.actual.token == t

    def parsear(self):
        self.PROG()
        if self.actual.token != TK_EOF:
            raise ParserError(f"[Línea {self.actual.linea}] Se esperaba EOF")

    def PROG(self):
        self.coincidir(TK_CLASE)
        self.coincidir(TK_ID_CLASE)
        self.coincidir(TK_LLAVEIZQ)
        self.VAR()
        self.METODOS()
        self.coincidir(TK_LLAVEDER)

    # VARIABLES
    def VAR(self):
        while self.comprobar(TK_VAR):
            self.coincidir(TK_VAR)
            self.listaId()
            self.coincidir(TK_PYC)

    # MÉTODOS
    def METODOS(self):
        while self.comprobar(TK_METODO):
            self.coincidir(TK_METODO)
            self.TIPO()
            self.coincidir(TK_ID_CLASE)
            self.coincidir(TK_PARIZQ)
            self.PARAM()
            self.coincidir(TK_PARDER)
            self.coincidir(TK_LLAVEIZQ)
            self.VAR()
            self.ESTATUTOS()
            self.coincidir(TK_LLAVEDER)

    def PARAM(self):
        if self.actual.token not in (TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL):
            return
        self.ID_ARREGLO()
        while self.comprobar(TK_CMA):
            self.coincidir(TK_CMA)
            self.ID_ARREGLO()

    def TIPO(self):
        if self.comprobar(TK_ENTERO):
            self.coincidir(TK_ENTERO)
        elif self.comprobar(TK_REAL):
            self.coincidir(TK_REAL)
        elif self.comprobar(TK_CADENA):
            self.coincidir(TK_CADENA)
        elif self.comprobar(TK_VACIO):
            self.coincidir(TK_VACIO)
        else:
            raise ParserError(f"[Línea {self.actual.linea}] Tipo inválido")

    # IDENTIFICADORES
    def listaId(self):
        self.ID_ARREGLO()
        while self.comprobar(TK_CMA):
            self.coincidir(TK_CMA)
            self.ID_ARREGLO()

    def ID_ARREGLO(self):
        if self.actual.token not in (TK_ID_CLASE, TK_ID_INT, TK_ID_REAL, TK_ID_STR):
            raise ParserError(f"[Línea {self.actual.linea}] Se esperaba ID")

        self.avanzar()

        if self.comprobar(TK_CORIZQ):
            self.coincidir(TK_CORIZQ)
            if self.comprobar(TK_ID_INT):
                self.coincidir(TK_ID_INT)
            elif self.comprobar(TK_CTE_INT):
                self.coincidir(TK_CTE_INT)
            else:
                raise ParserError(f"[Línea {self.actual.linea}] Índice inválido")
            self.coincidir(TK_CORDER)

    def CTE(self):
        if self.comprobar(TK_CTE_INT):
            self.coincidir(TK_CTE_INT)
        elif self.comprobar(TK_CTE_REAL):
            self.coincidir(TK_CTE_REAL)
        elif self.comprobar(TK_CTE_STR):
            self.coincidir(TK_CTE_STR)
        else:
            raise ParserError(f"[Línea {self.actual.linea}] Constante inválida")

    # ESTATUTOS
    def ESTATUTOS(self):
        while self._comienza_estatuto():
            self.ESTATUTO()

    def _comienza_estatuto(self):
        return self.actual.token in (
            TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL,
            TK_LEER, TK_ESCRIBIR, TK_SI, TK_SINO,
            TK_MIENTRAS, TK_REPITE,
            TK_SWITCH, TK_EJECUTAR, TK_REGRESAR, TK_SALIR
        )

    def ESTATUTO(self):
        if self.actual.token in (TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL):
            self.ASIGNA()
        elif self.comprobar(TK_LEER):
            self.LEER()
        elif self.comprobar(TK_ESCRIBIR):
            self.ESCRIBIR()
        elif self.comprobar(TK_SI):
            self.SI()
        elif self.comprobar(TK_MIENTRAS):
            self.MIENTRAS()
        elif self.comprobar(TK_REPITE):
            self.REPETIR()
        elif self.comprobar(TK_SWITCH):
            self.SWITCH()
        elif self.comprobar(TK_EJECUTAR):
            self.EJECUTAR()
        elif self.comprobar(TK_REGRESAR):
            self.REGRESAR()
        elif self.comprobar(TK_SALIR):
            self.SALIR()
        else:
            raise ParserError(f"[Línea {self.actual.linea}] Estatuto inválido")

    # ASIGNACIONES
    def ASIGNA(self):

        self.ID_ARREGLO()

        if self.actual.token in (TK_MASIG, TK_MENOSIG, TK_PORIG, TK_ENTRIG):
            self.avanzar()
            self.EXP_ARIT()
            self.coincidir(TK_PYC)
            return

        if self.actual.token in (TK_INC, TK_DEC):
            self.avanzar()
            self.coincidir(TK_PYC)
            return

        self.coincidir(TK_ASIG)
        self.EXP_ARIT()
        self.coincidir(TK_PYC)

    # ==========================
    # EXPRESIONES ARITMÉTICAS
    # ==========================
    def EXP_ARIT(self):
        # TERM ( (+|-|%) TERM )*
        self.TERM()
        while self.actual.token in (TK_MAS, TK_MENOS, TK_MOD):
            self.avanzar()
            self.TERM()

        # 🔥 CHEQUEO ESPECIAL:
        # Si después de terminar la expresión viene algo que parece
        # OTRO operando (ID, constante, o '('), entonces faltó un operador.
        if self.actual.token in (
                TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL,
                TK_CTE_INT, TK_CTE_REAL, TK_CTE_STR,
                TK_PARIZQ
        ):
            tok = self.actual
            raise ParserError(
                f"[Línea {tok.linea}] Se esperaba operador aritmético , llegó {tok.lexema}"
            )

    def TERM(self):
        self.FACTOR()
        while self.actual.token in (TK_POR, TK_ENTRE):
            self.avanzar()
            self.FACTOR()

    def FACTOR(self):
        if self.comprobar(TK_PARIZQ):
            self.coincidir(TK_PARIZQ)
            self.EXP_ARIT()
            self.coincidir(TK_PARDER)
            return

        if self.comprobar(TK_ID_CLASE):
            self.coincidir(TK_ID_CLASE)
            self.coincidir(TK_PARIZQ)
            if self._comienza_exp():
                self.EXP_ARIT()
            self.coincidir(TK_PARDER)
            return

        if self.actual.token in (TK_ID_INT, TK_ID_REAL, TK_ID_STR):
            self.ID_ARREGLO()
            return

        if self.actual.token in (TK_CTE_INT, TK_CTE_REAL, TK_CTE_STR):
            self.CTE()
            return

        raise ParserError(f"[Línea {self.actual.linea}] Factor inválido")

    def _comienza_exp(self):
        return self.actual.token in (
            TK_PARIZQ,
            TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL,
            TK_CTE_INT, TK_CTE_REAL, TK_CTE_STR
        )

    # CONDICIONES
    def CONDICION(self):
        if self.comprobar(TK_NOT): self.coincidir(TK_NOT)

        self.EXP_ARIT()
        self.OP_REL()
        self.EXP_ARIT()

        while self.actual.token in (TK_AND, TK_OR):
            self.OP_LOG()
            self.CONDICION()

    def OP_REL(self):
        if self.comprobar(TK_MENOR):
            self.coincidir(TK_MENOR)
        elif self.comprobar(TK_MENORIG):
            self.coincidir(TK_MENORIG)
        elif self.comprobar(TK_MAYOR):
            self.coincidir(TK_MAYOR)
        elif self.comprobar(TK_MAYORIG):
            self.coincidir(TK_MAYORIG)
        elif self.comprobar(TK_IGUAL):
            self.coincidir(TK_IGUAL)
        elif self.comprobar(TK_DIF):
            self.coincidir(TK_DIF)
        else:
            raise ParserError(f"[Línea {self.actual.linea}] Operador relacional inválido")

    def OP_LOG(self):
        if self.comprobar(TK_AND):
            self.coincidir(TK_AND)
        elif self.comprobar(TK_OR):
            self.coincidir(TK_OR)
        else:
            raise ParserError(f"[Línea {self.actual.linea}] Operador lógico inválido")

    # LEER
    def LEER(self):
        self.coincidir(TK_LEER)
        self.coincidir(TK_PARIZQ)
        self.listaId()
        self.coincidir(TK_PARDER)
        self.coincidir(TK_PYC)

    # ESCRIBIR
    def ESCRIBIR(self):
        self.coincidir(TK_ESCRIBIR)
        self.coincidir(TK_PARIZQ)
        self._elem_escribir()
        while self.comprobar(TK_CMA):
            self.coincidir(TK_CMA)
            self._elem_escribir()
        self.coincidir(TK_PARDER)
        self.coincidir(TK_PYC)

    def _elem_escribir(self):
        if self.actual.token in (TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL):
            self.ID_ARREGLO()
        elif self.actual.token in (TK_CTE_INT, TK_CTE_STR, TK_CTE_REAL):
            self.CTE()
        else:
            raise ParserError(f"[Línea {self.actual.linea}] Error en escribir")

    # SI
    def SI(self):
        self.coincidir(TK_SI)
        self.coincidir(TK_PARIZQ)
        self.CONDICION()
        self.coincidir(TK_PARDER)
        self.coincidir(TK_LLAVEIZQ)
        self.ESTATUTOS()
        self.coincidir(TK_LLAVEDER)

        if self.comprobar(TK_SINO):
            self.coincidir(TK_SINO)
            self.coincidir(TK_LLAVEIZQ)
            self.ESTATUTOS()
            self.coincidir(TK_LLAVEDER)

    # MIENTRAS
    def MIENTRAS(self):
        self.coincidir(TK_MIENTRAS)
        self.coincidir(TK_PARIZQ)
        self.CONDICION()
        self.coincidir(TK_PARDER)
        self.coincidir(TK_LLAVEIZQ)
        self.ESTATUTOS()
        self.coincidir(TK_LLAVEDER)

    # REPETIR
    def REPETIR(self):
        self.coincidir(TK_REPITE)
        self.coincidir(TK_LLAVEIZQ)
        self.ESTATUTOS()
        self.coincidir(TK_LLAVEDER)
        self.coincidir(TK_MIENTRAS)
        self.coincidir(TK_PARIZQ)
        self.CONDICION()
        self.coincidir(TK_PARDER)
        self.coincidir(TK_PYC)

    # SWITCH
    def SWITCH(self):
        self.coincidir(TK_SWITCH)
        self.coincidir(TK_PARIZQ)
        self.EXP_ARIT()
        self.coincidir(TK_PARDER)
        self.coincidir(TK_LLAVEIZQ)

        while self.comprobar(TK_ENCASO):
            self.coincidir(TK_ENCASO)
            self.coincidir(TK_CTE_INT)
            self.coincidir(TK_DOSP)
            self.ESTATUTOS()

        self.coincidir(TK_LLAVEDER)

    # EJECUTAR
    def EJECUTAR(self):
        self.coincidir(TK_EJECUTAR)
        self.ID_ARREGLO()
        self.coincidir(TK_ASIG)
        self.coincidir(TK_ID_CLASE)
        self.coincidir(TK_PARIZQ)
        self.coincidir(TK_PARDER)
        self.coincidir(TK_PYC)

    # REGRESAR
    def REGRESAR(self):
        self.coincidir(TK_REGRESAR)
        self.coincidir(TK_PARIZQ)
        if self._comienza_exp():
            self.EXP_ARIT()
        self.coincidir(TK_PARDER)
        self.coincidir(TK_PYC)

    # SALIR
    def SALIR(self):
        self.coincidir(TK_SALIR)
        self.coincidir(TK_PYC)