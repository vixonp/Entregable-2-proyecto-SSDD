import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from db import conectar_mysql

nombres_calles = [
    "Alameda Centro", "Plaza Italia", "Apoquindo Las Condes", "Vespucio Norte",
    "Vespucio Sur", "Grecia Ñuñoa", "Costanera Norte", "Autopista Central",
    "Av. La Florida", "Providencia", "Estación Central", "Pudahuel", "Maipú",
    "Peñalolén", "Puente Alto", "Lo Barnechea", "San Miguel", "San Bernardo",
    "Las Rejas", "Camino a Melipilla", "Los Dominicos", "Quinta Normal",
    "Independencia", "Macul", "La Cisterna", "Lo Prado", "Huechuraba",
    "Recoleta", "San Joaquín", "Ñuñoa Plaza Egaña"
]

bounding_box = {
    "bottom": -33.87,
    "top": -33.28,
    "left": -71.02,
    "right": -70.38
}

def iniciar_driver(modo_headless=True):
    options = Options()
    if modo_headless:
        options.add_argument("--headless=new")
    else:
        options.add_argument("--start-maximized")
    options.add_argument("--window-size=1280,800")
    options.add_argument("user-agent=Mozilla/5.0")
    return webdriver.Chrome(service=Service("chromedriver.exe"), options=options)

def ejecutar_scraping():
    modo_headless = input("\n¿Ejecutar en modo headless (sin navegador visible)? [s/n]: ").strip().lower() == "s"
    driver = iniciar_driver(modo_headless)

    conn = conectar_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM eventos")
    total_guardados = cursor.fetchone()[0]
    print(f"\nℹ️ Ya existen {total_guardados} eventos en la base de datos.")

    espera_segundos = 7
    max_eventos = 10000
    lat_total = bounding_box["top"] - bounding_box["bottom"]
    lon_total = bounding_box["right"] - bounding_box["left"]
    base_div = 16
    lat_step = lat_total / base_div
    lon_step = lon_total / base_div
    center_lat = (bounding_box["bottom"] + bounding_box["top"]) / 2
    center_lon = (bounding_box["left"] + bounding_box["right"]) / 2
    expansion = 1

    while total_guardados < max_eventos:
        zoom = max(14 - (expansion // 3), 11)
        cuadrantes = []
        for i in range(-expansion + 1, expansion):
            for j in range(-expansion + 1, expansion):
                lat_centro = center_lat + i * lat_step
                lon_centro = center_lon + j * lon_step
                if bounding_box["bottom"] <= lat_centro <= bounding_box["top"] and bounding_box["left"] <= lon_centro <= bounding_box["right"]:
                    cuadrantes.append((lat_centro, lon_centro, f"Q{expansion}_{i+expansion}_{j+expansion}"))

        for lat_centro, lon_centro, cuadrante_nombre in cuadrantes:
            if total_guardados >= max_eventos:
                break

            driver.get(f"https://www.waze.com/live-map?ll={lat_centro}%2C{lon_centro}&zoom={zoom}")
            time.sleep(espera_segundos)
            icons = driver.find_elements(By.CSS_SELECTOR, "div.leaflet-marker-icon")

            for icon in icons:
                if total_guardados >= max_eventos:
                    break
                try:
                    clases = icon.get_attribute("class").split()
                    tipo = next((c.replace("wm-alert-icon--", "").replace("wm-alert-cluster-icon--", "").replace("wm-user-icon--", "")
                                 for c in clases if c.startswith("wm-")), "desconocido")
                    descripcion = f"Evento tipo {tipo}"
                    lat = lat_centro
                    lon = lon_centro
                    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    calle = random.choice(nombres_calles)

                    cursor.execute("SELECT COUNT(*) FROM eventos WHERE tipo = %s AND cuadrante = %s AND fecha_extraccion = %s", (tipo, cuadrante_nombre, fecha))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            INSERT INTO eventos (tipo, descripcion, lat, lon, fecha_extraccion, cuadrante, calle)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (tipo, descripcion, lat, lon, fecha, cuadrante_nombre, calle))
                        conn.commit()
                        total_guardados += 1

                except Exception as e:
                    print("Error al guardar evento:", e)

        expansion += 1

    cursor.close()
    conn.close()
    driver.quit()
    print(f"\n✅ Extracción completada. Total de eventos capturados: {total_guardados}")
