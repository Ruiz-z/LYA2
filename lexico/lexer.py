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

# Palabras reservadas
Preservadas = [
    "clase","leer","switch","posxy","entero","var","escribir","encaso","limpiar","real",
    "vacio","si","repite","ejecutar","regresar","metodo","sino","mientras","cadena","salir"
]
Tok_Preservadas = {lex: -(i+1) for i, lex in enumerate(Preservadas)}

# Operadores
OpAritmeticos = ["++","--","+=","-=","/=","*=","+","-","*","/","%","="]
Tok_OpAritmeticos = {op: -(21 + i) for i, op in enumerate(OpAritmeticos)}

OpRelacionales = ["<=","!=",">=","==","<",">"]
Tok_Relacionales = {op: -(33+i) for i, op in enumerate(OpRelacionales)}

OpLogicos = ["&&","||","!"]
Tok_Logicos = {op: -(41+i) for i, op in enumerate(OpLogicos)}

OpEspeciales = [";","[","]",",",":","(",")","{","}"]
Tok_Especiales = {ch: -(61+i) for i, ch in enumerate(OpEspeciales)}

# Regex
espacios = re.compile(r"[ \t]+")
comentarios = re.compile(r"//.*$")
string = re.compile(r"\"(?:[^\"\n]|\\\")*\"")

# Números
real = re.compile(r"-?(?:\d+\.\d+|\.\d+)")
entero = re.compile(r"-?\d+")
invalid_real_final = re.compile(r"-?\d+\.(?!\d)")  # ej: 5. o -5.

# Identificadores
idClaMet = re.compile(r"@[A-Za-z]{1,7}")
idstring = re.compile(r"\$[A-Za-z]{1,7}")
identero = re.compile(r"&[A-Za-z]{1,7}")
idreal  = re.compile(r"%[A-Za-z]{1,7}")

entero_min, entero_max = -32768, 32767

def clasificacion_numero(lex: str) -> int:
    try:
        val = int(lex)
        return -52 if entero_min <= val <= entero_max else -53
    except ValueError:
        return -53

def _pts_token(token_code: int) -> int:
    return -2 if token_code == -51 else -1

def _pts_error_lexeme(lex: str) -> int:
    if re.fullmatch(r"[@$%&][A-Za-z]{1,7}", lex):
        return -2
    return -1

def emparejar_ops(text: str, i: int) -> Optional[Tuple[str, int, int]]:
    n = len(text)
    if i >= n:
        return None
    ch = text[i]
    if ch in '@$&%' and (i + 1 < n and text[i + 1].isalpha()):
        return None
    for op in OpAritmeticos[:6]:
        if text.startswith(op, i):
            return (op, Tok_OpAritmeticos[op], len(op))
    for op in ["<=", "!=", ">=", "=="]:
        if text.startswith(op, i):
            return (op, Tok_Relacionales[op], len(op))
    for op in ["&&", "||"]:
        if text.startswith(op, i):
            return (op, Tok_Logicos[op], len(op))
    if ch in Tok_OpAritmeticos:
        return (ch, Tok_OpAritmeticos[ch], 1)
    if ch in Tok_Relacionales:
        return (ch, Tok_Relacionales[ch], 1)
    if ch in Tok_Logicos:
        return (ch, Tok_Logicos[ch], 1)
    if ch in Tok_Especiales:
        return (ch, Tok_Especiales[ch], 1)
    return None

