import os
import pandas as pd
import subprocess
import stat
import time # Añadido para esperas

# ==============================================================================
# Configuración
# ==============================================================================
PIG_CONTAINER_NAME = "pig_container"
PIG_WORKING_DIR_CONTAINER = "/data" # Donde se monta ./data del host
HDFS_INPUT_DIR = "/user/hadoop/input" # Directorio de HDFS para entrada
HDFS_OUTPUT_ROOT_DIR = "/user/hadoop" # Directorio de HDFS para salida
JAVA_HOME = "/usr/lib/jvm/java-8-openjdk-amd64" # JAVA_HOME dentro del contenedor

# ==============================================================================
# Funciones auxiliares
# ==============================================================================

def ejecutar_comando_docker(comando):
    """Ejecuta un comando de Docker y retorna la salida o el error."""
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
        return True, resultado.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()
    except FileNotFoundError:
        return False, "Error: El comando 'docker' no se encontró. Asegúrate de tener Docker instalado y en el PATH."
    except Exception as e:
        return False, f"Error inesperado al ejecutar comando Docker: {e}"

def convertir_excel_a_csv(ruta_excel="data/eventos.xlsx", ruta_csv="data/eventos.csv"):
    """Convierte un archivo Excel a CSV."""
    print(f" Convirtiendo {ruta_excel} a {ruta_csv}...")
    if not os.path.exists(ruta_excel):
        print(f" Error: Archivo Excel de entrada no encontrado: {ruta_excel}")
        return False
    try:
        df = pd.read_excel(ruta_excel)
        df.to_csv(ruta_csv, index=False)
        print(f" Conversión exitosa. CSV guardado en {ruta_csv}")
        return True
    except Exception as e:
        print(f" Error al convertir Excel a CSV: {e}")
        return False

def check_container_running(nombre_contenedor):
    success, output = ejecutar_comando_docker(["docker", "ps", "--filter", f"name={nombre_contenedor}", "--format", "{{.Names}}"])
    return success and nombre_contenedor in output

def iniciar_hadoop_en_contenedor(nombre_contenedor="pig_container"):
    """Inicia Hadoop en segundo plano dentro del contenedor y verifica que está corriendo."""
    print("🚀 Iniciando Hadoop dentro del contenedor...")

    # Lanzar start_hadoop.sh sin esperar a que se quede vivo
    comando_inicio = [
        "docker", "exec", "-d", nombre_contenedor,
        "bash", "-c", "start_hadoop.sh &"
    ]
    subprocess.run(comando_inicio)

    # Esperar unos segundos para que los servicios se levanten
    print("⏳ Esperando a que Hadoop termine de levantar servicios...")
    time.sleep(10)  # puedes subir a 15 si hace falta

    # Verificar que los procesos de Hadoop están corriendo con jps
    comando_jps = ["docker", "exec", nombre_contenedor, "jps"]
    resultado = subprocess.run(comando_jps, capture_output=True, text=True)

    if resultado.returncode != 0:
        print("❌ No se pudo ejecutar jps para verificar servicios Hadoop.")
        return False

    procesos = resultado.stdout.strip().splitlines()
    procesos_requeridos = ["NameNode", "DataNode", "ResourceManager", "NodeManager"]

    activos = [proc for proc in procesos if any(p in proc for p in procesos_requeridos)]

    if len(activos) >= 3:  # espera al menos 3 de 4 para considerarlo válido
        print("✅ Hadoop iniciado correctamente dentro del contenedor:")
        for proc in activos:
            print("   -", proc)
        return True
    else:
        print("⚠️ Servicios de Hadoop no parecen estar activos todavía.")
        print(resultado.stdout)
        return False



def ejecutar_hdfs_comando(comando_hdfs):
    """Ejecuta un comando HDFS dentro del contenedor Pig."""
    comando = ["docker", "exec", PIG_CONTAINER_NAME, "hdfs", "dfs"] + comando_hdfs
    print(f"Executing HDFS command: {' '.join(comando_hdfs)}")
    return ejecutar_comando_docker(comando)

