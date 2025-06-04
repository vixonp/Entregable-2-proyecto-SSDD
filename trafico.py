import numpy as np
import time
from datetime import datetime
from db import ejecutar_query
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)
TTL = 3600  # segundos


def consultar_evento(id_evento):
    clave = f"evento:{id_evento}"
    if cache.exists(clave):
        cache.incr(f"{clave}:hits", 1)
        return cache.get(clave).decode(), "HIT"
    else:
        df = ejecutar_query("SELECT * FROM eventos WHERE id = %s", (id_evento,))
        if not df.empty:
            valor = df.to_json()
            cache.setex(clave, TTL, valor)
            return valor, "MISS"
        return None, "MISS"

def obtener_eventos_unicos(n):
    df = ejecutar_query("SELECT id FROM eventos ORDER BY RAND() LIMIT %s", (n,))
    return df["id"].tolist()

def simular_cache_y_exportar():
    print("\n🧪 Simulación de tráfico iniciada.")
    tipo = input("¿Tipo de distribución? [poisson/exponencial]: ").strip().lower()
    tasa = float(input("Tasa promedio (λ): "))
    repeticiones = int(input("Número total de consultas: "))
    eventos = obtener_eventos_unicos(10)

    if tipo == "poisson":
        esperas = np.random.exponential(1 / tasa, repeticiones)
    else:
        esperas = np.random.exponential(tasa, repeticiones)

    historial = []
    for i in range(repeticiones):
        id_evento = eventos[i % len(eventos)]
        resultado, estado = consultar_evento(id_evento)
        historial.append({"id": id_evento, "resultado": estado, "momento": datetime.now()})
        print(f"[{i+1}/{repeticiones}] Evento ID {id_evento}: {estado}")
        time.sleep(esperas[i])

    exportar_resultados(historial)

import pandas as pd
import matplotlib.pyplot as plt

def exportar_resultados(historial):
    df = pd.DataFrame(historial)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = f"resultados_cache_{timestamp}.xlsx"
    df.to_excel(archivo, index=False)

    resumen = df["resultado"].value_counts()
    resumen.plot(kind="bar", color=["green", "red"])
    plt.title("Resumen de HITs y MISSes")
    plt.xlabel("Estado")
    plt.ylabel("Cantidad")
    plt.grid(axis="y", linestyle="--")
    nombre_img = f"resumen_cache_{timestamp}.png"
    plt.savefig(nombre_img)
    plt.show()

    efectividad = (df["resultado"] == "HIT").cumsum() / (df.index + 1)
    plt.plot(efectividad)
    plt.title("Curva de efectividad acumulada del caché")
    plt.xlabel("Consulta")
    plt.ylabel("Efectividad (%)")
    nombre_img2 = f"curva_cache_{timestamp}.png"
    plt.savefig(nombre_img2)
    plt.show()

    print(f"\n✅ Resultados exportados en: {archivo}")
