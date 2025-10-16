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


#Se escriben las palabras reservadas para despues darle su identificador a cada uno
    Preservadas = ["clase","leer","siwtch","posxy","entero","var","escribir","encaso","limpiar","real",
                   "vacio","si","repite","ejecutar","regresar","metodo","sino","mientras","cadena","salir"]
    Tok_Preservadas = {lex: -(i+1) for i, lex in enumerate(Preservadas) }

#se escriben los operadores aritmeticos primero
#los que tienen dos simbolos y despues
    OpAritmeticos = ["++","--","+=","-=","/=", "*=","+","-","*","/","%","="]
    Tok_OpAritmeticos = {op: -(21+i) for i, op in enumerate(OpAritmeticos) }

    OpRelacionales = ["<","<=","!=",">",">=","=="]
    Tok_Relacionales = {op: -(33+i) for i, op in enumerate(OpRelacionales) }

    OpLogicos = ["&&","||","!"]
    Tok_log = {op: -(41+i) for i, op in enumerate(OpLogicos) }


    OpEspeciales = [";","[","]",",",":","(",")","{","}"]
    Tok_Especiales =  {ch: -(61+i) for i, ch in enumerate(OpEspeciales) }

espacios = re.compile(r"[ \t]+")
comentarios = re.compile(r"//.*$")
string = re.compile(r"\"(?:[^\"\n]|\\\")*\"")

real = re.compile(r"-?(\d+\.\d+|\.\d+)")
entero = re.compile(r"-?\d+")

#identificadores
idClaMet = re.compile(r"@[A-Za-z]{1,7}")
idstring = re.compile(r"\$([A-Za-z]{1,7})")
identero = re.compile(r"&[A-Za-z]{1,7}")
idreal = re.compile(r"%[A-Za-z]{1,7}")