def cargar_csv_a_hdfs(local_csv_path="data/eventos.csv", hdfs_path=f"{HDFS_INPUT_DIR}/eventos.csv"):
    """Copia el archivo CSV del host a HDFS."""
    print(f" Cargando {local_csv_path} a HDFS ({hdfs_path})...")
    if not os.path.exists(local_csv_path):
        print(f" Error: CSV de entrada no encontrado en el host: {local_csv_path}")
        return False

    # Crear el directorio de entrada en HDFS si no existe
    ejecutar_hdfs_comando(["-mkdir", "-p", HDFS_INPUT_DIR])

    # Copiar el archivo del sistema de archivos local del contenedor a HDFS
    # Primero copiamos el archivo del host al /data del contenedor (gracias al volumen)
    # Luego, desde /data en el contenedor, lo copiamos a HDFS
    container_local_path = f"{PIG_WORKING_DIR_CONTAINER}/eventos.csv"
    
    # Asegúrate de que el archivo existe en la ruta local del contenedor
    # (Ya se verificó al inicio de la función ejecutar_pig_paralelo con verificar_csv_en_contenedor,
    # pero aquí nos aseguramos antes de mover a HDFS)
    
    # Eliminar archivo previo en HDFS para evitar duplicados si existe
    ejecutar_hdfs_comando(["-rm", "-f", hdfs_path])
    
    success, output = ejecutar_hdfs_comando(["-put", container_local_path, hdfs_path])
    if not success:
        print(f" Error al cargar CSV a HDFS: {output}")
        return False
    print(f" CSV cargado a HDFS: {hdfs_path}")
    return True

def eliminar_hdfs_output(hdfs_path):
    """Elimina un directorio de salida en HDFS."""
    print(f" Eliminando output previo en HDFS: {hdfs_path}...")
    success, output = ejecutar_hdfs_comando(["-rm", "-r", "-skipTrash", hdfs_path])
    if not success and "No such file or directory" not in output: # Ignorar si no existe
        print(f" Advertencia: No se pudo eliminar el directorio de salida HDFS '{hdfs_path}'. Error: {output}")
    else:
        print(f" Output HDFS previo eliminado (o no existía).")

def copiar_resultado_de_hdfs(hdfs_source_path, local_destination_path):
    """Copia el resultado de Pig desde HDFS al host."""
    print(f" Copiando resultado de HDFS ({hdfs_source_path}) a {local_destination_path}...")
    
    if not os.path.exists(os.path.dirname(local_destination_path)):
        os.makedirs(os.path.dirname(local_destination_path))

    # Eliminar cualquier archivo o carpeta preexistente en la ruta de destino local
    if os.path.exists(local_destination_path):
        if os.path.isdir(local_destination_path):
            try:
                import shutil
                shutil.rmtree(local_destination_path)
            except Exception as e:
                print(f" Error al eliminar directorio local {local_destination_path}: {e}")
                return False
        else:
            try:
                os.remove(local_destination_path)
            except Exception as e:
                print(f" Error al eliminar archivo local {local_destination_path}: {e}")
                return False
    
    # Copiar del HDFS al /data del contenedor, luego del /data al host
    # Hadoop tiene un comando get que ya hace esto para directorios.
    # El comando -get copiará el directorio entero con sus partes.
    success, output = ejecutar_hdfs_comando(["-get", hdfs_source_path, f"{PIG_WORKING_DIR_CONTAINER}/"])
    
    if not success:
        print(f" Error al copiar resultado de HDFS a contenedor local: {output}")
        return False
    
    # Mover el archivo part-r-00000 de la carpeta copiada a la ruta final en el host
    # El -get comando crea una carpeta con el nombre de hdfs_source_path (ej. output_tipo_calle.csv)
    # dentro de /data. Necesitamos acceder a part-r-00000 dentro de esa carpeta.
    copied_dir_in_container_name = os.path.basename(hdfs_source_path) # ej. output_tipo_calle.csv
    container_part_file_path = f"{PIG_WORKING_DIR_CONTAINER}/{copied_dir_in_container_name}/part-r-00000"
    
    # Ahora, copiamos el part-r-00000 de vuelta al destino local del host
    comando_cp_to_host = ["docker", "cp", f"{PIG_CONTAINER_NAME}:{container_part_file_path}", local_destination_path]
    success_cp, output_cp = ejecutar_comando_docker(comando_cp_to_host)

    if not success_cp:
        print(f" Error al copiar part-r-00000 de contenedor al host: {output_cp}")
        return False

    print(f" Resultado copiado a {local_destination_path}")
    return True



