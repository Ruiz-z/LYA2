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
    Tok_OpAritmeticos = {lex: -(21+i) for i, lex in enumerate(OpAritmeticos) }

    OpRelacionales = ["<","<=","!=",">",">=","=="]
    OpLogicos = [";","[","]",",",":","(",")","{","}"]

