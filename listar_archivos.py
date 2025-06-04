import os

def listar_archivos_directorio(raiz=".", archivo_salida="estructura_proyecto.txt"):
    with open(archivo_salida, "w", encoding="utf-8") as f:
        for carpeta_raiz, carpetas, archivos in os.walk(raiz):
            nivel = carpeta_raiz.replace(raiz, "").count(os.sep)
            indentacion = " " * 4 * nivel
            f.write(f"{indentacion}{os.path.basename(carpeta_raiz)}/\n")
            subindentacion = " " * 4 * (nivel + 1)
            for archivo in archivos:
                f.write(f"{subindentacion}{archivo}\n")
    print(f"📄 Estructura guardada en {archivo_salida}")

if __name__ == "__main__":
    listar_archivos_directorio()