def ejecutar_pig_paralelo():
    print("\n Iniciando procesamiento distribuido con Pig sobre Hadoop...")

    if not check_container_running(PIG_CONTAINER_NAME):
        print(f" Error: El contenedor '{PIG_CONTAINER_NAME}' no está corriendo. Inícialo primero.")
        print("Asegúrate de ejecutar 'docker-compose up -d' y esperar a que Hadoop inicie.")
        return

    if not iniciar_hadoop_en_contenedor():
        print("❌ Proceso detenido porque no se pudo iniciar Hadoop.")
        return

    # 1. Convertir Excel a CSV (en el host)
    local_input_csv = "data/eventos.csv"
    if not convertir_excel_a_csv(ruta_csv=local_input_csv): 
        print("Proceso detenido debido a error en conversión de Excel a CSV.")
        return

    # 2. Copiar CSV al HDFS (Desde el volumen compartido, a HDFS)
    #    Pig leerá desde HDFS, no desde el sistema de archivos local del contenedor.
    hdfs_input_file = f"{HDFS_INPUT_DIR}/eventos.csv"
    if not cargar_csv_a_hdfs(local_csv_path=local_input_csv, hdfs_path=hdfs_input_file):
        print("Proceso detenido porque falló la carga del CSV a HDFS.")
        return

    scripts = [
        {
            "script": "test.pig",
            "hdfs_output_dir": "output_tipo_calle.csv", # Será /user/hadoop/output_tipo_calle.csv en HDFS
            "result_file": "data/output_tipo_calle.csv", # Ruta final en el host
            "columnas": ["tipo", "calle", "cantidad"]
        },
        {
            "script": "test_hora.pig",
            "hdfs_output_dir": "output_por_hora.csv", # Será /user/hadoop/output_por_hora.csv en HDFS
            "result_file": "data/output_por_hora.csv", # Ruta final en el host
            "columnas": ["hora", "cantidad"]
        }
    ]

    procesos = []

    for cfg in scripts:
        script_in_container_path = f"{PIG_WORKING_DIR_CONTAINER}/{cfg['script']}" # Ruta del script en el volumen del contenedor
        local_script_path = f"data/{cfg['script']}" # Ruta del script en el host
        hdfs_final_output_path = f"{HDFS_OUTPUT_ROOT_DIR}/{cfg['hdfs_output_dir']}" # Ruta de salida en HDFS
        log_path = f"data/{cfg['script']}.log" # Ruta del log en el host
        
        # Copiar script Pig al contenedor (a /data), si no confías solo en el volumen
        # Con el volumen ./data:/data, el script ya está en /data/test.pig
        # Si prefieres ser explícito:
        # success_cp_script, _ = ejecutar_comando_docker(["docker", "cp", local_script_path, f"{PIG_CONTAINER_NAME}:{script_in_container_path}"])
        # if not success_cp_script:
        #     print(f" Falló la copia del script: {cfg['script']}. Proceso para este script detenido.")
        #     continue

        # Verificar que el script existe en el contenedor (accesible via volumen)
        success_check_script, output_check_script = ejecutar_comando_docker(["docker", "exec", PIG_CONTAINER_NAME, "test", "-f", script_in_container_path])
        if not success_check_script:
            print(f" Error: Script '{script_in_container_path}' no encontrado en el contenedor '{PIG_CONTAINER_NAME}'.")
            print(f"Asegúrate de que '{local_script_path}' existe en tu host y el volumen está bien mapeado.")
            continue


        # Eliminar output previo en HDFS
        eliminar_hdfs_output(hdfs_final_output_path)

        # Ejecutar Pig sobre Hadoop (sin -x local)
        comando_pig_exec = [
            "docker", "exec", "-i", PIG_CONTAINER_NAME,
            "bash", "-c",
            f"export JAVA_HOME={JAVA_HOME} && pig {script_in_container_path}"
        ]
        
        print(f" Ejecutando Pig para {cfg['script']} sobre Hadoop...")
        log_file = open(log_path, "w", encoding="utf-8")
        proc = subprocess.Popen(comando_pig_exec, stdout=log_file, stderr=subprocess.STDOUT, text=True)
        procesos.append((proc, log_file, cfg))

    # Esperar y procesar resultados
    for proc, log_file, cfg in procesos:
        proc.wait() # Espera a que el proceso Pig termine
        log_file.close()
        print(f" {cfg['script']} completado. Log guardado en: {log_file.name}")

        # Después de que Pig termina, la salida está en HDFS
        hdfs_source_path = f"{HDFS_OUTPUT_ROOT_DIR}/{cfg['hdfs_output_dir']}"
        final_csv_on_host = cfg["result_file"] # Ruta del CSV final en el host
        final_xlsx_on_host = final_csv_on_host.replace(".csv", ".xlsx") # Ruta del XLSX final en el host

        # Copiar el resultado de Pig desde HDFS al host
        if not copiar_resultado_de_hdfs(hdfs_source_path, final_csv_on_host):
            print(f" No se pudo copiar el resultado de HDFS para {cfg['script']}. Revisa los logs.")
            continue

        # Convertir el CSV de resultado a Excel
        if os.path.exists(final_csv_on_host):
            try:
                # Pig por defecto usa tabulador para la salida. Asegúrate de que tus scripts Pig
                # están usando PigStorage(',') o cambia sep="\t" aquí.
                df = pd.read_csv(final_csv_on_host, sep="\t", names=cfg["columnas"]) 
                df.to_excel(final_xlsx_on_host, index=False)
                print(f" Exportado a Excel: {final_xlsx_on_host}")
            except Exception as e:
                print(f" Error exportando {cfg['script']} a Excel: {e}. Revisa el formato del CSV de salida de Pig o el separador en read_csv.")
        else:
            print(f" No se encontró el archivo CSV de salida en el host para {cfg['script']}: {final_csv_on_host}")

