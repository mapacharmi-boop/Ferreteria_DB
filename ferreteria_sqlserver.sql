-- =====================================================
-- Script SQL Server - Sistema de Inventario Ferreteria – Hecho por Arturo Sánchez Encina
-- CREATE DATABASE ferreteria_db;
-- USE ferreteria_db;
-- =====================================================

-- ---------- Creacion de tablas ----------

CREATE TABLE categorias (
    id_categoria INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(150) NOT NULL,
    CONSTRAINT pk_categorias PRIMARY KEY (id_categoria)
);

CREATE TABLE productos (
    id_producto INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    id_categoria INT NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    precio_compra DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_minimo INT NOT NULL,
    CONSTRAINT pk_productos PRIMARY KEY (id_producto),
    CONSTRAINT fk_productos_id_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
);

CREATE TABLE proveedores (
    id_proveedor INT NOT NULL,
    nombre_empresa VARCHAR(100) NOT NULL,
    contacto VARCHAR(80) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(80) NOT NULL,
    direccion VARCHAR(150) NOT NULL,
    CONSTRAINT pk_proveedores PRIMARY KEY (id_proveedor)
);

CREATE TABLE clientes (
    id_cliente INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(80) NOT NULL,
    direccion VARCHAR(150) NOT NULL,
    CONSTRAINT pk_clientes PRIMARY KEY (id_cliente)
);

CREATE TABLE empleados (
    id_empleado INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    puesto VARCHAR(50) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    fecha_ingreso DATE NOT NULL,
    CONSTRAINT pk_empleados PRIMARY KEY (id_empleado)
);

CREATE TABLE almacenes (
    id_almacen INT NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    ubicacion VARCHAR(150) NOT NULL,
    CONSTRAINT pk_almacenes PRIMARY KEY (id_almacen)
);

