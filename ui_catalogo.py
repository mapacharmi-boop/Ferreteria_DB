"""
Pantalla de un CATÁLOGO (tabla maestra) con su CRUD:
    Consultar  -> self.cargar()      -> bd.<tabla>_consultar()
    Insertar   -> self.insertar()    -> bd.<tabla>_insertar()
    Actualizar -> self.actualizar()  -> bd.<tabla>_obtener() y bd.<tabla>_actualizar()
    Eliminar   -> self.eliminar()    -> bd.<tabla>_eliminar()

El SQL NO está aquí, está en consultas.py. Esta pantalla solo:
    1. pide los datos con un formulario
    2. llama la función de consultas.py
    3. muestra el resultado
"""
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (QAbstractItemView, QComboBox, QDateEdit, QDialog, QDoubleSpinBox,
                             QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox, QPushButton,
                             QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

UNIDADES = ["pieza", "caja", "cubeta", "rollo", "metro", "kilogramo", "litro", "paquete", "juego"]


def dinero(valor):
    """Da formato de dinero:  1250.5 -> $1,250.50   y   -20 -> -$20.00"""
    valor = float(valor)
    signo = "-" if valor < 0 else ""
    return f"{signo}${abs(valor):,.2f}"


def definir_catalogos(bases):
    """Describe cada tabla maestra: qué columnas se ven, qué campos lleva el formulario
    y qué funciones de consultas.py se usan para cada operación del CRUD.

    columnas: (nombre_columna, encabezado, es_dinero)
    campos:   (nombre_columna, etiqueta, tipo)   tipo = texto | entero | decimal | fecha | categoria | unidad

    bases es un diccionario que dice con qué base de datos trabaja cada catálogo
    (se arma en ui_login.py según modulos.py), por ejemplo:
        bases["categorias"] -> Consultas conectada a PostgreSQL
        bases["clientes"]   -> Consultas conectada a SQL Server
    """
    return [
        dict(clave="categorias", titulo="Categorías", singular="categoría",
             descripcion="Líneas de productos de la ferretería.",
             id="id_categoria",
             columnas=[("id_categoria", "ID", False), ("nombre", "Nombre", False),
                       ("descripcion", "Descripción", False)],
             campos=[("nombre", "Nombre", "texto"), ("descripcion", "Descripción", "texto")],
             bd=bases["categorias"],
             consultar=bases["categorias"].categorias_consultar, obtener=bases["categorias"].categorias_obtener,
             insertar=bases["categorias"].categorias_insertar, actualizar=bases["categorias"].categorias_actualizar,
             eliminar=bases["categorias"].categorias_eliminar),

        dict(clave="productos", titulo="Productos", singular="producto",
             descripcion="Artículos a la venta con su precio y su stock mínimo.",
             id="id_producto",
             columnas=[("id_producto", "ID", False), ("nombre", "Nombre", False),
                       ("categoria", "Categoría", False), ("unidad_medida", "Unidad", False),
                       ("precio_compra", "P. compra", True), ("precio_venta", "P. venta", True),
                       ("stock_minimo", "Stock mín.", False)],
             campos=[("nombre", "Nombre", "texto"), ("id_categoria", "Categoría", "categoria"),
                     ("unidad_medida", "Unidad de medida", "unidad"),
                     ("precio_compra", "Precio de compra", "decimal"),
                     ("precio_venta", "Precio de venta", "decimal"),
                     ("stock_minimo", "Stock mínimo", "entero")],
             bd=bases["productos"],
             consultar=bases["productos"].productos_consultar, obtener=bases["productos"].productos_obtener,
             insertar=bases["productos"].productos_insertar, actualizar=bases["productos"].productos_actualizar,
             eliminar=bases["productos"].productos_eliminar),

        dict(clave="proveedores", titulo="Proveedores", singular="proveedor",
             descripcion="Empresas que surten a la ferretería.",
             id="id_proveedor",
             columnas=[("id_proveedor", "ID", False), ("nombre_empresa", "Empresa", False),
                       ("contacto", "Contacto", False), ("telefono", "Teléfono", False),
                       ("correo", "Correo", False), ("direccion", "Dirección", False)],
             campos=[("nombre_empresa", "Empresa", "texto"), ("contacto", "Contacto", "texto"),
                     ("telefono", "Teléfono", "texto"), ("correo", "Correo", "texto"),
                     ("direccion", "Dirección", "texto")],
             bd=bases["proveedores"],
             consultar=bases["proveedores"].proveedores_consultar, obtener=bases["proveedores"].proveedores_obtener,
             insertar=bases["proveedores"].proveedores_insertar, actualizar=bases["proveedores"].proveedores_actualizar,
             eliminar=bases["proveedores"].proveedores_eliminar),

        dict(clave="clientes", titulo="Clientes", singular="cliente",
             descripcion="Personas y empresas que compran.",
             id="id_cliente",
             columnas=[("id_cliente", "ID", False), ("nombre", "Nombre", False),
                       ("telefono", "Teléfono", False), ("correo", "Correo", False),
                       ("direccion", "Dirección", False)],
             campos=[("nombre", "Nombre", "texto"), ("telefono", "Teléfono", "texto"),
                     ("correo", "Correo", "texto"), ("direccion", "Dirección", "texto")],
             bd=bases["clientes"],
             consultar=bases["clientes"].clientes_consultar, obtener=bases["clientes"].clientes_obtener,
             insertar=bases["clientes"].clientes_insertar, actualizar=bases["clientes"].clientes_actualizar,
             eliminar=bases["clientes"].clientes_eliminar),

        dict(clave="empleados", titulo="Empleados", singular="empleado",
             descripcion="Personal de la ferretería.",
             id="id_empleado",
             columnas=[("id_empleado", "ID", False), ("nombre", "Nombre", False),
                       ("puesto", "Puesto", False), ("telefono", "Teléfono", False),
                       ("fecha_ingreso", "Ingreso", False)],
             campos=[("nombre", "Nombre", "texto"), ("puesto", "Puesto", "texto"),
                     ("telefono", "Teléfono", "texto"), ("fecha_ingreso", "Fecha de ingreso", "fecha")],
             bd=bases["empleados"],
             consultar=bases["empleados"].empleados_consultar, obtener=bases["empleados"].empleados_obtener,
             insertar=bases["empleados"].empleados_insertar, actualizar=bases["empleados"].empleados_actualizar,
             eliminar=bases["empleados"].empleados_eliminar),

        dict(clave="almacenes", titulo="Almacenes", singular="almacén",
             descripcion="Tiendas y bodegas donde se guarda la mercancía.",
             id="id_almacen",
             columnas=[("id_almacen", "ID", False), ("nombre", "Nombre", False),
                       ("ubicacion", "Ubicación", False)],
             campos=[("nombre", "Nombre", "texto"), ("ubicacion", "Ubicación", "texto")],
             bd=bases["almacenes"],
             consultar=bases["almacenes"].almacenes_consultar, obtener=bases["almacenes"].almacenes_obtener,
             insertar=bases["almacenes"].almacenes_insertar, actualizar=bases["almacenes"].almacenes_actualizar,
             eliminar=bases["almacenes"].almacenes_eliminar),
    ]


def mostrar_error(padre, titulo, respuesta):
    """Muestra el error que regresó Ejecutar_consulta."""
    texto = respuesta.get("mensaje", "Ocurrió un error")
    if respuesta.get("tipo") == "IntegrityError":
        texto += ("\n\nPuede ser que el registro esté en uso en otra tabla (llave foránea), "
                  "que un dato esté repetido o que no cumpla una regla (CHECK).")
    caja = QMessageBox(padre)
    caja.setIcon(QMessageBox.Icon.Warning)
    caja.setWindowTitle(titulo)
    caja.setText(texto)
    caja.setDetailedText(str(respuesta.get("error", "")))
    caja.exec()


# ============================================================
# PÁGINA DEL CATÁLOGO
# ============================================================
class PaginaCatalogo(QWidget):

    def __init__(self, bd, cfg):
        super().__init__()
        self.bd = bd
        self.cfg = cfg

        v = QVBoxLayout(self)
        v.setContentsMargins(28, 24, 28, 24)
        v.setSpacing(12)

        # Título y, a la derecha, en qué base de datos se guarda este catálogo
        fila = QHBoxLayout()
        titulo = QLabel(cfg["titulo"].upper())
        titulo.setObjectName("titulo")
        fila.addWidget(titulo)
        fila.addStretch()
        motor = QLabel(f"● SE GUARDA EN {bd.motor.upper()}")
        motor.setObjectName("pastilla")
        fila.addWidget(motor)
        v.addLayout(fila)
        sub = QLabel(cfg["descripcion"])
        sub.setObjectName("subtitulo")
        v.addWidget(sub)

        # Barra de herramientas: buscador + botones del CRUD
        barra = QHBoxLayout()
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText("Buscar por nombre...")
        self.buscar.textChanged.connect(self.cargar)      # busca mientras escribes
        barra.addWidget(self.buscar, 1)
        barra.addSpacing(12)
        self.b_insertar = self.boton("+ INSERTAR", "primario", self.insertar)
        self.b_actualizar = self.boton("ACTUALIZAR", "", self.actualizar)
        self.b_eliminar = self.boton("ELIMINAR", "peligro", self.eliminar)
        barra.addWidget(self.b_insertar)
        barra.addWidget(self.b_actualizar)
        barra.addWidget(self.b_eliminar)
        v.addLayout(barra)

        # Tabla con los registros
        self.tabla = QTableWidget(0, len(cfg["columnas"]))
        self.tabla.setHorizontalHeaderLabels([c[1].upper() for c in cfg["columnas"]])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(36)
        # cada columna se ajusta a su contenido y la 1 (nombre) ocupa el espacio que sobra
        encabezado = self.tabla.horizontalHeader()
        encabezado.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        encabezado.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.doubleClicked.connect(self.actualizar)   # doble clic = actualizar
        v.addWidget(self.tabla, 1)

        self.pie = QLabel("")
        self.pie.setObjectName("seccion")
        v.addWidget(self.pie)

    def boton(self, texto, estilo, accion):
        b = QPushButton(texto)
        b.setObjectName(estilo)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(accion)
        return b

    def id_seleccionado(self):
        """ID del renglón seleccionado (o None si no hay)."""
        fila = self.tabla.currentRow()
        if fila < 0 or not self.tabla.selectionModel().hasSelection():
            return None
        return int(self.tabla.item(fila, 0).text())

    # ---------- CONSULTAR ----------
    def cargar(self):
        respuesta = self.cfg["consultar"](self.buscar.text().strip())   # SELECT
        if not respuesta["estado"]:
            mostrar_error(self, "No se pudo consultar", respuesta)
            return
        registros = respuesta["registros"]

        self.tabla.setRowCount(len(registros))
        for i, registro in enumerate(registros):
            for j, (columna, _, es_dinero) in enumerate(self.cfg["columnas"]):
                valor = registro[columna]
                if es_dinero:
                    texto = dinero(valor)                 # 45.5 -> $45.50
                elif columna == "fecha_ingreso":
                    texto = str(valor)[:10]               # solo AAAA-MM-DD
                else:
                    texto = str(valor)
                celda = QTableWidgetItem(texto)
                if es_dinero:
                    celda.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tabla.setItem(i, j, celda)
        self.pie.setText(f"{len(registros)} REGISTRO(S)")

    # ---------- INSERTAR ----------
    def insertar(self):
        dialogo = DialogoRegistro(self, self.bd, self.cfg)
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return
        respuesta = self.cfg["insertar"](dialogo.datos())          # INSERT
        if respuesta["estado"]:
            QMessageBox.information(self, "Insertar", respuesta["mensaje"])
            self.cargar()
        else:
            mostrar_error(self, "No se pudo insertar", respuesta)

    # ---------- ACTUALIZAR ----------
    def actualizar(self):
        id_ = self.id_seleccionado()
        if id_ is None:
            QMessageBox.information(self, "Actualizar", "Primero selecciona un registro de la tabla.")
            return
        actual = self.cfg["obtener"](id_)                            # SELECT ... WHERE id = ?
        if not actual["estado"] or len(actual["registros"]) == 0:
            mostrar_error(self, "No se encontró el registro", actual)
            return
        dialogo = DialogoRegistro(self, self.bd, self.cfg, actual["registros"][0])
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return
        respuesta = self.cfg["actualizar"](id_, dialogo.datos())   # UPDATE
        if respuesta["estado"]:
            QMessageBox.information(self, "Actualizar", respuesta["mensaje"])
            self.cargar()
        else:
            mostrar_error(self, "No se pudo actualizar", respuesta)

    # ---------- ELIMINAR ----------
    def eliminar(self):
        id_ = self.id_seleccionado()
        if id_ is None:
            QMessageBox.information(self, "Eliminar", "Primero selecciona un registro de la tabla.")
            return
        nombre = self.tabla.item(self.tabla.currentRow(), 1).text()
        confirmacion = QMessageBox.question(
            self, "Eliminar", f"¿Eliminar {self.cfg['singular']} #{id_} ({nombre})?")
        if confirmacion != QMessageBox.StandardButton.Yes:
            return
        respuesta = self.cfg["eliminar"](id_)                       # DELETE
        if respuesta["estado"]:
            QMessageBox.information(self, "Eliminar", respuesta["mensaje"])
            self.cargar()
        else:
            mostrar_error(self, "No se pudo eliminar", respuesta)


# ============================================================
# FORMULARIO PARA INSERTAR / ACTUALIZAR
# ============================================================
class DialogoRegistro(QDialog):

    def __init__(self, padre, bd, cfg, actual=None):
        super().__init__(padre)
        self.cfg = cfg
        self.setWindowTitle(("Actualizar " if actual else "Insertar ") + cfg["singular"])
        self.setMinimumWidth(460)
        actual = actual or {}

        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        titulo = QLabel(("ACTUALIZAR " if actual else "NUEVO ") + cfg["singular"].upper())
        titulo.setObjectName("titulo")
        v.addWidget(titulo)
        v.addSpacing(8)

        # Un campo de captura por cada columna del formulario
        self.campos = []
        for columna, etiqueta, tipo in cfg["campos"]:
            valor = actual.get(columna)
            if tipo == "entero":
                campo = QSpinBox()
                campo.setRange(0, 1000000)
                campo.setValue(int(float(valor or 0)))
            elif tipo == "decimal":
                campo = QDoubleSpinBox()
                campo.setRange(0, 9999999)
                campo.setDecimals(2)
                campo.setPrefix("$ ")
                campo.setValue(float(valor or 0))
            elif tipo == "fecha":
                campo = QDateEdit()
                campo.setCalendarPopup(True)
                campo.setDisplayFormat("yyyy-MM-dd")
                fecha = QDate.fromString(str(valor)[:10], "yyyy-MM-dd") if valor else QDate.currentDate()
                campo.setDate(fecha)
            elif tipo == "unidad":
                campo = QComboBox()
                campo.addItems(UNIDADES)
                if valor:
                    campo.setCurrentText(str(valor))
            elif tipo == "categoria":
                # Lista con las categorías que existen (SELECT a la tabla categorias)
                campo = QComboBox()
                for c in bd.categorias_consultar()["registros"]:
                    campo.addItem(c["nombre"], c["id_categoria"])
                if valor is not None:
                    campo.setCurrentIndex(max(0, campo.findData(int(valor))))
            else:
                campo = QLineEdit("" if valor is None else str(valor))

            texto = QLabel(etiqueta.upper())
            texto.setObjectName("seccion")
            v.addWidget(texto)
            v.addWidget(campo)
            self.campos.append((columna, tipo, campo))

        self.error = QLabel("")
        self.error.setStyleSheet("color: #b42318;")
        v.addWidget(self.error)

        botones = QHBoxLayout()
        botones.addStretch()
        cancelar = QPushButton("CANCELAR")
        cancelar.clicked.connect(self.reject)
        guardar = QPushButton("GUARDAR")
        guardar.setObjectName("primario")
        guardar.clicked.connect(self.validar)
        botones.addWidget(cancelar)
        botones.addWidget(guardar)
        v.addLayout(botones)

    def validar(self):
        for columna, tipo, campo in self.campos:
            if tipo == "texto" and campo.text().strip() == "":
                self.error.setText("Llena todos los campos.")
                return
        self.accept()

    def datos(self):
        """Regresa lo capturado como diccionario {columna: valor}."""
        resultado = {}
        for columna, tipo, campo in self.campos:
            if tipo == "entero":
                resultado[columna] = campo.value()
            elif tipo == "decimal":
                resultado[columna] = round(campo.value(), 2)
            elif tipo == "fecha":
                resultado[columna] = campo.date().toString("yyyy-MM-dd")
            elif tipo == "unidad":
                resultado[columna] = campo.currentText()
            elif tipo == "categoria":
                resultado[columna] = campo.currentData()
            else:
                resultado[columna] = campo.text().strip()
        return resultado
