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

# ==========================
#  MAPEO DE TOKENS DEL LÉXICO
# ==========================

# Palabras reservadas
TK_CLASE    = Tok_Preservadas["clase"]
TK_LEER     = Tok_Preservadas["leer"]
TK_SWITCH   = Tok_Preservadas["switch"]
TK_POSXY    = Tok_Preservadas["posxy"]
TK_ENTERO   = Tok_Preservadas["entero"]
TK_VAR      = Tok_Preservadas["var"]
TK_ESCRIBIR = Tok_Preservadas["escribir"]
TK_ENCASO   = Tok_Preservadas["encaso"]
TK_LIMPIAR  = Tok_Preservadas["limpiar"]
TK_REAL     = Tok_Preservadas["real"]
TK_VACIO    = Tok_Preservadas["vacio"]
TK_SI       = Tok_Preservadas["si"]
TK_REPITE   = Tok_Preservadas["repite"]
TK_EJECUTAR = Tok_Preservadas["ejecutar"]
TK_REGRESAR = Tok_Preservadas["regresar"]
TK_METODO   = Tok_Preservadas["metodo"]
TK_SINO     = Tok_Preservadas["sino"]
TK_MIENTRAS = Tok_Preservadas["mientras"]
TK_CADENA   = Tok_Preservadas["cadena"]
TK_SALIR    = Tok_Preservadas["salir"]

# Identificadores
TK_ID_CLASE = ID_TOK_BY_PREFIX['@']  # -70
TK_ID_STR   = ID_TOK_BY_PREFIX['$']  # -71
TK_ID_INT   = ID_TOK_BY_PREFIX['&']  # -72
TK_ID_REAL  = ID_TOK_BY_PREFIX['%']  # -73

# Constantes (códigos que ya usas en tu léxico)
TK_CTE_INT  = -52  # entero en rango
TK_CTE_REAL = -53  # real o entero fuera de rango
TK_CTE_STR  = -54  # string

# Operadores aritméticos (usamos el diccionario del léxico)
TK_INC     = Tok_OpAritmeticos["++"]
TK_DEC     = Tok_OpAritmeticos["--"]
TK_MASIG   = Tok_OpAritmeticos["+="]
TK_MENOSIG = Tok_OpAritmeticos["-="]
TK_ENTRIG  = Tok_OpAritmeticos["/="]
TK_PORIG   = Tok_OpAritmeticos["*="]
TK_MAS     = Tok_OpAritmeticos["+"]
TK_MENOS   = Tok_OpAritmeticos["-"]
TK_POR     = Tok_OpAritmeticos["*"]
TK_ENTRE   = Tok_OpAritmeticos["/"]
TK_MOD     = Tok_OpAritmeticos["%"]
TK_ASIG    = Tok_OpAritmeticos["="]

# Relacionales
TK_MENORIG = Tok_Relacionales["<="]
TK_DIF     = Tok_Relacionales["!="]
TK_MAYORIG = Tok_Relacionales[">="]
TK_IGUAL   = Tok_Relacionales["=="]
TK_MENOR   = Tok_Relacionales["<"]
TK_MAYOR   = Tok_Relacionales[">"]

# Lógicos
TK_AND = Tok_Logicos["&&"]
TK_OR  = Tok_Logicos["||"]
TK_NOT = Tok_Logicos["!"]

# Especiales
TK_PYC      = Tok_Especiales[";"]
TK_CORIZQ   = Tok_Especiales["["]
TK_CORDER   = Tok_Especiales["]"]
TK_CMA      = Tok_Especiales[","]
TK_DOSP     = Tok_Especiales[":"]
TK_PARIZQ   = Tok_Especiales["("]
TK_PARDER   = Tok_Especiales[")"]
TK_LLAVEIZQ = Tok_Especiales["{"]
TK_LLAVEDER = Tok_Especiales["}"]