def ejecutar_pig_local():
    print("\n Ejecutando procesamiento local con Apache Pig...")

    if not convertir_excel_a_csv():
        print("Error: No se pudo convertir el archivo Excel a CSV.")
        return

    scripts = [
        {
            "script": "test.pig",
            "output_dir": "/data/output_tipo_calle",  # 🔁 CORREGIDO: sin .csv
            "result_file": "data/output_tipo_calle.csv",
            "xlsx_file": "data/output_tipo_calle.xlsx",
            "columnas": ["tipo", "calle", "cantidad"]
        },
        {
            "script": "test_hora.pig",
            "output_dir": "/data/output_por_hora",  # 🔁 CORREGIDO: sin .csv
            "result_file": "data/output_por_hora.csv",
            "xlsx_file": "data/output_por_hora.xlsx",
            "columnas": ["hora", "cantidad"]
        }
    ]

    contenedor = "pig_container"

    for cfg in scripts:
        print(f" Ejecutando Pig local para {cfg['script']}...")

        script_path = f"/data/{cfg['script']}"
        log_path = f"data/{cfg['script']}.log"

        subprocess.run(["docker", "cp", f"data/{cfg['script']}", f"{contenedor}:{script_path}"])
        subprocess.run(["docker", "exec", contenedor, "rm", "-rf", cfg["output_dir"]])

        comando = [
            "docker", "exec", "-i", contenedor,
            "bash", "-c",
            f"export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 && pig -x local {script_path}"
        ]

        with open(log_path, "w", encoding="utf-8") as log:
            proceso = subprocess.run(comando, stdout=log, stderr=subprocess.STDOUT, text=True)

        if proceso.returncode != 0:
            print(f"❌ Error al ejecutar {cfg['script']}. Revisa el log: {log_path}")
            continue

        print(f"✅ {cfg['script']} completado. Log guardado en {log_path}")

        if os.path.exists(cfg["result_file"]):
            try:
                os.remove(cfg["result_file"])
            except Exception as e:
                print(f"⚠️ No se pudo eliminar el archivo anterior {cfg['result_file']}: {e}")
                continue

        salida_contenedor = f"{cfg['output_dir']}/part-r-00000"
        resultado = subprocess.run(
            ["docker", "cp", f"{contenedor}:{salida_contenedor}", cfg["result_file"]],
            capture_output=True, text=True
        )

        if resultado.returncode != 0:
            print(f"❌ No se pudo copiar el resultado desde el contenedor: {resultado.stderr.strip()}")
            continue

        if not os.path.exists(cfg["result_file"]) or os.path.getsize(cfg["result_file"]) == 0:
            print(f"❌ El archivo {cfg['result_file']} no se creó correctamente o está vacío.")
            continue

        try:
            df = pd.read_csv(cfg["result_file"], sep="\t", names=cfg["columnas"])
            df.to_excel(cfg["xlsx_file"], index=False)
            print(f"📁 Exportado a Excel: {cfg['xlsx_file']}")
        except Exception as e:
            print(f"❌ Error procesando salida de {cfg['script']}: {e}")


# Las funciones mostrar_resultado_hora y mostrar_resultado_pig no cambian,
# ya que leen los XLSX generados por ejecutar_pig_paralelo().
def mostrar_resultado_hora():
    archivo_xlsx = "data/output_por_hora.xlsx" 
    if not os.path.exists(archivo_xlsx):
        print(" El archivo de evolución por hora aún no ha sido generado (o convertido a XLSX). Ejecuta Pig primero.")
        return

    try:
        df = pd.read_excel(archivo_xlsx)
        print(f" Resultado leído de Excel: {archivo_xlsx}\n")
        print(" Evolución temporal de eventos:")
        print(df)
    except Exception as e:
        print(f" Error al procesar los resultados por hora desde Excel: {e}")

def mostrar_resultado_pig():
    archivo_xlsx = "data/output_tipo_calle.xlsx" 
    if not os.path.exists(archivo_xlsx):
        print(" El archivo de resultados tipo-calle aún no ha sido generado (o convertido a XLSX). Ejecuta Pig primero.")
        return

    try:
        df = pd.read_excel(archivo_xlsx)
        print(f" Resultado leído de Excel: {archivo_xlsx}\n")
        print(" Resultados tipo-calle:")
        print(df.head())
    except Exception as e:
        print(f" Error al procesar los resultados tipo-calle desde Excel: {e}")