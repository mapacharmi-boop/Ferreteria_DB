-- =====================================================
-- Tabla de usuarios para el inicio de sesión
-- Funciona igual en SQL Server y en PostgreSQL.
-- Ejecútalo en ferreteria_db DESPUÉS del script principal.
--
-- Usuario inicial:   admin
-- Contraseña:        admin123   (cámbiala después)
--
-- La contraseña NO se guarda en texto plano: se guarda un hash
-- PBKDF2-SHA256 con sal aleatoria (formato: algoritmo$iteraciones$sal$hash).
-- Para generar el hash de otra contraseña:  python app.py --hash NuevaClave
-- =====================================================

CREATE TABLE usuarios (
    id_usuario INT NOT NULL,
    usuario VARCHAR(50) NOT NULL,
    contrasena VARCHAR(200) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    CONSTRAINT pk_usuarios PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuarios_usuario UNIQUE (usuario)
);

INSERT INTO usuarios (id_usuario, usuario, contrasena, nombre)
VALUES
    (1, 'admin',
     'pbkdf2_sha256$200000$f98e12384705caf1d45b41f400f9c3b9$139ae3720d7fd1c7b37cf24bc882842cf21dedb35e8052bf9bc3e93626a0c031',
     'Administrador');
