"""
TODAS las consultas SQL del sistema están en este archivo.

Cómo funciona:
    1. La ventana de login crea la conexión (ConexionPostgres o ConexionSqlServer).
    2. Con esa conexión se crea un objeto Consultas:   bd = Consultas(conexion)
    3. Las ventanas solo llaman funciones de aquí, por ejemplo:
           bd.clientes_consultar("juan")
           bd.clientes_insertar({"nombre": "...", "telefono": "...", ...})

Cada función:
    - arma el texto del SQL
    - pone un marcador (P) en cada lugar donde va un valor:  ? en SQL Server, %s en PostgreSQL
    - manda el SQL y los valores a conexion.Ejecutar_consulta(sql, parametros)
    - regresa la respuesta ya convertida a diccionario:
          {"estado": True,  "registros": [...]}          -> si fue SELECT
          {"estado": True,  "mensaje": "...", ...}        -> si fue INSERT / UPDATE / DELETE
          {"estado": False, "mensaje": "...", "error": "..."}  -> si algo falló
"""
import json

from seguridad import verificar_contrasena


class Consultas:

    def __init__(self, conexion):
        self.conexion = conexion
        # P es el marcador de parámetros del motor que se eligió en el login
        self.P = conexion.MARCADOR

    # ------------------------------------------------------------
    # Función base: TODAS las demás pasan por aquí
    # ------------------------------------------------------------
    def ejecutar(self, sql, parametros=None):
        respuesta = self.conexion.Ejecutar_consulta(sql, parametros)  # regresa texto JSON
        return json.loads(respuesta)                                   # texto JSON -> diccionario

    def siguiente_id(self, tabla, columna_id):
        """Las tablas no tienen autoincremento, así que el ID nuevo es el mayor + 1.
        (tabla y columna_id los escribe el programa, nunca el usuario)"""
        sql = f"SELECT COALESCE(MAX({columna_id}), 0) + 1 AS siguiente FROM {tabla}"
        respuesta = self.ejecutar(sql)
        return int(respuesta["registros"][0]["siguiente"])

    def cerrar(self):
        self.conexion.Cerrar_conexion()

    # ============================================================
    # LOGIN
    # ============================================================
    def iniciar_sesion(self, usuario, contrasena):
        """Regresa (datos_del_usuario, None) si entra, o (None, mensaje) si no."""
        P = self.P
        sql = f"SELECT id_usuario, usuario, contrasena, nombre FROM usuarios WHERE usuario = {P}"
        respuesta = self.ejecutar(sql, (usuario,))

        if not respuesta["estado"]:
            return None, "No se pudo leer la tabla usuarios. ¿Ya ejecutaste usuarios.sql?"
        if len(respuesta["registros"]) == 0:
            return None, "Usuario o contraseña incorrectos."

        fila = respuesta["registros"][0]
        if verificar_contrasena(contrasena, fila["contrasena"]):
            return fila, None
        return None, "Usuario o contraseña incorrectos."

    # ============================================================
    # CATÁLOGO: CATEGORÍAS
    # ============================================================
    def categorias_consultar(self, buscar=""):
        P = self.P
        sql = "SELECT id_categoria, nombre, descripcion FROM categorias"
        if buscar:
            sql += f" WHERE UPPER(nombre) LIKE UPPER({P})"
            sql += " ORDER BY id_categoria"
            return self.ejecutar(sql, (f"%{buscar}%",))
        sql += " ORDER BY id_categoria"
        return self.ejecutar(sql)

    def categorias_obtener(self, id_categoria):
        P = self.P
        sql = f"SELECT id_categoria, nombre, descripcion FROM categorias WHERE id_categoria = {P}"
        return self.ejecutar(sql, (id_categoria,))

    def categorias_insertar(self, datos):
        P = self.P
        nuevo_id = self.siguiente_id("categorias", "id_categoria")
        sql = f"INSERT INTO categorias (id_categoria, nombre, descripcion) VALUES ({P}, {P}, {P})"
        return self.ejecutar(sql, (nuevo_id, datos["nombre"], datos["descripcion"]))

    def categorias_actualizar(self, id_categoria, datos):
        P = self.P
        sql = f"UPDATE categorias SET nombre = {P}, descripcion = {P} WHERE id_categoria = {P}"
        return self.ejecutar(sql, (datos["nombre"], datos["descripcion"], id_categoria))

    def categorias_eliminar(self, id_categoria):
        P = self.P
        sql = f"DELETE FROM categorias WHERE id_categoria = {P}"
        return self.ejecutar(sql, (id_categoria,))

    # ============================================================
    # CATÁLOGO: PRODUCTOS
    # (al consultar se une con categorias para mostrar el nombre de la categoría)
    # ============================================================
    def productos_consultar(self, buscar=""):
        P = self.P
        sql = ("SELECT p.id_producto, p.nombre, c.nombre AS categoria, p.unidad_medida, "
               "p.precio_compra, p.precio_venta, p.stock_minimo "
               "FROM productos p "
               "INNER JOIN categorias c ON p.id_categoria = c.id_categoria")
        if buscar:
            sql += f" WHERE UPPER(p.nombre) LIKE UPPER({P})"
            sql += " ORDER BY p.id_producto"
            return self.ejecutar(sql, (f"%{buscar}%",))
        sql += " ORDER BY p.id_producto"
        return self.ejecutar(sql)

    def productos_obtener(self, id_producto):
        P = self.P
        sql = ("SELECT id_producto, nombre, id_categoria, unidad_medida, precio_compra, "
               f"precio_venta, stock_minimo FROM productos WHERE id_producto = {P}")
        return self.ejecutar(sql, (id_producto,))

    def productos_insertar(self, datos):
        P = self.P
        nuevo_id = self.siguiente_id("productos", "id_producto")
        sql = ("INSERT INTO productos (id_producto, nombre, id_categoria, unidad_medida, "
               "precio_compra, precio_venta, stock_minimo) "
               f"VALUES ({P}, {P}, {P}, {P}, {P}, {P}, {P})")
        return self.ejecutar(sql, (nuevo_id, datos["nombre"], datos["id_categoria"],
                                   datos["unidad_medida"], datos["precio_compra"],
                                   datos["precio_venta"], datos["stock_minimo"]))

    def productos_actualizar(self, id_producto, datos):
        P = self.P
        sql = (f"UPDATE productos SET nombre = {P}, id_categoria = {P}, unidad_medida = {P}, "
               f"precio_compra = {P}, precio_venta = {P}, stock_minimo = {P} "
               f"WHERE id_producto = {P}")
        return self.ejecutar(sql, (datos["nombre"], datos["id_categoria"], datos["unidad_medida"],
                                   datos["precio_compra"], datos["precio_venta"],
                                   datos["stock_minimo"], id_producto))

    def productos_eliminar(self, id_producto):
        P = self.P
        sql = f"DELETE FROM productos WHERE id_producto = {P}"
        return self.ejecutar(sql, (id_producto,))

    # ============================================================
    # CATÁLOGO: PROVEEDORES
    # ============================================================
    def proveedores_consultar(self, buscar=""):
        P = self.P
        sql = ("SELECT id_proveedor, nombre_empresa, contacto, telefono, correo, direccion "
               "FROM proveedores")
        if buscar:
            sql += f" WHERE UPPER(nombre_empresa) LIKE UPPER({P})"
            sql += " ORDER BY id_proveedor"
            return self.ejecutar(sql, (f"%{buscar}%",))
        sql += " ORDER BY id_proveedor"
        return self.ejecutar(sql)

    def proveedores_obtener(self, id_proveedor):
        P = self.P
        sql = ("SELECT id_proveedor, nombre_empresa, contacto, telefono, correo, direccion "
               f"FROM proveedores WHERE id_proveedor = {P}")
        return self.ejecutar(sql, (id_proveedor,))

    def proveedores_insertar(self, datos):
        P = self.P
        nuevo_id = self.siguiente_id("proveedores", "id_proveedor")
        sql = ("INSERT INTO proveedores (id_proveedor, nombre_empresa, contacto, telefono, "
               f"correo, direccion) VALUES ({P}, {P}, {P}, {P}, {P}, {P})")
        return self.ejecutar(sql, (nuevo_id, datos["nombre_empresa"], datos["contacto"],
                                   datos["telefono"], datos["correo"], datos["direccion"]))

    def proveedores_actualizar(self, id_proveedor, datos):
        P = self.P
        sql = (f"UPDATE proveedores SET nombre_empresa = {P}, contacto = {P}, telefono = {P}, "
               f"correo = {P}, direccion = {P} WHERE id_proveedor = {P}")
        return self.ejecutar(sql, (datos["nombre_empresa"], datos["contacto"], datos["telefono"],
                                   datos["correo"], datos["direccion"], id_proveedor))

    def proveedores_eliminar(self, id_proveedor):
        P = self.P
        sql = f"DELETE FROM proveedores WHERE id_proveedor = {P}"
        return self.ejecutar(sql, (id_proveedor,))

    # ============================================================
    # CATÁLOGO: CLIENTES
    # ============================================================
    def clientes_consultar(self, buscar=""):
        P = self.P
        sql = "SELECT id_cliente, nombre, telefono, correo, direccion FROM clientes"
        if buscar:
            sql += f" WHERE UPPER(nombre) LIKE UPPER({P})"
            sql += " ORDER BY id_cliente"
            return self.ejecutar(sql, (f"%{buscar}%",))
        sql += " ORDER BY id_cliente"
        return self.ejecutar(sql)

    def clientes_obtener(self, id_cliente):
        P = self.P
        sql = ("SELECT id_cliente, nombre, telefono, correo, direccion "
               f"FROM clientes WHERE id_cliente = {P}")
        return self.ejecutar(sql, (id_cliente,))

    def clientes_insertar(self, datos):
        P = self.P
        nuevo_id = self.siguiente_id("clientes", "id_cliente")
        sql = ("INSERT INTO clientes (id_cliente, nombre, telefono, correo, direccion) "
               f"VALUES ({P}, {P}, {P}, {P}, {P})")
        return self.ejecutar(sql, (nuevo_id, datos["nombre"], datos["telefono"],
                                   datos["correo"], datos["direccion"]))

    def clientes_actualizar(self, id_cliente, datos):
        P = self.P
        sql = (f"UPDATE clientes SET nombre = {P}, telefono = {P}, correo = {P}, direccion = {P} "
               f"WHERE id_cliente = {P}")
        return self.ejecutar(sql, (datos["nombre"], datos["telefono"], datos["correo"],
                                   datos["direccion"], id_cliente))

    def clientes_eliminar(self, id_cliente):
        P = self.P
        sql = f"DELETE FROM clientes WHERE id_cliente = {P}"
        return self.ejecutar(sql, (id_cliente,))

    # ============================================================
    # CATÁLOGO: EMPLEADOS
    # ============================================================
    def empleados_consultar(self, buscar=""):
        P = self.P
        sql = "SELECT id_empleado, nombre, puesto, telefono, fecha_ingreso FROM empleados"
        if buscar:
            sql += f" WHERE UPPER(nombre) LIKE UPPER({P})"
            sql += " ORDER BY id_empleado"
            return self.ejecutar(sql, (f"%{buscar}%",))
        sql += " ORDER BY id_empleado"
        return self.ejecutar(sql)

    def empleados_obtener(self, id_empleado):
        P = self.P
        sql = ("SELECT id_empleado, nombre, puesto, telefono, fecha_ingreso "
               f"FROM empleados WHERE id_empleado = {P}")
        return self.ejecutar(sql, (id_empleado,))

    def empleados_insertar(self, datos):
        P = self.P
        nuevo_id = self.siguiente_id("empleados", "id_empleado")
        sql = ("INSERT INTO empleados (id_empleado, nombre, puesto, telefono, fecha_ingreso) "
               f"VALUES ({P}, {P}, {P}, {P}, {P})")
        return self.ejecutar(sql, (nuevo_id, datos["nombre"], datos["puesto"],
                                   datos["telefono"], datos["fecha_ingreso"]))

    def empleados_actualizar(self, id_empleado, datos):
        P = self.P
        sql = (f"UPDATE empleados SET nombre = {P}, puesto = {P}, telefono = {P}, "
               f"fecha_ingreso = {P} WHERE id_empleado = {P}")
        return self.ejecutar(sql, (datos["nombre"], datos["puesto"], datos["telefono"],
                                   datos["fecha_ingreso"], id_empleado))

    def empleados_eliminar(self, id_empleado):
        P = self.P
        sql = f"DELETE FROM empleados WHERE id_empleado = {P}"
        return self.ejecutar(sql, (id_empleado,))

    # ============================================================
    # CATÁLOGO: ALMACENES
    # ============================================================
    def almacenes_consultar(self, buscar=""):
        P = self.P
        sql = "SELECT id_almacen, nombre, ubicacion FROM almacenes"
        if buscar:
            sql += f" WHERE UPPER(nombre) LIKE UPPER({P})"
            sql += " ORDER BY id_almacen"
            return self.ejecutar(sql, (f"%{buscar}%",))
        sql += " ORDER BY id_almacen"
        return self.ejecutar(sql)

    def almacenes_obtener(self, id_almacen):
        P = self.P
        sql = f"SELECT id_almacen, nombre, ubicacion FROM almacenes WHERE id_almacen = {P}"
        return self.ejecutar(sql, (id_almacen,))

    def almacenes_insertar(self, datos):
        P = self.P
        nuevo_id = self.siguiente_id("almacenes", "id_almacen")
        sql = f"INSERT INTO almacenes (id_almacen, nombre, ubicacion) VALUES ({P}, {P}, {P})"
        return self.ejecutar(sql, (nuevo_id, datos["nombre"], datos["ubicacion"]))

    def almacenes_actualizar(self, id_almacen, datos):
        P = self.P
        sql = f"UPDATE almacenes SET nombre = {P}, ubicacion = {P} WHERE id_almacen = {P}"
        return self.ejecutar(sql, (datos["nombre"], datos["ubicacion"], id_almacen))

    def almacenes_eliminar(self, id_almacen):
        P = self.P
        sql = f"DELETE FROM almacenes WHERE id_almacen = {P}"
        return self.ejecutar(sql, (id_almacen,))

    # ============================================================
    # DASHBOARD (las 5 consultas del entregable 2 + los totales)
    # No reciben valores del usuario, por eso no llevan marcadores.
    # Funcionan igual en SQL Server y PostgreSQL (no usan LIMIT ni TOP).
    # ============================================================

    # Totales: dinero vendido, dinero comprado, número de productos y de clientes
    def dashboard_totales(self):
        sql = ("SELECT "
               "(SELECT COALESCE(SUM(total), 0) FROM ventas) AS ventas, "
               "(SELECT COALESCE(SUM(total), 0) FROM compras) AS compras, "
               "(SELECT COUNT(*) FROM productos) AS productos, "
               "(SELECT COUNT(*) FROM clientes) AS clientes")
        return self.ejecutar(sql)

    # Consulta 1 (básica): productos con su categoría -> un JOIN
    def dashboard_productos_categoria(self):
        sql = ("SELECT p.nombre, c.nombre AS categoria, p.precio_venta "
               "FROM productos p "
               "INNER JOIN categorias c ON p.id_categoria = c.id_categoria "
               "ORDER BY c.nombre, p.nombre")
        return self.ejecutar(sql)

    # Consulta 2 (agregación): dinero vendido por método de pago -> GROUP BY + SUM
    def dashboard_ventas_metodo_pago(self):
        sql = ("SELECT metodo_pago, SUM(total) AS total "
               "FROM ventas "
               "GROUP BY metodo_pago "
               "ORDER BY SUM(total) DESC")
        return self.ejecutar(sql)

    # Consulta 3 (varias tablas): dinero vendido por categoría -> detalle + producto + categoría
    def dashboard_ventas_categoria(self):
        sql = ("SELECT c.nombre AS categoria, SUM(d.subtotal) AS total "
               "FROM detalle_ventas d "
               "INNER JOIN productos p ON d.id_producto = p.id_producto "
               "INNER JOIN categorias c ON p.id_categoria = c.id_categoria "
               "GROUP BY c.nombre "
               "ORDER BY SUM(d.subtotal) DESC")
        return self.ejecutar(sql)

    # Consulta 4 (ranking): unidades vendidas por producto, de mayor a menor
    # (en la pantalla se muestran solo los primeros 5)
    def dashboard_top_productos(self):
        sql = ("SELECT p.nombre, SUM(d.cantidad) AS unidades "
               "FROM detalle_ventas d "
               "INNER JOIN productos p ON d.id_producto = p.id_producto "
               "GROUP BY p.id_producto, p.nombre "
               "ORDER BY SUM(d.cantidad) DESC")
        return self.ejecutar(sql)

    # Consulta 5 (avanzada): productos cuya existencia total es menor a su stock mínimo
    #   LEFT JOIN  -> incluye productos que no tienen ningún registro en inventario
    #   COALESCE   -> si no hay inventario, la suma vale 0 en lugar de NULL
    #   HAVING     -> filtra DESPUÉS de sumar (WHERE no puede usar SUM)
    def dashboard_stock_bajo(self):
        sql = ("SELECT p.id_producto, p.nombre, p.stock_minimo, "
               "COALESCE(SUM(i.cantidad_actual), 0) AS existencia "
               "FROM productos p "
               "LEFT JOIN inventario i ON i.id_producto = p.id_producto "
               "GROUP BY p.id_producto, p.nombre, p.stock_minimo "
               "HAVING COALESCE(SUM(i.cantidad_actual), 0) < p.stock_minimo "
               "ORDER BY existencia")
        return self.ejecutar(sql)

    # Extra para la gráfica de línea: total vendido por día
    def dashboard_ventas_por_fecha(self):
        sql = ("SELECT fecha, SUM(total) AS total "
               "FROM ventas "
               "GROUP BY fecha "
               "ORDER BY fecha")
        return self.ejecutar(sql)
