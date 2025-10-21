from lexico.lexer import scan

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
    with open("lexico/entrada.txt", "r", encoding="utf-8") as f:
        fuente = f.read()
    tokens, errores = scan(fuente)
    escribir_tokens("lexico/tokens.txt", tokens)
    escribir_errores("lexico/errores.txt", errores)

if __name__ == "__main__":
    main()
