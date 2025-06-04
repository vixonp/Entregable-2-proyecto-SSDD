import mysql.connector
import pandas as pd
import subprocess
from datetime import datetime

config = {
    "host": "localhost",
    "user": "usuario",
    "password": "pass123",
    "database": "eventosdb",
    "port": 3306
}

def conectar_mysql():
    return mysql.connector.connect(**config)

def ejecutar_query(sql, params=None):
    conn = conectar_mysql()
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df

def ejecutar_modificacion(sql, params=None):
    conn = conectar_mysql()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    conn.close()

def exportar_xlsx():
    df = ejecutar_query("SELECT * FROM eventos")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"eventos_mysql_export_{timestamp}.xlsx"
    df.to_excel(nombre_archivo, index=False)
    return nombre_archivo

def controlar_docker(accion="up"):
    comando = ["docker", "compose", accion, "-d"] if accion == "up" else ["docker", "compose", "down"]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    return resultado.stdout if resultado.returncode == 0 else resultado.stderr

def eliminar_tabla_completa():
    conn = conectar_mysql()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tablas = [tabla[0] for tabla in cursor.fetchall()]
    if not tablas:
        print(" No hay tablas en la base de datos.")
        conn.close()
        return

    print("\n Tablas disponibles:")
    for idx, tabla in enumerate(tablas, 1):
        print(f"{idx}. {tabla}")

    try:
        eleccion = int(input("\nElige el número de la tabla que deseas eliminar: ").strip())
        if 1 <= eleccion <= len(tablas):
            tabla_a_eliminar = tablas[eleccion - 1]
            confirm = input(f" ¿Seguro que quieres eliminar toda la tabla '{tabla_a_eliminar}'? [s/N]: ").strip().lower()
            if confirm == "s":
                cursor.execute(f"DROP TABLE `{tabla_a_eliminar}`")
                conn.commit()
                print(f" Tabla '{tabla_a_eliminar}' eliminada correctamente.")
            else:
                print(" Cancelado.")
        else:
            print(" Número fuera de rango.")
    except ValueError:
        print(" Entrada no válida.")
    conn.close()

def menu_mysql():
    print(" MENÚ DE CONSULTAS Y GESTIÓN DE TABLA 'eventos'")
    print("1. Total de eventos")
    print("2. Eventos por tipo")
    print("3. Eventos por cuadrante")
    print("4. Eventos por fecha")
    print("5. Ver tabla completa (limit 50)")
    print("6. Ver eventos por tipo específico")
    print("7. Eliminar TODOS los eventos")
    print("8. Eliminar eventos por tipo")
    print("9. Eliminar eventos por cuadrante")
    print("10. Exportar a Excel")
    print("11. Iniciar Docker Compose")
    print("12. Detener Docker Compose")
    print("13. Eliminar tabla completa (elegir tabla)")
    print("0. Salir")

    opcion = input("Elige una opción [0-13]: ").strip()

    if opcion == "1":
        df = ejecutar_query("SELECT COUNT(*) AS total_eventos FROM eventos")
        print(df)
    elif opcion == "2":
        df = ejecutar_query("""
            SELECT tipo, COUNT(*) AS cantidad FROM eventos GROUP BY tipo ORDER BY cantidad DESC
        """)
        print(df)
    elif opcion == "3":
        df = ejecutar_query("""
            SELECT cuadrante, COUNT(*) AS cantidad FROM eventos GROUP BY cuadrante ORDER BY cuadrante
        """)
        print(df)
    elif opcion == "4":
        df = ejecutar_query("""
            SELECT DATE(fecha_extraccion) AS fecha, COUNT(*) AS cantidad FROM eventos GROUP BY DATE(fecha_extraccion)
        """)
        print(df)
    elif opcion == "5":
        df = ejecutar_query("SELECT * FROM eventos LIMIT 50")
        print(df)
    elif opcion == "6":
        tipo = input("Tipo de evento a consultar: ").strip()
        df = ejecutar_query("SELECT * FROM eventos WHERE tipo = %s", (tipo,))
        print(df)
    elif opcion == "7":
        confirm = input(" ¿Eliminar TODOS los eventos? [s/N]: ").strip().lower()
        if confirm == "s":
            ejecutar_modificacion("DELETE FROM eventos")
            print(" Todos eliminados.")
    elif opcion == "8":
        tipo = input("Tipo a eliminar: ").strip()
        ejecutar_modificacion("DELETE FROM eventos WHERE tipo = %s", (tipo,))
        print(" Eliminados.")
    elif opcion == "9":
        cuadrante = input("Cuadrante a eliminar: ").strip()
        ejecutar_modificacion("DELETE FROM eventos WHERE cuadrante = %s", (cuadrante,))
        print(" Eliminados.")
    elif opcion == "10":
        archivo = exportar_xlsx()
        print(f"Exportado como: {archivo}")
    elif opcion == "11":
        print(controlar_docker("up"))
    elif opcion == "12":
        print(controlar_docker("down"))
    elif opcion == "13":
        eliminar_tabla_completa()
    elif opcion == "0":
        print("Saliendo del menú.")
    else:
        print("Opción no válida.")