def token_linea(line: str, num_linea: int) -> Tuple[List[Token], List[ErrorLex]]:
    tokens: List[Token] = []
    errores: List[ErrorLex] = []
    i = 0
    mcom = comentarios.search(line)
    corte = mcom.start() if mcom else len(line)

    while i < corte:
        msp = espacios.match(line, i)
        if msp:
            i = msp.end()
            continue

        # STRING (si no cierra, muestra completo el texto)
        if i < corte and line[i] == '"':
            mstr = string.match(line, i)
            if not mstr:
                lex_err = line[i:corte]
                errores.append(ErrorLex(lex_err, "String sin cerrar", _pts_error_lexeme(lex_err), num_linea))
                i = corte
                continue
            lex = mstr.group(0)
            tok = -54
            tokens.append(Token(lex, tok, _pts_token(tok), num_linea))
            i = mstr.end()
            continue

        # IDENTIFICADORES con prefijo o '&&' como operador lógico
        if line[i] in "@$%&":
            # Caso especial: '&&' es operador lógico válido
            if line[i] == '&' and i + 1 < corte and line[i + 1] == '&':
                tok = Tok_Logicos["&&"]
                tokens.append(Token("&&", tok, _pts_token(tok), num_linea))
                i += 2
                continue

            mfull = re.match(r"[@$%&][A-Za-z0-9_]*", line[i:corte])
            lex_full = mfull.group(0) if mfull else line[i]
            i_next = i + len(lex_full) if mfull else i + 1

            if re.fullmatch(r"[@$%&][A-Za-z]{1,7}", lex_full):
                tok = -51
                tokens.append(Token(lex_full, tok, _pts_token(tok), num_linea))
                i = i_next
                continue
            else:
                errores.append(
                    ErrorLex(
                        lex_full,
                        "Identificador inválido (solo letras tras el prefijo y longitud 2–8)",
                        _pts_error_lexeme(lex_full),
                        num_linea,
                    )
                )
                i = i_next
                continue

        # NÚMEROS
        mbad = invalid_real_final.match(line, i)
        if mbad:
            lex = mbad.group(0)
            errores.append(ErrorLex(lex, "Real no puede terminar con punto decimal", -1, num_linea))
            i += len(lex)
            continue

        if line[i] == '-' and i + 1 < corte and line[i + 1] in {'-', '='}:
            pass
        else:
            mreal = real.match(line, i)
            if mreal:
                lex = mreal.group(0)
                tok = -53
                tokens.append(Token(lex, tok, _pts_token(tok), num_linea))
                i = mreal.end()
                continue
            mint = entero.match(line, i)
            if mint:
                lex = mint.group(0)
                tok = clasificacion_numero(lex)
                tokens.append(Token(lex, tok, _pts_token(tok), num_linea))
                i = mint.end()
                continue

        # OPERADORES / ESPECIALES
        mop = emparejar_ops(line, i)
        if mop:
            lex, tok, adv = mop
            tokens.append(Token(lex, tok, _pts_token(tok), num_linea))
            i += adv
            continue

        # PALABRAS (reservadas o error)
        mword = re.match(r"[A-Za-z]+", line[i:])
        if mword:
            lex = mword.group(0)
            if lex in Tok_Preservadas:
                tok = Tok_Preservadas[lex]
                tokens.append(Token(lex, tok, _pts_token(tok), num_linea))
            else:
                errores.append(
                    ErrorLex(
                        lex,
                        "Identificador inválido (debe iniciar con @ $ & % y solo letras, 2-8)",
                        _pts_error_lexeme(lex),
                        num_linea,
                    )
                )
            i += len(lex)
            continue

        # IGNORADOS
        ch = line[i]
        if ch in {'.', '\t', ' ', '“', '”'}:
            i += 1
            continue

        # DESCONOCIDO
        errores.append(ErrorLex(ch, "Caracter no reconocido", _pts_error_lexeme(ch), num_linea))
        i += 1

    return tokens, errores

def scan(source: str) -> Tuple[List[Token], List[ErrorLex]]:
    all_tokens: List[Token] = []
    all_errores: List[ErrorLex] = []
    for nlinea, raw in enumerate(source.splitlines(), start=1):
        toks, errs = token_linea(raw, nlinea)
        all_tokens.extend(toks)
        all_errores.extend(errs)
    return all_tokens, all_errores
