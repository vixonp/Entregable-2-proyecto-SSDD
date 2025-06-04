# entregable2
entregable 2 proyecto SSDD

# Proyecto Sistemas Distribuidos - Entrega 2: Procesamiento Distribuido con Pig

**Autores**: Lucas Vicuña, Vicente Silva  
**Curso**: Sistemas Distribuidos - Universidad Diego Portales  
**Profesor**: Nicolás Hidalgo  
**Fecha**: 2 de junio de 2025  

---

## Descripción General

Esta segunda entrega expande el sistema distribuido de análisis de eventos de tráfico mediante el uso de **Apache Pig** como herramienta de procesamiento paralelo. Se incorporan nuevos análisis agrupando eventos por **tipo y calle** y por **hora de ocurrencia**, con visualizaciones generadas automáticamente.

---

## Tecnologías utilizadas

- **Python 3.10+**
- **MySQL 8.0 (contenedor Docker)**
- **Apache Pig 0.17 (contenedor Docker)**
- **Redis 7 (contenedor Docker)**
- **Selenium (modo headless) + ChromeDriver**
- **Pandas, NumPy, Matplotlib**
- **Docker + Docker Compose**

---

## Instalación y ejecución

### 1. Clona el repositorio

```bash
git clone https://github.com/vixonp/Entregable-2-proyecto-SSDD.git
cd sistemas_distribuidos
```

### 2. Requisitos

- Docker + Docker Compose
- Python 3.10+
- `chromedriver.exe` (ya incluido)
- Google Chrome instalado

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Levanta los servicios

```bash
docker-compose up -d
```

Se levantarán:

- `mysql_eventos`: contenedor de base de datos MySQL
- `redis_cache`: contenedor Redis
- `pig_container`: contenedor con Apache Pig

### 5. Ejecuta el programa principal

```bash
python main.py
```

Desde el menú podrás:

- Ejecutar scraping desde Waze
- Consultar la base de datos
- Simular tráfico y evaluar caché
- Ejecutar procesamiento distribuido con Pig
- Ver resultados y gráficos

---

## Procesamiento con Apache Pig

Se ejecutan automáticamente dos scripts Pig:

- `test.pig`: agrupa eventos por **tipo y calle**.
- `test_hora.pig`: agrupa eventos por **hora** de ocurrencia.

Los resultados se guardan en:

- `data/output_tipo_calle.xlsx`
- `data/output_por_hora.xlsx`

Los gráficos resultantes son:

- `distribucion_tipos_evento.png`
- `evolucion_eventos_por_hora.png`

---

## Estructura del Repositorio

```
./
    .env
    .gitattributes
    chromedriver.exe
    curva_cache_20250430_171836.png
    db.py
    distribucion_tipos_evento.png
    docker-compose.yml
    Dockerfile.pig
    estructura_proyecto.txt
    evolucion_eventos_por_hora.png
    funciones.py
    listar_archivos.py
    main.py
    pig_processor.py
    prueba.py
    README.md
    requirements.txt
    resultados_cache.xlsx
    resumen_cache_20250430_171836.png
    scraper.py
    start_hadoop.sh
    trafico.py
    .ipynb_checkpoints/
        Tarea1-checkpoint.ipynb
    data/
        eventos.csv
        eventos.xlsx
        output_por_hora.csv
        output_por_hora.xlsx
        output_por_tipo.csv.rar
        output_tipo_calle.csv
        output_tipo_calle.xlsx
        test.pig
        test.pig.log
        test_hadoop.pig
        test_hora.pig
        test_hora.pig.log
        test_hora_hadoop.pig
        output_por_hora/
            .part-r-00000.crc
            ._SUCCESS.crc
            part-r-00000
            _SUCCESS
        output_tipo_calle/
            .part-r-00000.crc
            ._SUCCESS.crc
            part-r-00000
            _SUCCESS
    hadoop_conf/
        core-site.xml
        hadoop-env.sh
        hdfs-site.xml
        mapred-site.xml
        yarn-site.xml
    informe/
        main.tex
    logs/
        scraping.log
    mysql/
        init.sql
    __pycache__/
        db.cpython-311.pyc
        db.cpython-312.pyc
        db.cpython-313.pyc
        funciones.cpython-312.pyc
        funciones.cpython-313.pyc
        pig_processor.cpython-312.pyc
        pig_processor.cpython-313.pyc
        scraper.cpython-311.pyc
        scraper.cpython-312.pyc
        scraper.cpython-313.pyc
        trafico.cpython-312.pyc
        trafico.cpython-313.pyc

```

---

## Resultados de la Entrega 2

Se generaron:

| Agrupación     | Archivo Excel                  | Imagen generada                   |
|----------------|--------------------------------|-----------------------------------|
| Tipo y Calle   | `output_tipo_calle.xlsx`       | `distribucion_tipos_evento.png`   |
| Hora del día   | `output_por_hora.xlsx`         | `evolucion_eventos_por_hora.png`  |

> Ambos análisis permiten visualizar tendencias de tráfico en distintos contextos.

---

## Enlaces

- [Repositorio GitHub](https://github.com/vixonp/Entregable-2-proyecto-SSDD.git)
- [Entrega 1 README](./README.md)
- [Informe LaTeX (PDF)](./tarea_2_Sistemas_Distribuidos)

---

## Notas

- El contenedor `pig_container` debe estar corriendo antes de ejecutar el procesamiento.
- Si los archivos de salida no se generan, verifica los logs en `data/*.log`.
- Para ejecutar los scripts Pig manualmente:
  
```bash
docker exec -it pig_container bash
pig -x local /data/test.pig
pig -x local /data/test_hora.pig
```

---
