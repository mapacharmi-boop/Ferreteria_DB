-- =====================================================
-- Script PostgreSQL - Sistema de Inventario Ferreteria - Hecho por Arturo Sánchez Encina
-- CREATE DATABASE ferreteria_db;
-- =====================================================

-- ---------- Creacion de tablas ----------

-- ===== Modulo de catalogo =====
CREATE TABLE categorias (
    id_categoria INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(150) NOT NULL,
    CONSTRAINT pk_categorias PRIMARY KEY (id_categoria),
    CONSTRAINT uq_categorias_nombre UNIQUE (nombre),
    CONSTRAINT ck_categorias_nombre CHECK (LENGTH(TRIM(nombre)) > 0)
);

CREATE TABLE productos (
    id_producto INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    id_categoria INT NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    precio_compra DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_minimo INT NOT NULL DEFAULT 0,
    CONSTRAINT pk_productos PRIMARY KEY (id_producto),
    CONSTRAINT fk_productos_id_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    CONSTRAINT uq_productos_nombre UNIQUE (nombre),
    CONSTRAINT ck_productos_unidad CHECK (unidad_medida IN ('pieza', 'caja', 'cubeta', 'rollo', 'metro', 'kilogramo', 'litro', 'paquete', 'juego')),
    CONSTRAINT ck_productos_precio_compra CHECK (precio_compra > 0),
    CONSTRAINT ck_productos_precio_venta CHECK (precio_venta >= precio_compra),
    CONSTRAINT ck_productos_stock_minimo CHECK (stock_minimo >= 0)
);

-- ===== Modulo de compras =====
CREATE TABLE proveedores (
    id_proveedor INT NOT NULL,
    nombre_empresa VARCHAR(100) NOT NULL,
    contacto VARCHAR(80) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(80) NOT NULL,
    direccion VARCHAR(150) NOT NULL,
    CONSTRAINT pk_proveedores PRIMARY KEY (id_proveedor),
    CONSTRAINT uq_proveedores_empresa UNIQUE (nombre_empresa),
    CONSTRAINT ck_proveedores_telefono CHECK (LENGTH(telefono) >= 10),
    CONSTRAINT ck_proveedores_correo CHECK (correo LIKE '%_@_%._%')
);

-- ===== Modulo de ventas =====
CREATE TABLE clientes (
    id_cliente INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(80) NOT NULL,
    direccion VARCHAR(150) NOT NULL,
    CONSTRAINT pk_clientes PRIMARY KEY (id_cliente),
    CONSTRAINT ck_clientes_nombre CHECK (LENGTH(TRIM(nombre)) > 0),
    CONSTRAINT ck_clientes_telefono CHECK (LENGTH(telefono) >= 10),
    CONSTRAINT ck_clientes_correo CHECK (correo LIKE '%_@_%._%')
);

CREATE TABLE empleados (
    id_empleado INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    puesto VARCHAR(50) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT pk_empleados PRIMARY KEY (id_empleado),
    CONSTRAINT ck_empleados_nombre CHECK (LENGTH(TRIM(nombre)) > 0),
    CONSTRAINT ck_empleados_telefono CHECK (LENGTH(telefono) >= 10),
    CONSTRAINT ck_empleados_fecha_ingreso CHECK (fecha_ingreso >= '2000-01-01')
);

-- ===== Modulo de inventario =====
CREATE TABLE almacenes (
    id_almacen INT NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    ubicacion VARCHAR(150) NOT NULL,
    CONSTRAINT pk_almacenes PRIMARY KEY (id_almacen),
    CONSTRAINT uq_almacenes_nombre UNIQUE (nombre)
);

-- ===== Modulo de compras (movimientos) =====
CREATE TABLE compras (
    id_compra INT NOT NULL,
    id_proveedor INT NOT NULL,
    id_empleado INT NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    total DECIMAL(10,2) NOT NULL DEFAULT 0,
    CONSTRAINT pk_compras PRIMARY KEY (id_compra),
    CONSTRAINT fk_compras_id_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
    CONSTRAINT fk_compras_id_empleado FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    CONSTRAINT ck_compras_total CHECK (total >= 0),
    CONSTRAINT ck_compras_fecha CHECK (fecha >= '2020-01-01')
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
    CONSTRAINT fk_detalle_compras_id_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    CONSTRAINT uq_detalle_compras_producto UNIQUE (id_compra, id_producto),
    CONSTRAINT ck_detalle_compras_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_detalle_compras_precio CHECK (precio_unitario > 0),
    CONSTRAINT ck_detalle_compras_subtotal CHECK (subtotal = cantidad * precio_unitario)
);

