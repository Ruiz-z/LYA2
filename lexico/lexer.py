import re
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Token:
    lexema: str
    token: int
    pts: int
    linea: int

@dataclass
class ErrorLex:
    lexema: str
    descripcion: str
    pts: int
    linea: int


# Palabras reservadas (corrijo "siwtch" -> "switch"; si lo quieres con error, deja como estaba)
Preservadas = [
    "clase","leer","switch","posxy","entero","var","escribir","encaso","limpiar","real",
    "vacio","si","repite","ejecutar","regresar","metodo","sino","mientras","cadena","salir"
]
Tok_Preservadas = {lex: -(i+1) for i, lex in enumerate(Preservadas)}

# Operadores aritméticos
OpAritmeticosdob = ["++", "--", "+=", "-=", "/=", "*="]
OpAritmeticosimple = ["+", "-", "*", "/", "%", "="]
Tok_OpAritmeticos = {op: -(21 + i) for i, op in enumerate(OpAritmeticosdob + OpAritmeticosimple)}

# Operadores relacionales (ASCII puro)
OpRelacionales = ["<=","!=",">=","==","<",">"]
Tok_Relacionales = {op: -(33+i) for i, op in enumerate(OpRelacionales)}

# Operadores lógicos
OpLogicos = ["&&","||","!"]
Tok_log = {op: -(41+i) for i, op in enumerate(OpLogicos)}

# Caracteres especiales
OpEspeciales = [";","[","]",",",":","(",")","{","}"]
Tok_Especiales = {ch: -(61+i) for i, ch in enumerate(OpEspeciales)}

espacios = re.compile(r"[ \t]+")
comentarios = re.compile(r"//.*$")
string = re.compile(r"\"(?:[^\"\n]|\\\")*\"")

real = re.compile(r"-?(?:\d+\.\d+|\.\d+)")   # opcional: acepta .5 o 0.5
entero = re.compile(r"-?\d+")

# identificadores
idClaMet = re.compile(r"@[A-Za-z]{1,7}")
idstring = re.compile(r"\$[A-Za-z]{1,7}")
identero = re.compile(r"&[A-Za-z]{1,7}")
idreal = re.compile(r"%[A-Za-z]{1,7}")


entero_min, entero_max = -32768, 32767

def clasificacion_numero(lex: str) -> int:
    try:
        val = int(lex)
        if entero_min <= val <= entero_max:
            return -52
        else:
            return -53
    except ValueError:
        return -53   # <- antes tenías -54 (string), esto era un bug


def emparejar_ops(text: str, i: int) -> Optional[Tuple[str, int, int]]:

    n = len(text)
    if i >= n:
        return None

    # 1) Aritméticos dobles
    for op in OpAritmeticosdob:
        if text.startswith(op, i):
            return (op, Tok_OpAritmeticos[op], len(op))

    # 2) Relacionales dobles
    for op in ["<=", "!=", ">=", "=="]:
        if text.startswith(op, i):
            return (op, Tok_Relacionales[op], len(op))

    # 3) Lógicos dobles
    for op in ["&&", "||"]:
        if text.startswith(op, i):
            return (op, Tok_log[op], len(op))

    # 4) Aritméticos simples
    ch = text[i]
    if ch in Tok_OpAritmeticos:      # + - * / % =
        return (ch, Tok_OpAritmeticos[ch], 1)

    # 5) Relacionales simples
    if ch in Tok_Relacionales:       # < >
        return (ch, Tok_Relacionales[ch], 1)

    # 6) Lógicos simples
    if ch in Tok_log:                # !
        return (ch, Tok_log[ch], 1)

    # 7) Especiales
    if ch in Tok_Especiales:         # ; [ ] , : ( ) { }
        return (ch, Tok_Especiales[ch], 1)

    return None


