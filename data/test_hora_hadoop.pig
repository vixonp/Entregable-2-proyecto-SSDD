-- test_hora.pig

-- Cargar CSV completo
eventos = LOAD '/user/hadoop/input/eventos.csv' USING PigStorage(',') AS (

    id:int,
    tipo:chararray,
    descripcion:chararray,
    lat:float,
    lon:float,
    fecha_extraccion:chararray,
    cuadrante:int,
    calle:chararray
);

eventos_filtrados = FILTER eventos BY fecha_extraccion IS NOT NULL AND fecha_extraccion != '';

eventos_hora = FOREACH eventos_filtrados GENERATE 
    FLATTEN(STRSPLIT(fecha_extraccion, ' ')) AS (fecha_str:chararray, hora_str:chararray);

horas = FOREACH eventos_hora GENERATE SUBSTRING(hora_str, 0, 2) AS hora;

agrupado = GROUP horas BY hora;

conteo = FOREACH agrupado GENERATE 
    group AS hora,
    COUNT(horas) AS cantidad;

STORE conteo INTO '/user/hadoop/output_por_hora.csv' USING PigStorage(',');