CREATE TABLE compras (
    id_compra INT NOT NULL,
    id_proveedor INT NOT NULL,
    id_empleado INT NOT NULL,
    fecha DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_compras PRIMARY KEY (id_compra),
    CONSTRAINT fk_compras_id_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
    CONSTRAINT fk_compras_id_empleado FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

CREATE TABLE detalle_compras (
    id_detalle_compra INT NOT NULL,
    id_compra INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_detalle_compras PRIMARY KEY (id_detalle_compra),
    CONSTRAINT fk_detalle_compras_id_compra FOREIGN KEY (id_compra) REFERENCES compras(id_compra),
    CONSTRAINT fk_detalle_compras_id_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE ventas (
    id_venta INT NOT NULL,
    id_cliente INT NOT NULL,
    id_empleado INT NOT NULL,
    fecha DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(20) NOT NULL,
    CONSTRAINT pk_ventas PRIMARY KEY (id_venta),
    CONSTRAINT fk_ventas_id_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    CONSTRAINT fk_ventas_id_empleado FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

CREATE TABLE detalle_ventas (
    id_detalle_venta INT NOT NULL,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_detalle_ventas PRIMARY KEY (id_detalle_venta),
    CONSTRAINT fk_detalle_ventas_id_venta FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
    CONSTRAINT fk_detalle_ventas_id_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE inventario (
    id_inventario INT NOT NULL,
    id_producto INT NOT NULL,
    id_almacen INT NOT NULL,
    cantidad_actual INT NOT NULL,
    CONSTRAINT pk_inventario PRIMARY KEY (id_inventario),
    CONSTRAINT fk_inventario_id_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    CONSTRAINT fk_inventario_id_almacen FOREIGN KEY (id_almacen) REFERENCES almacenes(id_almacen)
);

CREATE TABLE movimientos_inventario (
    id_movimiento INT NOT NULL,
    id_inventario INT NOT NULL,
    id_empleado INT NOT NULL,
    tipo_movimiento VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL,
    fecha DATE NOT NULL,
    motivo VARCHAR(100) NOT NULL,
    CONSTRAINT pk_movimientos_inventario PRIMARY KEY (id_movimiento),
    CONSTRAINT fk_movimientos_inventario_id_inventario FOREIGN KEY (id_inventario) REFERENCES inventario(id_inventario),
    CONSTRAINT fk_movimientos_inventario_id_empleado FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- ---------- Insercion de datos ----------

-- categorias (5 registros)
INSERT INTO categorias (id_categoria, nombre, descripcion)
VALUES
    (1, 'Tornilleria', 'Tornillos, tuercas, rondanas y anclas'),
    (2, 'Pintura', 'Pinturas, brochas, rodillos y solventes'),
    (3, 'Herramienta Manual', 'Martillos, desarmadores, llaves y pinzas'),
    (4, 'Plomeria', 'Tubos, conexiones y accesorios hidraulicos'),
    (5, 'Electricidad', 'Cables, contactos, apagadores y focos');

-- productos (5 registros)
INSERT INTO productos (id_producto, nombre, id_categoria, unidad_medida, precio_compra, precio_venta, stock_minimo)
VALUES
    (1, 'Tornillo autorroscante 1 pulg (caja 100)', 1, 'caja', 45.0, 75.0, 15),
    (2, 'Taladro percutor 1/2 pulg', 3, 'pieza', 620.0, 950.0, 5),
    (3, 'Pintura vinilica blanca 4L', 2, 'cubeta', 180.0, 265.0, 10),
    (4, 'Tubo PVC hidraulico 1/2 pulg x 6m', 4, 'pieza', 55.0, 89.0, 20),
    (5, 'Cable electrico cal. 12 (rollo 100m)', 5, 'rollo', 890.0, 1250.0, 4);

-- proveedores (5 registros)
INSERT INTO proveedores (id_proveedor, nombre_empresa, contacto, telefono, correo, direccion)
VALUES
    (1, 'Materiales y Ferreteria del Bajio SA', 'Luis Hernandez', '353-100-2211', 'ventas@mfbajio.mx', 'Av. Industrial 210, Jiquilpan'),
    (2, 'Distribuidora Tornillos del Centro', 'Mariana Ochoa', '353-100-3344', 'contacto@tornicentro.mx', 'Calle Hidalgo 88, Sahuayo'),
    (3, 'Pinturas y Acabados Michoacan', 'Jorge Campos', '353-100-5566', 'pedidos@pinturasmich.mx', 'Blvd. Lazaro Cardenas 45, Jiquilpan'),
    (4, 'Electricos y Plomeria del Valle', 'Ana Torres', '353-100-7788', 'atorres@electroplomeria.mx', 'Av. Morelos 12, Sahuayo'),
    (5, 'Herramientas Profesionales JR', 'Ricardo Nunez', '353-100-9900', 'rnunez@herramientasjr.mx', 'Priv. Reforma 30, Jiquilpan');

-- clientes (5 registros)
INSERT INTO clientes (id_cliente, nombre, telefono, correo, direccion)
VALUES
    (1, 'Constructora Del Toro', '353-200-1122', 'contacto@deltoro.mx', 'Av. Revolucion 300, Jiquilpan'),
    (2, 'Juan Ramirez Solis', '353-200-3344', 'juan.ramirez@mail.com', 'Calle Juarez 15, Jiquilpan'),
    (3, 'Talleres Mecanicos Lopez', '353-200-5566', 'tlrlopez@mail.com', 'Av. Zaragoza 77, Sahuayo'),
    (4, 'Maria Fernanda Castro', '353-200-7788', 'mf.castro@mail.com', 'Calle Allende 9, Jiquilpan'),
    (5, 'Remodelaciones Garcia e Hijos', '353-200-9900', 'remodgarcia@mail.com', 'Av. Guadalupe Victoria 60, Sahuayo');

-- empleados (5 registros)
INSERT INTO empleados (id_empleado, nombre, puesto, telefono, fecha_ingreso)
VALUES
    (1, 'Arturo Vega', 'Gerente', '353-300-1111', '2022-03-01'),
    (2, 'Sofia Mendoza', 'Vendedora', '353-300-2222', '2023-01-15'),
    (3, 'Daniel Ortiz', 'Cajero', '353-300-3333', '2023-06-10'),
    (4, 'Paola Reyes', 'Encargada de Almacen', '353-300-4444', '2021-11-20'),
    (5, 'Hector Guzman', 'Auxiliar de Almacen', '353-300-5555', '2024-02-05');

-- almacenes (5 registros)
INSERT INTO almacenes (id_almacen, nombre, ubicacion)
VALUES
    (1, 'Tienda Principal', 'Av. Insurgentes 100, Jiquilpan'),
    (2, 'Bodega Central', 'Carretera Jiquilpan-Sahuayo Km 2'),
    (3, 'Sucursal Norte', 'Av. Lazaro Cardenas 500, Jiquilpan'),
    (4, 'Sucursal Sur', 'Calle Morelos 220, Sahuayo'),
    (5, 'Bodega de Temporada', 'Camino Real 8, Jiquilpan');

-- compras (5 registros)
INSERT INTO compras (id_compra, id_proveedor, id_empleado, fecha, total)
VALUES
    (1, 1, 1, '2026-08-01', 500.0),
    (2, 2, 2, '2026-08-02', 2480.0),
    (3, 3, 3, '2026-08-03', 3600.0),
    (4, 4, 4, '2026-08-04', 825.0),
    (5, 5, 5, '2026-08-05', 2670.0);

-- detalle_compras (5 registros)
INSERT INTO detalle_compras (id_detalle_compra, id_compra, id_producto, cantidad, precio_unitario, subtotal)
VALUES
    (1, 1, 1, 10, 50.0, 500.0),
    (2, 2, 2, 4, 620.0, 2480.0),
    (3, 3, 3, 20, 180.0, 3600.0),
    (4, 4, 4, 15, 55.0, 825.0),
    (5, 5, 5, 3, 890.0, 2670.0);

-- ventas (5 registros)
INSERT INTO ventas (id_venta, id_cliente, id_empleado, fecha, total, metodo_pago)
VALUES
    (1, 1, 1, '2026-09-01', 225.0, 'Efectivo'),
    (2, 2, 2, '2026-09-02', 950.0, 'Tarjeta'),
    (3, 3, 3, '2026-09-03', 530.0, 'Efectivo'),
    (4, 4, 4, '2026-09-04', 712.0, 'Transferencia'),
    (5, 5, 5, '2026-09-05', 1250.0, 'Tarjeta');

-- detalle_ventas (5 registros)
INSERT INTO detalle_ventas (id_detalle_venta, id_venta, id_producto, cantidad, precio_unitario, subtotal)
VALUES
    (1, 1, 1, 3, 75.0, 225.0),
    (2, 2, 2, 1, 950.0, 950.0),
    (3, 3, 3, 2, 265.0, 530.0),
    (4, 4, 4, 8, 89.0, 712.0),
    (5, 5, 5, 1, 1250.0, 1250.0);

-- inventario (5 registros)
INSERT INTO inventario (id_inventario, id_producto, id_almacen, cantidad_actual)
VALUES
    (1, 1, 1, 40),
    (2, 1, 2, 6),
    (3, 2, 1, 15),
    (4, 2, 2, 60),
    (5, 3, 1, 3);

-- movimientos_inventario (5 registros)
INSERT INTO movimientos_inventario (id_movimiento, id_inventario, id_empleado, tipo_movimiento, cantidad, fecha, motivo)
VALUES
    (1, 1, 1, 'entrada', 8, '2026-09-01', 'Recepcion de compra a proveedor'),
    (2, 2, 2, 'salida', 3, '2026-09-02', 'Venta en mostrador'),
    (3, 3, 3, 'ajuste', 2, '2026-09-03', 'Ajuste por conteo fisico'),
    (4, 4, 4, 'entrada', 10, '2026-09-04', 'Traslado entre almacenes'),
    (5, 5, 5, 'salida', 1, '2026-09-05', 'Venta en mostrador');

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