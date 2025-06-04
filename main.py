from scraper import ejecutar_scraping
from db import menu_mysql
from funciones import graficar_tipo_calle, graficar_por_hora
from trafico import simular_cache_y_exportar
from pig_processor import ejecutar_pig_local,ejecutar_pig_paralelo, mostrar_resultado_pig, mostrar_resultado_hora  # Agregado mostrar_resultado_pig


def menu_principal():
    while True:
        print("\n===== MENÚ PRINCIPAL - SISTEMA DE EVENTOS DE TRÁFICO =====")
        print("1. Ejecutar scraping de eventos desde Waze")
        print("2. Consultar base de datos MySQL (menú extendido)")
        print("3. Ejecutar simulación de tráfico y evaluar caché")
        print("4. Ejecutar procesamiento distribuido con Apache Pig de forma local")
        print("5. Ejecutar procesamiento distribuido con Apache Pig con hadoop (en construccion)")
        print("6. Ver resultados del procesamiento Pig (tipo y calle)") 
        print("7. Ver evolución temporal de eventos (por hora)")         
        print("8. Graficar distribución por tipo y calle")  
        print("9. Graficar evolución por hora")            
        print("0. Salir")
        opcion = input("\nElige una opción [0-8]: ")

        if opcion == "1":
            ejecutar_scraping()
        elif opcion == "2":
            menu_mysql()
        elif opcion == "3":
            simular_cache_y_exportar()
        elif opcion == "4":
            ejecutar_pig_local()
        elif opcion == "5":
            ejecutar_pig_paralelo()
        elif opcion == "6":
            mostrar_resultado_pig()  # Resultado por tipo y calle
        elif opcion == "7":
            mostrar_resultado_hora()  
        elif opcion == "8":
            graficar_tipo_calle()
        elif opcion == "9":
            graficar_por_hora()
        elif opcion == "0":
            break
        else:
            print("Opción inválida. Intenta de nuevo.")

if __name__ == "__main__":
    menu_principal()
# main.py