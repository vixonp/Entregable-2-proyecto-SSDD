CREATE TABLE IF NOT EXISTS eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(50),
    descripcion TEXT,
    lat DOUBLE,
    lon DOUBLE,
    fecha_extraccion DATETIME,
    cuadrante VARCHAR(20)
);