# EOF sintáctico
TK_EOF = 0


class ParserError(Exception):
    """Error sintáctico."""
    pass


class Parser:
    def __init__(self, tokens: List[LexToken]):
        self.tokens = tokens
        self.i = 0

    @property
    def actual(self) -> LexToken:
        return self.tokens[self.i]

    def avanzar(self):
        if self.actual.token != TK_EOF:
            self.i += 1

    def coincidir(self, esperado: int, mensaje: str = None):
        if self.actual.token == esperado:
            self.avanzar()
        else:
            tok = self.actual
            msg = mensaje or f"Se esperaba token {esperado} y se encontró '{tok.lexema}'"
            raise ParserError(f"[Línea {tok.linea}] {msg}")

    def comprobar(self, tipo: int) -> bool:
        return self.actual.token == tipo

#Metodos


    def parsear(self):
        self.PROG()
        if self.actual.token != TK_EOF:
            tok = self.actual
            raise ParserError(f"[Línea {tok.linea}] Se esperaba fin de archivo y se encontró '{tok.lexema}'")

    def PROG(self):
        # PROG -> clase @id { VAR METODOS }
        self.coincidir(TK_CLASE, "Se esperaba la palabra reservada 'clase'")
        self.coincidir(TK_ID_CLASE, "Se esperaba identificador de clase (@Nombre)")
        self.coincidir(TK_LLAVEIZQ, "Se esperaba '{' después del encabezado de clase")
        self.VAR()
        self.METODOS()
        self.coincidir(TK_LLAVEDER, "Se esperaba '}' al final de la clase")

    def VAR(self):
        # VAR -> ( var TIPO listaId ; )*
        while self.comprobar(TK_VAR):
            self.coincidir(TK_VAR)
            self.listaId()
            self.coincidir(TK_PYC, "Se esperaba ';' al final de la declaración de variables")

    def METODOS(self):
        # METODOS -> ( metodo TIPO @id ( PARAM ) { VAR ESTATUTOS } )*
        while self.comprobar(TK_METODO):
            self.coincidir(TK_METODO)
            self.TIPO()
            self.coincidir(TK_ID_CLASE, "Se esperaba identificador de método (@Nombre)")
            self.coincidir(TK_PARIZQ, "Se esperaba '(' después del nombre del método")
            self.PARAM()
            self.coincidir(TK_PARDER, "Se esperaba ')' al terminar la lista de parámetros")
            self.coincidir(TK_LLAVEIZQ, "Se esperaba '{' al inicio del cuerpo del método")
            self.VAR()
            self.ESTATUTOS()
            self.coincidir(TK_LLAVEDER, "Se esperaba '}' al final del método")

    def PARAM(self):
        """
        <PARAM> -> ε | ID_ARREGLO ( , ID_ARREGLO )*
        """
        # Si NO empieza con un ID válido, entonces es ε (sin parámetros)
        if self.actual.token not in (TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL):
            return

        # Primer parámetro
        self.ID_ARREGLO()

        # , ID_ARREGLO repetido
        while self.comprobar(TK_CMA):
            self.coincidir(TK_CMA)
            self.ID_ARREGLO()

    def TIPO(self):
        # TIPO -> entero | real | cadena | vacio
        if self.comprobar(TK_ENTERO):
            self.coincidir(TK_ENTERO)
        elif self.comprobar(TK_REAL):
            self.coincidir(TK_REAL)
        elif self.comprobar(TK_CADENA):
            self.coincidir(TK_CADENA)
        elif self.comprobar(TK_VACIO):
            self.coincidir(TK_VACIO)
        else:
            tok = self.actual
            raise ParserError(f"[Línea {tok.linea}] Se esperaba un tipo (entero, real, cadena, vacio)")

    def _siguiente_es_tipo(self) -> bool:
        return self.actual.token in (TK_ENTERO, TK_REAL, TK_CADENA, TK_VACIO)

    # ---------- IDs / constantes ----------

    def ID_ARREGLO(self):
        # ID_ARREGLO -> ID ( [ índice ] )?
        if self.actual.token not in (TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL):
            tok = self.actual
            raise ParserError(f"[Línea {tok.linea}] Se esperaba un identificador")
        self.avanzar()

        if self.comprobar(TK_CORIZQ):
            self.coincidir(TK_CORIZQ)
            if self.comprobar(TK_ID_INT):
                self.coincidir(TK_ID_INT)
            elif self.comprobar(TK_CTE_INT):
                self.coincidir(TK_CTE_INT)
            else:
                tok = self.actual
                raise ParserError(f"[Línea {tok.linea}] Se esperaba índice entero para el arreglo")
            self.coincidir(TK_CORDER, "Se esperaba ']' cerrando el índice del arreglo")

    def CTE(self):
        if self.comprobar(TK_CTE_INT):
            self.coincidir(TK_CTE_INT)
        elif self.comprobar(TK_CTE_REAL):
            self.coincidir(TK_CTE_REAL)
        elif self.comprobar(TK_CTE_STR):
            self.coincidir(TK_CTE_STR)
        else:
            tok = self.actual
            raise ParserError(f"[Línea {tok.linea}] Se esperaba una constante")

    def listaId(self):
        self.ID_ARREGLO()
        while self.comprobar(TK_CMA):
            self.coincidir(TK_CMA)
            self.ID_ARREGLO()

    # ---------- Estatutos ----------

    def ESTATUTOS(self):
        while self._comienza_estatuto():
            self.ESTATUTO()

    def _comienza_estatuto(self) -> bool:
        return (
            self.actual.token in (TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL)
            or self.comprobar(TK_LEER)
            or self.comprobar(TK_ESCRIBIR)
            or self.comprobar(TK_SI)
            or self.comprobar(TK_MIENTRAS)
            or self.comprobar(TK_REPITE)
            or self.comprobar(TK_SWITCH)
            or self.comprobar(TK_EJECUTAR)
            or self.comprobar(TK_REGRESAR)
            or self.comprobar(TK_SALIR)
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
            tok = self.actual
            raise ParserError(f"[Línea {tok.linea}] Estatuto no reconocido '{tok.lexema}'")

    # ---------- Asignación / expresiones ----------
    def ASIGNA(self):
        """
        <ASIGNA> -> ID_ARREGLO = EXP_ARIT ;
        """
        # ID_ARREGLO
        self.ID_ARREGLO()

        # '=' obligatorio
        self.coincidir(TK_ASIG, "Se esperaba '=' en la asignación")

        # EXP_ARIT
        self.EXP_ARIT()

        # ';' obligatorio
        self.coincidir(TK_PYC, "Se esperaba ';' al final de la asignación")

    def EXP_ARIT(self):
        self.TERM()
        while self.actual.token in (TK_MAS, TK_MENOS, TK_MOD):
            self.avanzar()
            self.TERM()

    def TERM(self):
        self.FACTOR()
        while self.actual.token in (TK_POR, TK_ENTRE):
            self.avanzar()
            self.FACTOR()

    def FACTOR(self):
        if self.comprobar(TK_PARIZQ):
            self.coincidir(TK_PARIZQ)
            self.EXP_ARIT()
            self.coincidir(TK_PARDER, "Se esperaba ')' al cerrar la expresión")
        elif self.actual.token in (TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL):
            self.ID_ARREGLO()
        elif self.actual.token in (TK_CTE_INT, TK_CTE_REAL, TK_CTE_STR):
            self.CTE()
        else:
            tok = self.actual
            raise ParserError(f"[Línea {tok.linea}] Se esperaba un factor (id, constante o '(')")

    # ---------- leer / escribir ----------

    def LEER(self):
        self.coincidir(TK_LEER)
        self.coincidir(TK_PARIZQ)
        self.listaId()
        self.coincidir(TK_PARDER, "Se esperaba ')' en leer()")
        self.coincidir(TK_PYC, "Se esperaba ';' al final de leer")

    def ESCRIBIR(self):
        self.coincidir(TK_ESCRIBIR)
        self.coincidir(TK_PARIZQ)
        self.listaExp()
        self.coincidir(TK_PARDER, "Se esperaba ')' en escribir()")
        self.coincidir(TK_PYC, "Se esperaba ';' al final de escribir")

    def listaExp(self):
        self.EXP_ARIT()
        while self.comprobar(TK_CMA):
            self.coincidir(TK_CMA)
            self.EXP_ARIT()

    # ---------- estructuras de control ----------

    def SI(self):
        # si ( CONDICION ) { ESTATUTOS } [ sino { ESTATUTOS } ]
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

    def MIENTRAS(self):
        # mientras ( CONDICION ) { ESTATUTOS }
        self.coincidir(TK_MIENTRAS)
        self.coincidir(TK_PARIZQ)
        self.CONDICION()
        self.coincidir(TK_PARDER)
        self.coincidir(TK_LLAVEIZQ)
        self.ESTATUTOS()
        self.coincidir(TK_LLAVEDER)

    def REPETIR(self):
        # repite { ESTATUTOS } CONDICION ;
        self.coincidir(TK_REPITE)
        self.coincidir(TK_LLAVEIZQ)
        self.ESTATUTOS()
        self.coincidir(TK_LLAVEDER)
        self.CONDICION()
        self.coincidir(TK_PYC, "Se esperaba ';' al final de repite")

    def SWITCH(self):
        # switch ( EXP_ARIT ) { encaso CTE_INT : ESTATUTOS ... [ default : ESTATUTOS ] }
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

        # default opcional (si lo manejas en el PDF, aquí se puede ajustar)

        self.coincidir(TK_LLAVEDER)

    def EJECUTAR(self):
        # ejecutar @id ;
        self.coincidir(TK_EJECUTAR)
        self.coincidir(TK_ID_CLASE, "Se esperaba identificador de método después de 'ejecutar'")
        self.coincidir(TK_PYC, "Se esperaba ';' al final de ejecutar")

    def REGRESAR(self):
        # regresar [ EXP_ARIT ] ;
        self.coincidir(TK_REGRESAR)
        if self._comienza_exp():
            self.EXP_ARIT()
        self.coincidir(TK_PYC, "Se esperaba ';' al final de regresar")

    def SALIR(self):
        # salir ;
        self.coincidir(TK_SALIR)
        self.coincidir(TK_PYC, "Se esperaba ';' al final de salir")

    # ---------- condiciones ----------

    def CONDICION(self):
        # [ ! ] EXP_ARIT OP_REL EXP_ARIT { (&& ||) CONDICION }?
        if self.comprobar(TK_NOT):
            self.coincidir(TK_NOT)

        self.EXP_ARIT()
        self.OP_REL()
        self.EXP_ARIT()

        while self.actual.token in (TK_AND, TK_OR):
            self.OP_LOG()
            self.CONDICION()

    def OP_LOG(self):
        if self.comprobar(TK_AND):
            self.coincidir(TK_AND)
        elif self.comprobar(TK_OR):
            self.coincidir(TK_OR)
        else:
            tok = self.actual
            raise ParserError(f"[Línea {tok.linea}] Se esperaba operador lógico (&&, ||)")

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
            tok = self.actual
            raise ParserError(f"[Línea {tok.linea}] Se esperaba operador relacional")

    def _comienza_exp(self) -> bool:
        return self.actual.token in (
            TK_PARIZQ,
            TK_ID_CLASE, TK_ID_STR, TK_ID_INT, TK_ID_REAL,
            TK_CTE_INT, TK_CTE_REAL, TK_CTE_STR
        )