-- ===== Modulo de ventas (movimientos) =====
CREATE TABLE ventas (
    id_venta INT NOT NULL,
    id_cliente INT NOT NULL,
    id_empleado INT NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    total DECIMAL(10,2) NOT NULL DEFAULT 0,
    metodo_pago VARCHAR(20) NOT NULL DEFAULT 'Efectivo',
    CONSTRAINT pk_ventas PRIMARY KEY (id_venta),
    CONSTRAINT fk_ventas_id_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    CONSTRAINT fk_ventas_id_empleado FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    CONSTRAINT ck_ventas_total CHECK (total >= 0),
    CONSTRAINT ck_ventas_metodo_pago CHECK (metodo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia')),
    CONSTRAINT ck_ventas_fecha CHECK (fecha >= '2020-01-01')
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
    CONSTRAINT fk_detalle_ventas_id_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    CONSTRAINT uq_detalle_ventas_producto UNIQUE (id_venta, id_producto),
    CONSTRAINT ck_detalle_ventas_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_detalle_ventas_precio CHECK (precio_unitario > 0),
    CONSTRAINT ck_detalle_ventas_subtotal CHECK (subtotal = cantidad * precio_unitario)
);

-- ===== Modulo de inventario (movimientos) =====
CREATE TABLE inventario (
    id_inventario INT NOT NULL,
    id_producto INT NOT NULL,
    id_almacen INT NOT NULL,
    cantidad_actual INT NOT NULL DEFAULT 0,
    CONSTRAINT pk_inventario PRIMARY KEY (id_inventario),
    CONSTRAINT fk_inventario_id_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    CONSTRAINT fk_inventario_id_almacen FOREIGN KEY (id_almacen) REFERENCES almacenes(id_almacen),
    CONSTRAINT uq_inventario_producto_almacen UNIQUE (id_producto, id_almacen),
    CONSTRAINT ck_inventario_cantidad CHECK (cantidad_actual >= 0)
);

CREATE TABLE movimientos_inventario (
    id_movimiento INT NOT NULL,
    id_inventario INT NOT NULL,
    id_empleado INT NOT NULL,
    tipo_movimiento VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    motivo VARCHAR(100) NOT NULL,
    CONSTRAINT pk_movimientos_inventario PRIMARY KEY (id_movimiento),
    CONSTRAINT fk_movimientos_inventario_id_inventario FOREIGN KEY (id_inventario) REFERENCES inventario(id_inventario),
    CONSTRAINT fk_movimientos_inventario_id_empleado FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    CONSTRAINT ck_movimientos_tipo CHECK (tipo_movimiento IN ('entrada', 'salida', 'ajuste')),
    CONSTRAINT ck_movimientos_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_movimientos_motivo CHECK (LENGTH(TRIM(motivo)) > 0)
);

-- ---------- Insercion de datos ----------
-- Tablas maestras: 5 registros | Tablas de movimientos (detalle): 10 registros

-- categorias (5 registros)
INSERT INTO categorias (id_categoria, nombre, descripcion)
VALUES
    (1, 'Tornilleria', 'Tornillos, tuercas, rondanas y anclas'),
    (2, 'Pintura', 'Pinturas, brochas, rodillos y solventes'),
    (3, 'Herramienta', 'Herramienta manual y electrica'),
    (4, 'Plomeria', 'Tubos, conexiones y accesorios hidraulicos'),
    (5, 'Electricidad', 'Cables, contactos, apagadores y focos');

-- productos (5 registros)
INSERT INTO productos (id_producto, nombre, id_categoria, unidad_medida, precio_compra, precio_venta, stock_minimo)
VALUES
    (1, 'Tornillo autorroscante 1 pulg (caja 100)', 1, 'caja', 45.00, 75.00, 15),
    (2, 'Taladro percutor 1/2 pulg', 3, 'pieza', 620.00, 950.00, 5),
    (3, 'Pintura vinilica blanca 4L', 2, 'cubeta', 180.00, 265.00, 10),
    (4, 'Tubo PVC hidraulico 1/2 pulg x 6m', 4, 'pieza', 55.00, 89.00, 20),
    (5, 'Cable electrico cal. 12 (rollo 100m)', 5, 'rollo', 890.00, 1250.00, 4);

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

-- compras (10 registros)
INSERT INTO compras (id_compra, id_proveedor, id_empleado, fecha, total)
VALUES
    (1, 2, 4, '2026-08-03', 1350.00),
    (2, 5, 1, '2026-08-04', 6200.00),
    (3, 3, 4, '2026-08-06', 4500.00),
    (4, 4, 4, '2026-08-07', 2200.00),
    (5, 4, 1, '2026-08-10', 5340.00),
    (6, 1, 5, '2026-08-14', 900.00),
    (7, 3, 4, '2026-08-18', 1800.00),
    (8, 5, 1, '2026-08-21', 3100.00),
    (9, 4, 5, '2026-08-25', 1650.00),
    (10, 1, 4, '2026-08-28', 2670.00);

-- detalle_compras (10 registros)
INSERT INTO detalle_compras (id_detalle_compra, id_compra, id_producto, cantidad, precio_unitario, subtotal)
VALUES
    (1, 1, 1, 30, 45.00, 1350.00),
    (2, 2, 2, 10, 620.00, 6200.00),
    (3, 3, 3, 25, 180.00, 4500.00),
    (4, 4, 4, 40, 55.00, 2200.00),
    (5, 5, 5, 6, 890.00, 5340.00),
    (6, 6, 1, 20, 45.00, 900.00),
    (7, 7, 3, 10, 180.00, 1800.00),
    (8, 8, 2, 5, 620.00, 3100.00),
    (9, 9, 4, 30, 55.00, 1650.00),
    (10, 10, 5, 3, 890.00, 2670.00);

-- ventas (10 registros)
INSERT INTO ventas (id_venta, id_cliente, id_empleado, fecha, total, metodo_pago)
VALUES
    (1, 1, 2, '2026-09-01', 225.00, 'Efectivo'),
    (2, 2, 2, '2026-09-02', 950.00, 'Tarjeta'),
    (3, 3, 3, '2026-09-03', 530.00, 'Efectivo'),
    (4, 4, 3, '2026-09-04', 712.00, 'Transferencia'),
    (5, 5, 2, '2026-09-05', 1250.00, 'Tarjeta'),
    (6, 1, 3, '2026-09-08', 1068.00, 'Transferencia'),
    (7, 2, 2, '2026-09-09', 150.00, 'Efectivo'),
    (8, 5, 3, '2026-09-11', 1060.00, 'Tarjeta'),
    (9, 3, 2, '2026-09-15', 950.00, 'Efectivo'),
    (10, 4, 3, '2026-09-18', 2500.00, 'Transferencia');

-- detalle_ventas (10 registros)
INSERT INTO detalle_ventas (id_detalle_venta, id_venta, id_producto, cantidad, precio_unitario, subtotal)
VALUES
    (1, 1, 1, 3, 75.00, 225.00),
    (2, 2, 2, 1, 950.00, 950.00),
    (3, 3, 3, 2, 265.00, 530.00),
    (4, 4, 4, 8, 89.00, 712.00),
    (5, 5, 5, 1, 1250.00, 1250.00),
    (6, 6, 4, 12, 89.00, 1068.00),
    (7, 7, 1, 2, 75.00, 150.00),
    (8, 8, 3, 4, 265.00, 1060.00),
    (9, 9, 2, 1, 950.00, 950.00),
    (10, 10, 5, 2, 1250.00, 2500.00);

-- inventario (10 registros)
INSERT INTO inventario (id_inventario, id_producto, id_almacen, cantidad_actual)
VALUES
    (1, 1, 1, 30),
    (2, 1, 2, 12),
    (3, 2, 1, 4),
    (4, 2, 2, 6),
    (5, 3, 1, 3),
    (6, 3, 3, 5),
    (7, 4, 1, 15),
    (8, 4, 4, 0),
    (9, 5, 1, 2),
    (10, 5, 2, 0);

-- movimientos_inventario (10 registros)
INSERT INTO movimientos_inventario (id_movimiento, id_inventario, id_empleado, tipo_movimiento, cantidad, fecha, motivo)
VALUES
    (1, 1, 4, 'entrada', 30, '2026-08-03', 'Recepcion de la compra 1'),
    (2, 3, 1, 'entrada', 10, '2026-08-04', 'Recepcion de la compra 2'),
    (3, 5, 4, 'entrada', 25, '2026-08-06', 'Recepcion de la compra 3'),
    (4, 7, 4, 'entrada', 40, '2026-08-07', 'Recepcion de la compra 4'),
    (5, 1, 2, 'salida', 3, '2026-09-01', 'Venta 1 en mostrador'),
    (6, 3, 2, 'salida', 1, '2026-09-02', 'Venta 2 en mostrador'),
    (7, 1, 5, 'salida', 12, '2026-09-06', 'Traslado a Bodega Central'),
    (8, 2, 5, 'entrada', 12, '2026-09-06', 'Traslado desde Tienda Principal'),
    (9, 6, 4, 'ajuste', 2, '2026-09-10', 'Ajuste por conteo fisico'),
    (10, 8, 4, 'ajuste', 5, '2026-09-12', 'Baja de producto danado');
