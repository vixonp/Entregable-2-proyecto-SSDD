SET default_parallel 1;
SET opt.multiquery false;
SET pig.exec.reducers.max 1;

-- Cargar CSV completo
eventos = LOAD '/data/eventos.csv' USING PigStorage(',') AS (
    id:int,
    tipo:chararray,
    descripcion:chararray,
    lat:float,
    lon:float,
    fecha_extraccion:chararray,
    cuadrante:int,
    calle:chararray
);

-- Filtrar eventos con fecha válida
eventos_filtrados = FILTER eventos BY fecha_extraccion IS NOT NULL AND fecha_extraccion != '';

-- Separar la hora de la fecha
eventos_hora = FOREACH eventos_filtrados GENERATE 
    FLATTEN(STRSPLIT(fecha_extraccion, ' ')) AS (fecha_str:chararray, hora_str:chararray);

-- ⚠️ Validar que la hora tenga formato mínimo "HH"
eventos_validos = FILTER eventos_hora BY hora_str IS NOT NULL AND SIZE(hora_str) >= 2;

-- Obtener solo la hora "HH"
horas = FOREACH eventos_validos GENERATE SUBSTRING(hora_str, 0, 2) AS hora;

-- Agrupar por hora
agrupado = GROUP horas BY hora;

-- Contar eventos por hora
conteo = FOREACH agrupado GENERATE 
    group AS hora,
    COUNT(horas) AS cantidad;

-- Guardar salida con extensión .csv
STORE conteo INTO '/data/output_por_hora' USING PigStorage('\t');


