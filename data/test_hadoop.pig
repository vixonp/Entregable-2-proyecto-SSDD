-- Cargar todas las líneas como texto plano
raw_lines = LOAD '/user/hadoop/input/eventos.csv' USING TextLoader();

-- Eliminar el header (filas que parten con "id,")
sin_encabezado = FILTER raw_lines BY NOT STARTSWITH($0, 'id,');

-- Separar por coma
campos = FOREACH sin_encabezado GENERATE FLATTEN(STRSPLIT($0, ',')) AS (
    id_str:chararray,
    tipo:chararray,
    descripcion:chararray,
    lat_str:chararray,
    lon_str:chararray,
    fecha_extraccion:chararray,
    cuadrante:chararray,
    calle:chararray
);

-- Convertir tipos
eventos_typed = FOREACH campos GENERATE
    (int)id_str AS id,
    tipo,
    descripcion,
    (float)lat_str AS lat,
    (float)lon_str AS lon,
    fecha_extraccion,
    cuadrante,
    calle;

-- Filtrar válidos
eventos_filtrados = FILTER eventos_typed BY tipo IS NOT NULL AND tipo != '';

-- Agrupar y contar
agrupado = GROUP eventos_filtrados BY (tipo, calle);
conteo = FOREACH agrupado GENERATE group.tipo, group.calle, COUNT(eventos_filtrados);

-- Guardar salida
STORE conteo INTO '/user/hadoop/output_tipo_calle.csv' USING PigStorage(',');

