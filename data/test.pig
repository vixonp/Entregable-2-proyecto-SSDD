SET default_parallel 1;
SET opt.multiquery false;
SET pig.exec.reducers.max 1;


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

eventos_filtrados = FILTER eventos BY tipo IS NOT NULL AND tipo != '';

agrupado = GROUP eventos_filtrados BY (tipo, calle);

conteo = FOREACH agrupado GENERATE 
    group.tipo AS tipo,
    group.calle AS calle,
    COUNT(eventos_filtrados) AS cantidad;

-- 🧪 Guardar en archivo .tmp plano, no en carpeta
STORE conteo INTO '/data/output_tipo_calle' USING PigStorage('\t');


