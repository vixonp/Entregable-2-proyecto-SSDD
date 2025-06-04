import mysql.connector
import pandas as pd
import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
import os

def graficar_tipo_calle():
    ruta = "data/output_tipo_calle.xlsx"
    if not os.path.exists(ruta):
        print("❌ Archivo 'output_tipo_calle.xlsx' no encontrado.")
        return

    df = pd.read_excel(ruta)
    df_filtrado = df[df["cantidad"] > 1]  # Opcional: filtra calles con más de 1 evento
    top_calles = df_filtrado.groupby("tipo")["cantidad"].sum().sort_values(ascending=False).head(10)

    plt.figure(figsize=(10, 6))
    top_calles.plot(kind="bar", color='skyblue')
    plt.title("Top 10 tipos de eventos por cantidad total")
    plt.xlabel("Tipo de evento")
    plt.ylabel("Cantidad total en distintas calles")
    plt.xticks(rotation=45)
    plt.tight_layout()
    output_path = "distribucion_tipos_evento.png"
    plt.savefig(output_path)
    print(f"✅ Gráfico guardado como: {output_path}")
    plt.show()

def graficar_por_hora():
    ruta = "data/output_por_hora.xlsx"
    if not os.path.exists(ruta):
        print("❌ Archivo 'output_por_hora.xlsx' no encontrado.")
        return

    df = pd.read_excel(ruta)
    df["hora"] = pd.to_numeric(df["hora"], errors='coerce')
    df = df.dropna().sort_values("hora")

    plt.figure(figsize=(10, 6))
    plt.plot(df["hora"], df["cantidad"], marker='o', linestyle='-')
    plt.title("Evolución de eventos por hora")
    plt.xlabel("Hora del día")
    plt.ylabel("Cantidad de eventos")
    plt.grid(True)
    plt.xticks(range(0, 24))
    plt.tight_layout()
    output_path = "evolucion_eventos_por_hora.png"
    plt.savefig(output_path)
    print(f"✅ Gráfico guardado como: {output_path}")
    plt.show()