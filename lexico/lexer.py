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
        return -53


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

def token_linea(line: str, num_linea: int) -> Tuple[List[Token], List[ErrorLex]]:
    tokens: List[Token] = []
    errores: List[ErrorLex] = []
    i = 0
    N = len(line)

    mcom = comentarios.search(line)
    corte = mcom.start() if mcom else N

    while i < corte:
        msp = espacios.search(line,i)
        if msp:
            i = msp.end()
            continue

        pts = i + 1
#String
        if line[i] == '"':
            mstr = string.match(line, i)
            if not mstr:
                errores.append(ErrorLex('"', "String sin cerrar", pts, num_linea))
                break
            lex = mstr.group(0)
            tokens.append(Token(lex, -54, pts, num_linea))
            i = mstr.end()
            continue
        #Operadores y caracteres especiales
        op = emparejar_ops(line, i)
        if op:
            lex,tok,adv = op
            tokens.append(Token(lex, tok , pts , num_linea))
            i += adv
            continue

        mreal = real.match(line, i)
        if mreal:
            lex = mreal.group(0)
            tokens.append(Token(lex, -53, pts, num_linea))
            i = mreal.end()
            continue

        mint = entero.match(line, i)
        if mint:
            lex = mstr.group(0)
            tok = clasificacion_numero(lex)
            tokens.append(Token(tok, -54, pts, num_linea))
            i = mstr.end()
            continue

        for rg in (idClaMet.findall(line), idstring.findall(line)):
            mid = rg.match(line, i)
            if mid:
                lex = line[i:mid.end()]
                tokens.append(Token(lex, -54, pts, num_linea))
                i = mid.end()
                break

        else:
            mword = re.match(r"[A-za-z]+",line[i:])
            if mword:
                lex = mword.group(0)
                if lex in Tok_Preservadas:
                    tokens.append(Token(lex, -54, pts, num_linea))
                else:
                    errores.append(
                        ErrorLex(
                            lex,"Identificador invalido debe iniciar con almenos un @,$,&,% y solo letras",
                            pts,
                            num_linea,
                        )
                    )
                i += len(lex)
                continue

        ch = line[i]
        if ch == '.':
            i += 1
            continue

        errores.append(ErrorLex(ch, "Simbolo no reconocido", pts, num_linea))
        i += 1
    return tokens, errores

def scan(source: str) -> Tuple[List[Token], List[ErrorLex]]:
    all_tokens: List[Token] = []
    all_errores: List[ErrorLex] = []
    for nlinea, raw in enumerate(source.splitlines(), start=1):
        toks, errs = token_lineai(raw, nlinea)
        all_tokens.extend(toks)
        all_errores.extend(errs)
    return all_tokens, all_errores