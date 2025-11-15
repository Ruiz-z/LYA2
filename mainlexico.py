from lexico.lexer import scan, Token
from sintaxis.parser import Parser, ParserError, TK_EOF

def escribir_tokens(ruta: str, tokens):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("Lexema\tToken\tPTS\t#Linea\n")
        for t in tokens:
            f.write(f"{t.lexema}\t{t.token}\t{t.pts}\t{t.linea}\n")

def escribir_errores(ruta: str, errores):
    with open(ruta, "w", encoding="utf-8") as f:
        for e in errores:
            f.write(f"Error en la palabra:\t{e.lexema}\t{e.descripcion}\tEn la línea: {e.linea}\n")

def main():
    # 1. Leer fuente
    with open("lexico/entrada.txt", "r", encoding="utf-8") as f:
        fuente = f.read()

    # 2. Análisis léxico
    tokens, errores = scan(fuente)

    # 3. Guardar resultados léxicos
    escribir_tokens("lexico/tokens.txt", tokens)
    escribir_errores("lexico/errores.txt", errores)

    # 4. Si hay errores léxicos, detiene aquí
    if errores:
        print("Se encontraron errores léxicos. No se ejecutará el análisis sintáctico.")
        return

    # 5. Agregar token EOF para el parser
    if tokens:
        ultima_linea = tokens[-1].linea
    else:
        ultima_linea = 1
    eof_token = Token("EOF", TK_EOF, -1, ultima_linea)
    tokens_sintaxis = tokens + [eof_token]

    # 6. Ejecutar análisis sintáctico
    parser = Parser(tokens_sintaxis)
    try:
        parser.parsear()
        print("Análisis sintáctico correcto.")
        # opcional: escribir un archivo indicando éxito
        with open("lexico/sintaxis_ok.txt", "w", encoding="utf-8") as f:
            f.write("Análisis sintáctico correcto.\n")
    except ParserError as e:
        print("Error sintáctico:", e)
        with open("lexico/errores_sintacticos.txt", "w", encoding="utf-8") as f:
            f.write(str(e) + "\n")

if __name__ == "__main__":
    main()
