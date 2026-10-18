# -*- coding: utf-8 -*-
"""
Ferretería - Sistema de Inventarios (interfaz gráfica con PyQt6)

Se ejecuta con:   python app.py
Los datos de conexión se leen del archivo .env (igual que en menu.py).
Antes de entrar por primera vez ejecuta usuarios.sql en la base de datos.

Estructura:
    1. Seguridad (hash de contraseñas)       -> generar_hash / verificar_contrasena
    2. Acceso a datos (usa conexion.py)      -> crear_conexion / BaseDatos / autenticar
    3. Configuración de las tablas maestras  -> CATALOGOS
    4. Interfaz gráfica                      -> login, ventana principal, páginas y diálogos
"""
import os
import sys
import json
import hmac
import hashlib

from dotenv import load_dotenv
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QAction, QColor, QFont, QFontDatabase, QPalette
from PyQt6.QtWidgets import (
    QAbstractItemView, QAbstractSpinBox, QApplication, QButtonGroup, QComboBox,
    QDateEdit, QDialog, QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QInputDialog, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPushButton, QSpinBox, QStackedWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from conexion import ConexionPostgres, ConexionSqlServer


# ============================================================
#  1. SEGURIDAD: HASH DE CONTRASEÑAS
#  La contraseña nunca se guarda en texto plano. Se guarda:
#  algoritmo$iteraciones$sal$hash   (PBKDF2 con SHA-256)
# ============================================================
def generar_hash(contrasena, iteraciones=200_000):
    sal = os.urandom(16)                                   # sal aleatoria de 16 bytes
    h = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), sal, iteraciones)
    return f"pbkdf2_sha256${iteraciones}${sal.hex()}${h.hex()}"


def verificar_contrasena(contrasena, guardado):
    try:
        _, iteraciones, sal, esperado = str(guardado).split("$")
        h = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"),
                                bytes.fromhex(sal), int(iteraciones))
        return hmac.compare_digest(h.hex(), esperado)      # comparación en tiempo constante
    except (ValueError, TypeError):
        return False


# ============================================================
#  2. ACCESO A DATOS
# ============================================================
MOTORES = ["PostgreSQL", "SQL Server"]


def crear_conexion(motor):
    """Crea y abre la conexión. Cada clase lee sus datos del .env en su constructor."""
    if motor == "SQL Server":
        conexion = ConexionSqlServer()
    else:
        conexion = ConexionPostgres()

    # Crear_conexion() devuelve None si falla; aquí lo convertimos en un error
    # para que la ventana de login muestre el mensaje.
    if conexion.Crear_conexion() is None:
        raise Exception(conexion.ERROR or f"No se pudo conectar a {motor}")
    return conexion


class BaseDatos:
    """Toda consulta de la app pasa por aquí y termina en conexion.Ejecutar_consulta."""

    def __init__(self, conexion):
        self.conexion = conexion
        self.P = conexion.MARCADOR           # "?" en SQL Server, "%s" en PostgreSQL

    def ejecutar(self, sql, parametros=None):
        try:
            return json.loads(self.conexion.Ejecutar_consulta(sql, parametros))
        except Exception as e:
            return {"estado": False, "mensaje": "No se pudo ejecutar la consulta",
                    "registros": [], "filas_afectadas": 0, "error": str(e)}

    def cerrar(self):
        self.conexion.Cerrar_conexion()


def autenticar(bd, usuario, contrasena):
    """Devuelve (registro_del_usuario, None), (None, None) si no coincide o (None, error)."""
    r = bd.ejecutar(
        f"SELECT id_usuario, usuario, contrasena, nombre FROM usuarios WHERE usuario = {bd.P}",
        (usuario,))
    if not r["estado"]:
        return None, r
    if not r["registros"]:
        return None, None
    fila = r["registros"][0]
    if verificar_contrasena(contrasena, fila["contrasena"]):
        return fila, None
    return None, None


def es_error_llave_foranea(datos):
    err = str(datos.get("error", "")).lower()
    return "foreign key" in err or "reference" in err or "conflicted" in err


# ============================================================
#  3. TABLAS MAESTRAS (CATÁLOGOS)
#  campos: (columna, etiqueta, tipo, opciones)
#     tipo: texto | entero | decimal | fecha | fk
#  cols:   (columna, encabezado, formato) para la tabla en pantalla
# ============================================================
CATALOGOS = [
    dict(clave="categorias", titulo="Categorías", singular="categoría", fem=True,
         desc="Líneas de productos de la ferretería",
         tabla="categorias", pk="id_categoria",
         campos=[("nombre", "Nombre", "texto", {"max": 50}),
                 ("descripcion", "Descripción", "texto", {"max": 150})],
         vista="SELECT c.id_categoria, c.nombre, c.descripcion FROM categorias c",
         cols=[("id_categoria", "ID", None), ("nombre", "Nombre", None),
               ("descripcion", "Descripción", None)],
         pk_q="c.id_categoria", nombre_q="c.nombre", orden="c.id_categoria"),

    dict(clave="productos", titulo="Productos", singular="producto",
         desc="Artículos a la venta con sus precios",
         tabla="productos", pk="id_producto",
         campos=[("nombre", "Nombre", "texto", {"max": 100}),
                 ("id_categoria", "Categoría", "fk",
                  {"sql": "SELECT id_categoria AS id, nombre FROM categorias ORDER BY nombre"}),
                 ("unidad_medida", "Unidad de medida (pieza, caja, rollo...)", "texto", {"max": 20}),
                 ("precio_compra", "Precio de compra", "decimal", {}),
                 ("precio_venta", "Precio de venta", "decimal", {}),
                 ("stock_minimo", "Stock mínimo", "entero", {})],
         vista=("SELECT p.id_producto, p.nombre, c.nombre AS categoria, p.unidad_medida, "
                "p.precio_compra, p.precio_venta, p.stock_minimo FROM productos p "
                "INNER JOIN categorias c ON p.id_categoria = c.id_categoria"),
         cols=[("id_producto", "ID", None), ("nombre", "Nombre", None),
               ("categoria", "Categoría", None), ("unidad_medida", "Unidad", None),
               ("precio_compra", "P. compra", "dinero"), ("precio_venta", "P. venta", "dinero"),
               ("stock_minimo", "Stock mín.", "entero")],
         pk_q="p.id_producto", nombre_q="p.nombre", orden="p.id_producto"),

    dict(clave="proveedores", titulo="Proveedores", singular="proveedor",
         desc="Empresas que surten a la ferretería",
         tabla="proveedores", pk="id_proveedor",
         campos=[("nombre_empresa", "Nombre de la empresa", "texto", {"max": 100}),
                 ("contacto", "Persona de contacto", "texto", {"max": 80}),
                 ("telefono", "Teléfono", "texto", {"max": 20}),
                 ("correo", "Correo", "texto", {"max": 80}),
                 ("direccion", "Dirección", "texto", {"max": 150})],
         vista=("SELECT pr.id_proveedor, pr.nombre_empresa, pr.contacto, pr.telefono, "
                "pr.correo, pr.direccion FROM proveedores pr"),
         cols=[("id_proveedor", "ID", None), ("nombre_empresa", "Empresa", None),
               ("contacto", "Contacto", None), ("telefono", "Teléfono", None),
               ("correo", "Correo", None), ("direccion", "Dirección", None)],
         pk_q="pr.id_proveedor", nombre_q="pr.nombre_empresa", orden="pr.id_proveedor"),

    dict(clave="clientes", titulo="Clientes", singular="cliente",
         desc="Personas y empresas que compran",
         tabla="clientes", pk="id_cliente",
         campos=[("nombre", "Nombre", "texto", {"max": 100}),
                 ("telefono", "Teléfono", "texto", {"max": 20}),
                 ("correo", "Correo", "texto", {"max": 80}),
                 ("direccion", "Dirección", "texto", {"max": 150})],
         vista=("SELECT c.id_cliente, c.nombre, c.telefono, c.correo, c.direccion "
                "FROM clientes c"),
         cols=[("id_cliente", "ID", None), ("nombre", "Nombre", None),
               ("telefono", "Teléfono", None), ("correo", "Correo", None),
               ("direccion", "Dirección", None)],
         pk_q="c.id_cliente", nombre_q="c.nombre", orden="c.id_cliente"),

    dict(clave="empleados", titulo="Empleados", singular="empleado",
         desc="Personal de la ferretería",
         tabla="empleados", pk="id_empleado",
         campos=[("nombre", "Nombre", "texto", {"max": 100}),
                 ("puesto", "Puesto", "texto", {"max": 50}),
                 ("telefono", "Teléfono", "texto", {"max": 20}),
                 ("fecha_ingreso", "Fecha de ingreso", "fecha", {})],
         vista=("SELECT e.id_empleado, e.nombre, e.puesto, e.telefono, e.fecha_ingreso "
                "FROM empleados e"),
         cols=[("id_empleado", "ID", None), ("nombre", "Nombre", None),
               ("puesto", "Puesto", None), ("telefono", "Teléfono", None),
               ("fecha_ingreso", "Ingreso", "fecha")],
         pk_q="e.id_empleado", nombre_q="e.nombre", orden="e.id_empleado"),

    dict(clave="almacenes", titulo="Almacenes", singular="almacén",
         desc="Tiendas y bodegas del inventario",
         tabla="almacenes", pk="id_almacen",
         campos=[("nombre", "Nombre", "texto", {"max": 80}),
                 ("ubicacion", "Ubicación", "texto", {"max": 150})],
         vista="SELECT a.id_almacen, a.nombre, a.ubicacion FROM almacenes a",
         cols=[("id_almacen", "ID", None), ("nombre", "Nombre", None),
               ("ubicacion", "Ubicación", None)],
         pk_q="a.id_almacen", nombre_q="a.nombre", orden="a.id_almacen"),
]


def genero(cfg):
    """Palabras en masculino o femenino según la tabla ("un producto" / "una categoría")."""
    f = cfg.get("fem", False)
    return dict(un="una" if f else "un", o="a" if f else "o", del_="de la" if f else "del",
                este="esta" if f else "este", ningun="ninguna" if f else "ningún")


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def formatear(v, fmt=None):
    if v is None or v == "None":
        return "—"
    if fmt == "dinero":
        return f"${num(v):,.2f}"
    if fmt == "entero":
        return f"{int(num(v)):,}"
    if fmt == "fecha":
        return str(v)[:10]
    return str(v)


# ============================================================
#  4. INTERFAZ GRÁFICA
#  Colores tomados del DESIGN.md (Obsidian / Neon Pulse / Mint Frost)
# ============================================================
OBSIDIANA = "#132322"
ABISMO = "#0e1a19"
CARBON = "#070f0f"
MENTA = "#edf7f5"
BLANCO = "#ffffff"
NIEBLA = "#d0d3d3"
PIEDRA = "#b2b6b4"
PIZARRA = "#828786"
GRAFITO = "#424f4f"
NEON = "#3ddc91"
SUSURRO = "#97ddbc"
AMARILLO = "#ffcd48"
ROJO = "#ff7b7b"

FUENTE = "Segoe UI"     # se reemplaza por Inter si está instalada (ver configurar_apariencia)

QSS = f"""
QWidget {{ color: {BLANCO}; }}
QLabel {{ background: transparent; }}
#fondo, QMainWindow {{ background: {OBSIDIANA}; }}

/* ---------- Menú principal (barra superior) ---------- */
QMenuBar {{ background: {ABISMO}; color: {NIEBLA}; padding: 4px 10px;
           border-bottom: 1px solid rgba(255,255,255,16); }}
QMenuBar::item {{ background: transparent; padding: 6px 12px; border-radius: 8px; }}
QMenuBar::item:selected {{ background: rgba(255,255,255,22); color: {BLANCO}; }}
QMenu {{ background: {ABISMO}; color: {BLANCO}; border: 1px solid rgba(255,255,255,28);
        border-radius: 10px; padding: 6px; }}
QMenu::item {{ padding: 8px 28px 8px 14px; border-radius: 6px; }}
QMenu::item:selected {{ background: {NEON}; color: {OBSIDIANA}; }}
QMenu::separator {{ height: 1px; background: rgba(255,255,255,22); margin: 6px 8px; }}
QMenu::right-arrow {{ width: 8px; height: 8px; }}

/* ---------- Barra lateral ---------- */
#sidebar {{ background: {ABISMO}; border-right: 1px solid rgba(255,255,255,14); }}
QPushButton#nav {{ background: transparent; color: {PIEDRA}; border: none; border-radius: 10px;
                  padding: 10px 14px; text-align: left; }}
QPushButton#nav:hover {{ background: rgba(255,255,255,14); color: {BLANCO}; }}
QPushButton#nav:checked {{ background: {NEON}; color: {OBSIDIANA}; }}
#tarjetaUsuario {{ background: {OBSIDIANA}; border-radius: 14px; }}
#avatar {{ background: {NEON}; color: {OBSIDIANA}; border-radius: 18px; }}

/* ---------- Botones (píldora) ---------- */
QPushButton {{ background: rgba(255,255,255,18); color: {BLANCO}; border: none;
              border-radius: 16px; padding: 8px 18px; }}
QPushButton:hover {{ background: rgba(255,255,255,30); }}
QPushButton#primario {{ background: {NEON}; color: {OBSIDIANA}; border: none;
                       border-radius: 18px; padding: 10px 22px; min-height: 18px; }}
QPushButton#primario:hover {{ background: #5be6a4; }}
QPushButton#primario:pressed {{ background: #31c47f; }}
QPushButton#primario:disabled {{ background: #2a3b3a; color: #5f6b6a; }}
QPushButton#fantasma {{ background: transparent; color: {BLANCO};
                       border: 1px solid rgba(255,255,255,90); border-radius: 18px; padding: 9px 20px; min-height: 18px; }}
QPushButton#fantasma:hover {{ border-color: {BLANCO}; background: rgba(255,255,255,14); }}
QPushButton#fantasma:disabled {{ color: {GRAFITO}; border-color: #2a3b3a; }}
QPushButton#peligro {{ background: transparent; color: {ROJO};
                      border: 1px solid rgba(255,123,123,120); border-radius: 18px; padding: 9px 20px; min-height: 18px; }}
QPushButton#peligro:hover {{ background: rgba(255,123,123,28); }}
QPushButton#peligro:disabled {{ color: {GRAFITO}; border-color: #2a3b3a; }}

/* ---------- Buscador ---------- */
QLineEdit#buscar {{ background: {ABISMO}; color: {BLANCO}; border: 1px solid rgba(255,255,255,30);
                   border-radius: 18px; padding: 9px 18px; min-height: 18px; }}
QLineEdit#buscar:focus {{ border-color: {NEON}; }}

/* ---------- Tarjetas ---------- */
#tarjetaClara {{ background: {MENTA}; border-radius: 20px; }}
#tarjetaClara QLabel {{ color: {OBSIDIANA}; }}
#tarjetaOscura {{ background: {ABISMO}; border-radius: 20px; border: 1px solid rgba(255,255,255,14); }}
#tarjetaOscura:hover {{ border-color: {NEON}; }}
#panelMarca {{ background: {ABISMO}; }}

/* ---------- Tabla ---------- */
QTableWidget {{ background: {BLANCO}; color: {OBSIDIANA}; border: 1px solid {NIEBLA};
               border-radius: 12px; gridline-color: transparent;
               alternate-background-color: #f6fbfa;
               selection-background-color: {SUSURRO}; selection-color: {OBSIDIANA}; }}
QTableWidget::item {{ padding: 0 10px; border-bottom: 1px solid #eef1f0; }}
QHeaderView::section {{ background: {BLANCO}; color: {PIZARRA}; border: none;
                       border-bottom: 1px solid {NIEBLA}; padding: 10px; }}
QTableCornerButton::section {{ background: {BLANCO}; border: none; }}

/* ---------- Barras de desplazamiento ---------- */
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 4px; }}
QScrollBar::handle:vertical {{ background: {NIEBLA}; border-radius: 3px; min-height: 30px; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 4px; }}
QScrollBar::handle:horizontal {{ background: {NIEBLA}; border-radius: 3px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

/* ---------- Formularios claros (login y diálogos) ---------- */
#tarjetaLogin, QDialog#dialogo {{ background: {MENTA}; }}
#tarjetaLogin {{ border-radius: 24px; }}
#tarjetaLogin QLabel, QDialog#dialogo QLabel {{ color: {OBSIDIANA}; }}
QLabel#etiquetaCampo {{ color: {GRAFITO}; }}
QLabel#error {{ color: #c0392b; }}
#tarjetaLogin QLineEdit, #tarjetaLogin QComboBox,
QDialog#dialogo QLineEdit, QDialog#dialogo QComboBox, QDialog#dialogo QSpinBox,
QDialog#dialogo QDoubleSpinBox, QDialog#dialogo QDateEdit {{
    background: {BLANCO}; color: {OBSIDIANA}; border: 1px solid {NIEBLA};
    border-radius: 10px; padding: 8px 12px; min-height: 22px;
    selection-background-color: {SUSURRO}; selection-color: {OBSIDIANA}; }}
#tarjetaLogin QLineEdit:focus, #tarjetaLogin QComboBox:focus,
QDialog#dialogo QLineEdit:focus, QDialog#dialogo QComboBox:focus, QDialog#dialogo QSpinBox:focus,
QDialog#dialogo QDoubleSpinBox:focus, QDialog#dialogo QDateEdit:focus {{ border: 1px solid {NEON}; }}
QDialog#dialogo QLineEdit:read-only {{ background: #e1ecea; color: {PIZARRA}; }}
QComboBox::drop-down, QDateEdit::drop-down {{ border: none; width: 26px; }}
QComboBox QAbstractItemView {{ background: {BLANCO}; color: {OBSIDIANA}; border: 1px solid {NIEBLA};
                              selection-background-color: {SUSURRO}; selection-color: {OBSIDIANA};
                              outline: none; padding: 4px; }}
QPushButton#fantasmaClaro {{ background: transparent; color: {OBSIDIANA};
                            border: 1px solid {OBSIDIANA}; border-radius: 18px; padding: 9px 20px; min-height: 18px; }}
QPushButton#fantasmaClaro:hover {{ background: rgba(19,35,34,18); }}

/* ---------- Calendario ---------- */
QCalendarWidget QWidget {{ background: {BLANCO}; color: {OBSIDIANA};
                          alternate-background-color: {MENTA}; }}
QCalendarWidget QToolButton {{ background: transparent; color: {OBSIDIANA}; padding: 4px 8px; }}
QCalendarWidget QAbstractItemView {{ selection-background-color: {NEON};
                                    selection-color: {OBSIDIANA}; }}

/* ---------- Mensajes ---------- */
QMessageBox, QInputDialog {{ background: {OBSIDIANA}; }}
QMessageBox QLabel, QInputDialog QLabel {{ color: {BLANCO}; }}
QInputDialog QSpinBox {{ background: {ABISMO}; color: {BLANCO}; border: 1px solid rgba(255,255,255,40);
                        border-radius: 8px; padding: 6px 10px; }}
QToolTip {{ background: {CARBON}; color: {BLANCO}; border: 1px solid {GRAFITO}; padding: 6px; }}
"""


# ---------- Ayudantes de interfaz ----------
def fuente(tam=14, peso=400, espaciado=0.0):
    f = QFont(FUENTE)
    f.setPixelSize(tam)
    f.setWeight({400: QFont.Weight.Normal, 500: QFont.Weight.Medium,
                 600: QFont.Weight.DemiBold}.get(peso, QFont.Weight.Normal))
    if espaciado:
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, espaciado)
    return f


def texto(t, tam=14, peso=400, color=None, espaciado=0.0, nombre=None, ajustar=False):
    lbl = QLabel(t)
    lbl.setFont(fuente(tam, peso, espaciado))
    if color:
        lbl.setStyleSheet(f"color: {color};")
    if nombre:
        lbl.setObjectName(nombre)
    lbl.setWordWrap(ajustar)
    return lbl


def ceja(t, color=PIZARRA):
    """Etiqueta pequeña en mayúsculas que va arriba de los títulos (eyebrow label)."""
    return texto(t.upper(), 11, 500, color, 1.2)


def boton(t, estilo="primario", al_clic=None, ancho=None):
    b = QPushButton(t)
    b.setObjectName(estilo)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setFont(fuente(14, 500 if estilo == "primario" else 400))
    if al_clic:
        b.clicked.connect(al_clic)
    if ancho:
        b.setMinimumWidth(ancho)
    return b


def mostrar_error(padre, titulo, datos, contexto=""):
    """Muestra el error de una consulta con un mensaje entendible."""
    if es_error_llave_foranea(datos):
        msg = ("La base de datos rechazó la operación por integridad referencial.\n\n"
               "Puede ser que el registro esté en uso en otras tablas (productos, ventas, "
               "compras, inventario...) o que el ID relacionado no exista.")
    else:
        msg = datos.get("mensaje", "Ocurrió un error")
    caja = QMessageBox(padre)
    caja.setIcon(QMessageBox.Icon.Warning)
    caja.setWindowTitle(titulo)
    caja.setText(f"{contexto}\n\n{msg}".strip())
    if datos.get("error"):
        caja.setDetailedText(str(datos["error"]))
    caja.exec()


def confirmar(padre, titulo, mensaje, texto_si="Eliminar"):
    caja = QMessageBox(padre)
    caja.setIcon(QMessageBox.Icon.Question)
    caja.setWindowTitle(titulo)
    caja.setText(mensaje)
    si = caja.addButton(texto_si, QMessageBox.ButtonRole.DestructiveRole)
    caja.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
    caja.exec()
    return caja.clickedButton() is si


# ============================================================
#  VENTANA DE INICIO DE SESIÓN
# ============================================================
class VentanaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.principal = None
        self.setObjectName("fondo")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setWindowTitle("Ferretería · Iniciar sesión")
        self.resize(1040, 640)
        self.setMinimumSize(860, 560)

        raiz = QHBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(self._panel_marca(), 5)
        raiz.addWidget(self._panel_formulario(), 4)

    def _panel_marca(self):
        panel = QFrame()
        panel.setObjectName("panelMarca")
        v = QVBoxLayout(panel)
        v.setContentsMargins(56, 48, 56, 48)

        marca = QHBoxLayout()
        punto = QLabel()
        punto.setFixedSize(12, 12)
        punto.setStyleSheet(f"background: {NEON}; border-radius: 6px;")
        marca.addWidget(punto)
        marca.addSpacing(10)
        marca.addWidget(texto("Ferretería", 17, 500, BLANCO))
        marca.addStretch()
        v.addLayout(marca)

        v.addStretch()
        v.addWidget(ceja("Sistema de inventarios", NEON))
        v.addSpacing(14)
        v.addWidget(texto("Controla tu inventario\nen un solo lugar.", 40, 500, BLANCO))
        v.addSpacing(16)
        v.addWidget(texto("Catálogos, existencias y movimientos de la ferretería, "
                          "conectados a SQL Server o PostgreSQL.", 16, 400, PIEDRA, ajustar=True))
        v.addSpacing(40)

        stats = QHBoxLayout()
        stats.setSpacing(48)
        for numero, etiqueta in (("6", "Catálogos"), ("2", "Motores de BD"), ("CRUD", "Completo")):
            col = QVBoxLayout()
            col.setSpacing(4)
            col.addWidget(texto(numero, 34, 500, NEON))
            col.addWidget(texto(etiqueta.upper(), 10, 400, PIZARRA, 1.2))
            stats.addLayout(col)
        stats.addStretch()
        v.addLayout(stats)
        v.addStretch()
        v.addWidget(texto("Ingeniería en Sistemas Computacionales · TecNM Jiquilpan", 12, 400, GRAFITO))
        return panel

    def _panel_formulario(self):
        contenedor = QWidget()
        v = QVBoxLayout(contenedor)
        v.setContentsMargins(40, 40, 40, 40)
        v.addStretch()

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaLogin")
        tarjeta.setFixedWidth(380)
        f = QVBoxLayout(tarjeta)
        f.setContentsMargins(36, 36, 36, 32)
        f.setSpacing(6)

        f.addWidget(ceja("Bienvenido", OBSIDIANA))
        f.addWidget(texto("Iniciar sesión", 26, 500, OBSIDIANA))
        f.addWidget(texto("Ingresa con tu usuario del sistema.", 14, 400, PIZARRA))
        f.addSpacing(18)

        self.motor = QComboBox()
        self.motor.addItems(MOTORES)
        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Ej. admin")
        self.clave = QLineEdit()
        self.clave.setPlaceholderText("••••••••")
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave.returnPressed.connect(self.entrar)
        self.usuario.returnPressed.connect(self.clave.setFocus)

        for etiqueta, campo in (("Base de datos", self.motor), ("Usuario", self.usuario),
                                ("Contraseña", self.clave)):
            f.addWidget(texto(etiqueta, 13, 500, nombre="etiquetaCampo"))
            campo.setFont(fuente(14))
            f.addWidget(campo)
            f.addSpacing(8)

        self.error = texto("", 13, 400, nombre="error", ajustar=True)
        self.error.hide()
        f.addWidget(self.error)
        f.addSpacing(6)

        self.b_entrar = boton("Iniciar sesión", "primario", self.entrar)
        self.b_entrar.setMinimumHeight(44)
        f.addWidget(self.b_entrar)

        v.addWidget(tarjeta, 0, Qt.AlignmentFlag.AlignHCenter)
        v.addStretch()
        return contenedor

    def _error(self, msg, detalle=""):
        self.error.setText(msg)
        self.error.setToolTip(detalle)
        self.error.show()
        self.b_entrar.setEnabled(True)
        self.b_entrar.setText("Iniciar sesión")

    def entrar(self):
        usuario = self.usuario.text().strip()
        clave = self.clave.text()
        motor = self.motor.currentText()
        if not usuario or not clave:
            self._error("Escribe tu usuario y tu contraseña.")
            return

        self.error.hide()
        self.b_entrar.setEnabled(False)
        self.b_entrar.setText(f"Conectando con {motor}...")
        QApplication.processEvents()

        try:
            conexion = crear_conexion(motor)
        except Exception as e:
            self._error(f"No se pudo conectar a {motor}. Revisa el archivo .env "
                        "y que el servidor esté encendido.", str(e))
            return

        bd = BaseDatos(conexion)
        registro, fallo = autenticar(bd, usuario, clave)
        if fallo:
            bd.cerrar()
            self._error("No se pudo consultar la tabla usuarios. "
                        "¿Ya ejecutaste usuarios.sql en esta base de datos?", fallo.get("error", ""))
            return
        if registro is None:
            bd.cerrar()
            self.clave.clear()
            self.clave.setFocus()
            self._error("Usuario o contraseña incorrectos.")
            return

        self.principal = VentanaPrincipal(bd, motor, registro, self)
        self.principal.show()
        self.hide()

    def reiniciar(self):
        self.clave.clear()
        self.error.hide()
        self.b_entrar.setEnabled(True)
        self.b_entrar.setText("Iniciar sesión")
        self.clave.setFocus()


# ============================================================
#  VENTANA PRINCIPAL
# ============================================================
class VentanaPrincipal(QMainWindow):
    def __init__(self, bd, motor, usuario, login):
        super().__init__()
        self.bd = bd
        self.motor = motor
        self.usuario = usuario
        self.login = login
        self._cerrando_sesion = False

        self.setWindowTitle("Ferretería · Sistema de Inventarios")
        self.resize(1320, 820)
        self.setMinimumSize(1060, 660)

        self.paginas = QStackedWidget()
        self.botones = {}
        self.crud = {}

        central = QWidget()
        central.setObjectName("fondo")
        raiz = QHBoxLayout(central)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(self._barra_lateral())

        self.inicio = PaginaInicio(self)
        self.paginas.addWidget(self.inicio)
        for cfg in CATALOGOS:
            pagina = PaginaCatalogo(self.bd, cfg)
            self.crud[cfg["clave"]] = pagina
            self.paginas.addWidget(pagina)
        raiz.addWidget(self.paginas, 1)

        self.setCentralWidget(central)
        self._menu_principal()
        self.ir("inicio")

    # ---------- MENÚ PRINCIPAL: Archivo · Catálogos · Ayuda ----------
    def _menu_principal(self):
        barra = self.menuBar()
        barra.setFont(fuente(14))

        archivo = barra.addMenu("&Archivo")
        a_inicio = QAction("Inicio", self)
        a_inicio.triggered.connect(lambda: self.ir("inicio"))
        archivo.addAction(a_inicio)
        archivo.addSeparator()
        a_sesion = QAction("Cerrar sesión", self)
        a_sesion.triggered.connect(self.cerrar_sesion)
        archivo.addAction(a_sesion)
        a_salir = QAction("Salir", self)
        a_salir.setShortcut("Ctrl+Q")
        a_salir.triggered.connect(self.close)
        archivo.addAction(a_salir)

        # Catálogos -> una opción por tabla maestra -> Insertar / Actualizar / Eliminar / Consultar
        catalogos = barra.addMenu("&Catálogos")
        for i, cfg in enumerate(CATALOGOS, 1):
            sub = catalogos.addMenu(cfg["titulo"])
            clave = cfg["clave"]
            for nombre, accion in (("Insertar", "insertar"), ("Actualizar", "actualizar"),
                                   ("Eliminar", "eliminar"), ("Consultar", "consultar")):
                act = QAction(nombre, self)
                if accion == "consultar":
                    act.setShortcut(f"Ctrl+{i}")
                act.triggered.connect(lambda _=False, k=clave, a=accion: self.accion_catalogo(k, a))
                sub.addAction(act)

        ayuda = barra.addMenu("A&yuda")
        a_acerca = QAction("Acerca de", self)
        a_acerca.triggered.connect(self.acerca_de)
        ayuda.addAction(a_acerca)

    def accion_catalogo(self, clave, accion):
        self.ir(clave)
        pagina = self.crud[clave]
        if accion == "insertar":
            pagina.insertar()
        elif accion == "actualizar":
            pagina.actualizar()
        elif accion == "eliminar":
            pagina.eliminar()
        else:
            pagina.buscar.setFocus()
            pagina.buscar.selectAll()

    # ---------- Barra lateral ----------
    def _barra_lateral(self):
        lateral = QFrame()
        lateral.setObjectName("sidebar")
        lateral.setFixedWidth(250)
        v = QVBoxLayout(lateral)
        v.setContentsMargins(18, 24, 18, 18)
        v.setSpacing(4)

        marca = QHBoxLayout()
        punto = QLabel()
        punto.setFixedSize(12, 12)
        punto.setStyleSheet(f"background: {NEON}; border-radius: 6px;")
        marca.addSpacing(6)
        marca.addWidget(punto)
        marca.addSpacing(8)
        marca.addWidget(texto("Ferretería", 17, 500, BLANCO))
        marca.addStretch()
        v.addLayout(marca)
        v.addSpacing(28)

        self.grupo = QButtonGroup(self)
        self.grupo.setExclusive(True)

        v.addWidget(self._etiqueta_lateral("General"))
        v.addWidget(self._boton_nav("inicio", "Inicio"))
        v.addSpacing(18)
        v.addWidget(self._etiqueta_lateral("Catálogos"))
        for cfg in CATALOGOS:
            v.addWidget(self._boton_nav(cfg["clave"], cfg["titulo"]))
        v.addStretch()

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaUsuario")
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(12, 12, 12, 12)
        nombre = str(self.usuario.get("nombre") or self.usuario.get("usuario"))
        iniciales = "".join(p[0] for p in nombre.split()[:2]).upper() or "U"
        avatar = texto(iniciales, 14, 600, nombre="avatar")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(avatar)
        datos = QVBoxLayout()
        datos.setSpacing(0)
        datos.addWidget(texto(nombre, 14, 500, BLANCO))
        datos.addWidget(texto(f"● {self.motor}", 12, 400, NEON))
        h.addLayout(datos, 1)
        v.addWidget(tarjeta)
        v.addSpacing(10)
        v.addWidget(boton("Cerrar sesión", "fantasma", self.cerrar_sesion))
        return lateral

    def _etiqueta_lateral(self, t):
        lbl = ceja(t, GRAFITO)
        lbl.setContentsMargins(14, 0, 0, 6)
        return lbl

    def _boton_nav(self, clave, titulo):
        b = QPushButton(titulo)
        b.setObjectName("nav")
        b.setCheckable(True)
        b.setFont(fuente(14))
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(lambda: self.ir(clave))
        self.grupo.addButton(b)
        self.botones[clave] = b
        return b

    # ---------- Navegación ----------
    def ir(self, clave):
        self.botones[clave].setChecked(True)
        if clave == "inicio":
            self.inicio.actualizar()
            self.paginas.setCurrentWidget(self.inicio)
        else:
            pagina = self.crud[clave]
            pagina.cargar()
            self.paginas.setCurrentWidget(pagina)

    def acerca_de(self):
        QMessageBox.about(self, "Acerca de",
                          "Ferretería · Sistema de Inventarios\n\n"
                          "Interfaz gráfica en PyQt6 con CRUD de las tablas maestras.\n"
                          f"Conectado a: {self.motor}")

    def cerrar_sesion(self):
        self._cerrando_sesion = True
        self.close()

    def closeEvent(self, evento):
        self.bd.cerrar()
        if self._cerrando_sesion:
            self.login.reiniciar()
            self.login.show()
        evento.accept()


# ============================================================
#  PÁGINA DE INICIO (resumen)
# ============================================================
class TarjetaDato(QFrame):
    """Tarjeta oscura con un número grande; al dar clic abre su catálogo."""

    def __init__(self, titulo, descripcion, al_clic):
        super().__init__()
        self.setObjectName("tarjetaOscura")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.al_clic = al_clic
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 22, 24, 22)
        v.setSpacing(4)
        v.addWidget(ceja(titulo, PIZARRA))
        self.numero = texto("—", 40, 500, NEON)
        v.addWidget(self.numero)
        v.addWidget(texto(descripcion, 13, 400, PIEDRA, ajustar=True))

    def mousePressEvent(self, evento):
        if evento.button() == Qt.MouseButton.LeftButton:
            self.al_clic()


class PaginaInicio(QWidget):
    def __init__(self, ventana):
        super().__init__()
        self.ventana = ventana
        v = QVBoxLayout(self)
        v.setContentsMargins(44, 36, 44, 36)
        v.setSpacing(6)

        nombre = str(ventana.usuario.get("nombre") or ventana.usuario.get("usuario"))
        v.addWidget(ceja("Panel general", NEON))
        v.addWidget(texto(f"Hola, {nombre}", 32, 500, BLANCO))
        v.addWidget(texto("Este es el resumen de los catálogos de la ferretería. "
                          "Da clic en una tarjeta para administrarlo.", 15, 400, PIEDRA))
        v.addSpacing(24)

        rejilla = QGridLayout()
        rejilla.setSpacing(16)
        self.tarjetas = {}
        for i, cfg in enumerate(CATALOGOS):
            t = TarjetaDato(cfg["titulo"], cfg["desc"],
                            lambda k=cfg["clave"]: self.ventana.ir(k))
            self.tarjetas[cfg["clave"]] = t
            rejilla.addWidget(t, i // 3, i % 3)
        v.addLayout(rejilla)
        v.addSpacing(24)

        # Tarjeta clara de acceso rápido
        rapido = QFrame()
        rapido.setObjectName("tarjetaClara")
        h = QHBoxLayout(rapido)
        h.setContentsMargins(32, 28, 32, 28)
        col = QVBoxLayout()
        col.setSpacing(4)
        col.addWidget(ceja("Acceso rápido", OBSIDIANA))
        col.addWidget(texto("¿Qué quieres registrar hoy?", 22, 500, OBSIDIANA))
        col.addWidget(texto("También puedes usar el menú Catálogos de la barra superior.",
                            14, 400, PIZARRA))
        h.addLayout(col, 1)
        for clave, etiqueta in (("productos", "+ Producto"), ("clientes", "+ Cliente"),
                                ("proveedores", "+ Proveedor")):
            h.addWidget(boton(etiqueta, "primario",
                              lambda _=False, k=clave: self.ventana.accion_catalogo(k, "insertar")))
        v.addWidget(rapido)
        v.addStretch()

    def actualizar(self):
        bd = self.ventana.bd
        for cfg in CATALOGOS:
            r = bd.ejecutar(f"SELECT COUNT(*) AS total FROM {cfg['tabla']}")
            valor = "—"
            if r["estado"] and r["registros"]:
                valor = formatear(r["registros"][0]["total"], "entero")
            self.tarjetas[cfg["clave"]].numero.setText(valor)


# ============================================================
#  PÁGINA DE CATÁLOGO (CRUD de una tabla maestra)
# ============================================================
class PaginaCatalogo(QWidget):
    def __init__(self, bd, cfg):
        super().__init__()
        self.bd = bd
        self.cfg = cfg
        self.g = genero(cfg)

        v = QVBoxLayout(self)
        v.setContentsMargins(44, 36, 44, 36)
        v.setSpacing(18)

        # Encabezado
        enc = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(4)
        col.addWidget(ceja("Catálogos · tabla maestra", NEON))
        col.addWidget(texto(cfg["titulo"], 32, 500, BLANCO))
        col.addWidget(texto(cfg["desc"], 15, 400, PIEDRA))
        enc.addLayout(col, 1)
        self.aviso = texto("", 14, 500)
        self.aviso.hide()
        enc.addWidget(self.aviso, 0, Qt.AlignmentFlag.AlignTop)
        v.addLayout(enc)

        # Barra de herramientas
        barra = QHBoxLayout()
        barra.setSpacing(10)
        self.buscar = QLineEdit()
        self.buscar.setObjectName("buscar")
        self.buscar.setFont(fuente(14))
        self.buscar.setPlaceholderText(f"Consultar {cfg['titulo'].lower()} por nombre o ID...")
        self.buscar.setClearButtonEnabled(True)
        self.buscar.setMinimumWidth(340)
        self._retraso = QTimer(self)
        self._retraso.setSingleShot(True)
        self._retraso.setInterval(250)
        self._retraso.timeout.connect(self.cargar)
        self.buscar.textChanged.connect(lambda _: self._retraso.start())
        barra.addWidget(self.buscar)
        barra.addWidget(boton("Refrescar", "fantasma", self.cargar))
        barra.addStretch()
        self.b_eliminar = boton("Eliminar", "peligro", lambda: self.eliminar())
        self.b_editar = boton("Actualizar", "fantasma", lambda: self.actualizar())
        self.b_nuevo = boton(f"+ Insertar {cfg['singular']}", "primario", self.insertar)
        barra.addWidget(self.b_eliminar)
        barra.addWidget(self.b_editar)
        barra.addWidget(self.b_nuevo)
        v.addLayout(barra)

        # Tarjeta clara con la tabla
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaClara")
        tv = QVBoxLayout(tarjeta)
        tv.setContentsMargins(20, 20, 20, 14)
        tv.setSpacing(10)

        self.tabla = QTableWidget(0, len(cfg["cols"]))
        self.tabla.setHorizontalHeaderLabels([c[1] for c in cfg["cols"]])
        self.tabla.setFont(fuente(14))
        self.tabla.horizontalHeader().setFont(fuente(13, 500))
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(42)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)
        self.tabla.setWordWrap(False)
        cab = self.tabla.horizontalHeader()
        cab.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        cab.setHighlightSections(False)
        cab.setStretchLastSection(True)
        self.tabla.itemSelectionChanged.connect(self._seleccion)
        self.tabla.doubleClicked.connect(lambda _: self.actualizar())
        tv.addWidget(self.tabla, 1)

        pie = QHBoxLayout()
        self.total = texto("", 13, 400, PIZARRA)
        pie.addWidget(self.total)
        pie.addStretch()
        pie.addWidget(texto("Doble clic en una fila para actualizarla", 13, 400, PIZARRA))
        tv.addLayout(pie)
        v.addWidget(tarjeta, 1)

        self._temporizador_aviso = QTimer(self)
        self._temporizador_aviso.setSingleShot(True)
        self._temporizador_aviso.timeout.connect(self.aviso.hide)
        self._seleccion()

    # ---------- Utilidades ----------
    def notificar(self, mensaje, tipo="ok"):
        fondo, color = (NEON, OBSIDIANA) if tipo == "ok" else (AMARILLO, OBSIDIANA)
        self.aviso.setText(mensaje)
        self.aviso.setStyleSheet(f"background: {fondo}; color: {color}; "
                                 "border-radius: 10px; padding: 10px 16px;")
        self.aviso.show()
        self._temporizador_aviso.start(4000)

    def _seleccion(self):
        hay = self.id_seleccionado() is not None
        self.b_editar.setEnabled(hay)
        self.b_eliminar.setEnabled(hay)

    def id_seleccionado(self):
        filas = self.tabla.selectionModel().selectedRows()
        if not filas:
            return None
        return self.tabla.item(filas[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def seleccionar(self, id_):
        for fila in range(self.tabla.rowCount()):
            if self.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole) == id_:
                self.tabla.selectRow(fila)
                self.tabla.scrollToItem(self.tabla.item(fila, 0))
                return

    def _pedir_id(self, accion):
        """Si no hay fila seleccionada (por ejemplo, desde el menú) se pide el ID."""
        id_ = self.id_seleccionado()
        if id_ is not None:
            return id_
        valor, ok = QInputDialog.getInt(
            self, f"{accion} {self.cfg['singular']}",
            f"ID {self.g['del_']} {self.cfg['singular']} a {accion.lower()}:", 1, 1, 2147483647)
        return valor if ok else None

    def _siguiente_id(self):
        r = self.bd.ejecutar(f"SELECT MAX({self.cfg['pk']}) AS maximo FROM {self.cfg['tabla']}")
        if not r["estado"]:
            mostrar_error(self, "Error", r, "No se pudo calcular el ID nuevo.")
            return None
        maximo = r["registros"][0]["maximo"]
        return 1 if maximo in (None, "None") else int(num(maximo)) + 1

    # ---------- CONSULTAR ----------
    def cargar(self):
        cfg, P = self.cfg, self.bd.P
        busqueda = self.buscar.text().strip()
        sql, parametros = cfg["vista"], None
        if busqueda.isdigit():
            sql += f" WHERE {cfg['pk_q']} = {P} OR UPPER({cfg['nombre_q']}) LIKE UPPER({P})"
            parametros = (int(busqueda), f"%{busqueda}%")
        elif busqueda:
            sql += f" WHERE UPPER({cfg['nombre_q']}) LIKE UPPER({P})"
            parametros = (f"%{busqueda}%",)
        sql += f" ORDER BY {cfg['orden']}"

        r = self.bd.ejecutar(sql, parametros)
        if not r["estado"]:
            self.tabla.setRowCount(0)
            self.total.setText("No se pudo consultar la tabla")
            self.notificar("Error al consultar", "error")
            return

        filas = r["registros"]
        self.tabla.setRowCount(len(filas))
        for i, registro in enumerate(filas):
            for j, (col, _, fmt) in enumerate(cfg["cols"]):
                item = QTableWidgetItem(formatear(registro.get(col), fmt))
                item.setToolTip(item.text())
                if fmt in ("dinero", "entero"):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if j == 0:
                    item.setData(Qt.ItemDataRole.UserRole, int(num(registro.get(cfg["pk"]))))
                    item.setForeground(QColor(PIZARRA))
                self.tabla.setItem(i, j, item)
        self.tabla.resizeColumnsToContents()
        for j in range(self.tabla.columnCount() - 1):
            ancho = self.tabla.columnWidth(j)
            self.tabla.setColumnWidth(j, min(max(ancho + 24, 64), 260))

        n = len(filas)
        if busqueda:
            self.total.setText(f"{n} resultado{'s' if n != 1 else ''} para «{busqueda}»")
        else:
            self.total.setText(f"{n} registro{'s' if n != 1 else ''}")
        self._seleccion()

    # ---------- INSERTAR ----------
    def insertar(self):
        cfg = self.cfg
        nuevo_id = self._siguiente_id()
        if nuevo_id is None:
            return
        dialogo = DialogoRegistro(self, self.bd, cfg, nuevo_id)
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return
        columnas = [cfg["pk"]] + [c[0] for c in cfg["campos"]]
        sql = (f"INSERT INTO {cfg['tabla']} ({', '.join(columnas)}) "
               f"VALUES ({', '.join([self.bd.P] * len(columnas))})")
        r = self.bd.ejecutar(sql, tuple([nuevo_id] + dialogo.valores()))
        if not r["estado"]:
            mostrar_error(self, "No se pudo insertar", r)
            return
        self.notificar(f"{cfg['singular'].capitalize()} #{nuevo_id} registrad{self.g['o']}")
        self.cargar()
        self.seleccionar(nuevo_id)

    # ---------- ACTUALIZAR ----------
    def actualizar(self):
        cfg = self.cfg
        id_ = self._pedir_id("Actualizar")
        if id_ is None:
            return
        campos = [c[0] for c in cfg["campos"]]
        r = self.bd.ejecutar(
            f"SELECT {', '.join(campos)} FROM {cfg['tabla']} WHERE {cfg['pk']} = {self.bd.P}",
            (id_,))
        if not r["estado"]:
            mostrar_error(self, "Error", r)
            return
        if not r["registros"]:
            self.notificar(f"No existe {self.g['un']} {cfg['singular']} con el ID {id_}", "error")
            return
        dialogo = DialogoRegistro(self, self.bd, cfg, id_, r["registros"][0])
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return
        asignaciones = ", ".join(f"{c} = {self.bd.P}" for c in campos)
        r = self.bd.ejecutar(
            f"UPDATE {cfg['tabla']} SET {asignaciones} WHERE {cfg['pk']} = {self.bd.P}",
            tuple(dialogo.valores() + [id_]))
        if not r["estado"]:
            mostrar_error(self, "No se pudo actualizar", r)
            return
        self.notificar(f"{cfg['singular'].capitalize()} #{id_} actualizad{self.g['o']}")
        self.cargar()
        self.seleccionar(id_)

    # ---------- ELIMINAR ----------
    def eliminar(self):
        cfg = self.cfg
        id_ = self._pedir_id("Eliminar")
        if id_ is None:
            return
        r = self.bd.ejecutar(cfg["vista"] + f" WHERE {cfg['pk_q']} = {self.bd.P}", (id_,))
        if not r["estado"]:
            mostrar_error(self, "Error", r)
            return
        if not r["registros"]:
            self.notificar(f"No existe {self.g['un']} {cfg['singular']} con el ID {id_}", "error")
            return
        nombre = r["registros"][0].get(cfg["cols"][1][0], "")
        if not confirmar(self, f"Eliminar {cfg['singular']}",
                         f"¿Seguro que deseas eliminar {self.g['este']} {cfg['singular']}?\n\n"
                         f"#{id_} · {nombre}\n\nEsta acción no se puede deshacer."):
            return
        r = self.bd.ejecutar(f"DELETE FROM {cfg['tabla']} WHERE {cfg['pk']} = {self.bd.P}", (id_,))
        if not r["estado"]:
            mostrar_error(self, "No se pudo eliminar", r, f"#{id_} · {nombre}")
            return
        self.notificar(f"{cfg['singular'].capitalize()} #{id_} eliminad{self.g['o']}")
        self.cargar()


# ============================================================
#  DIÁLOGO PARA INSERTAR / ACTUALIZAR UN REGISTRO
# ============================================================
class DialogoRegistro(QDialog):
    def __init__(self, padre, bd, cfg, id_, actual=None):
        super().__init__(padre)
        self.cfg = cfg
        self.setObjectName("dialogo")
        self.setModal(True)
        self.setMinimumWidth(500)
        g = genero(cfg)
        editando = actual is not None
        actual = actual or {}
        titulo = (f"Actualizar {cfg['singular']}" if editando
                  else f"Nuev{g['o']} {cfg['singular']}")
        self.setWindowTitle(titulo)

        v = QVBoxLayout(self)
        v.setContentsMargins(32, 28, 32, 24)
        v.setSpacing(4)
        v.addWidget(ceja("Actualizar registro" if editando else "Insertar registro", OBSIDIANA))
        v.addWidget(texto(titulo[0].upper() + titulo[1:], 24, 500, OBSIDIANA))
        v.addWidget(texto("Modifica los datos y guarda los cambios." if editando
                          else "Llena los datos del nuevo registro.", 14, 400, PIZARRA))
        v.addSpacing(14)

        # El ID se muestra pero no se puede cambiar
        campo_id = QLineEdit(str(id_))
        campo_id.setReadOnly(True)
        self._agregar(v, "ID", campo_id)

        self.widgets = []
        for col, etiqueta, tipo, op in cfg["campos"]:
            valor = actual.get(col)
            if tipo == "texto":
                w = QLineEdit("" if valor is None else str(valor))
                w.setMaxLength(op.get("max", 255))
            elif tipo == "entero":
                w = QSpinBox()
                w.setRange(0, 2_000_000_000)
                w.setGroupSeparatorShown(True)
                w.setValue(int(num(valor)))
            elif tipo == "decimal":
                w = QDoubleSpinBox()
                w.setRange(0, 99_999_999.99)
                w.setDecimals(2)
                w.setPrefix("$ ")
                w.setGroupSeparatorShown(True)
                w.setValue(num(valor))
            elif tipo == "fecha":
                w = QDateEdit()
                w.setCalendarPopup(True)
                w.setDisplayFormat("yyyy-MM-dd")
                fecha = QDate.fromString(str(valor)[:10], "yyyy-MM-dd") if valor else QDate()
                w.setDate(fecha if fecha.isValid() else QDate.currentDate())
            else:  # fk: lista desplegable con los registros de la tabla relacionada
                w = QComboBox()
                r = bd.ejecutar(op["sql"])
                for fila in (r["registros"] if r["estado"] else []):
                    w.addItem(f"{fila['nombre']}  (#{fila['id']})", int(num(fila["id"])))
                if valor is not None:
                    w.setCurrentIndex(max(0, w.findData(int(num(valor)))))
            if isinstance(w, QAbstractSpinBox):
                w.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            self.widgets.append((col, etiqueta, tipo, w))
            self._agregar(v, etiqueta, w)

        self.error = texto("", 13, 400, nombre="error", ajustar=True)
        self.error.hide()
        v.addSpacing(4)
        v.addWidget(self.error)
        v.addSpacing(14)

        botones = QHBoxLayout()
        botones.addStretch()
        botones.addWidget(boton("Cancelar", "fantasmaClaro", self.reject))
        guardar = boton("Guardar cambios" if editando else "Guardar", "primario", self.aceptar)
        guardar.setDefault(True)
        botones.addWidget(guardar)
        v.addLayout(botones)

        if self.widgets:
            self.widgets[0][3].setFocus()

    def _agregar(self, layout, etiqueta, widget):
        layout.addWidget(texto(etiqueta, 13, 500, nombre="etiquetaCampo"))
        widget.setFont(fuente(14))
        layout.addWidget(widget)
        layout.addSpacing(8)

    def aceptar(self):
        for col, etiqueta, tipo, w in self.widgets:
            if tipo == "texto" and not w.text().strip():
                self._error(f"El campo «{etiqueta}» es obligatorio.", w)
                return
            if tipo == "fk" and w.currentData() is None:
                self._error(f"No hay registros disponibles para «{etiqueta}». "
                            "Primero da de alta uno en su catálogo.", w)
                return
        self.accept()

    def _error(self, msg, widget):
        self.error.setText(msg)
        self.error.show()
        widget.setFocus()

    def valores(self):
        """Valores capturados, en el mismo orden que cfg['campos']."""
        salida = []
        for _, _, tipo, w in self.widgets:
            if tipo == "texto":
                salida.append(w.text().strip())
            elif tipo == "entero":
                salida.append(w.value())
            elif tipo == "decimal":
                salida.append(round(w.value(), 2))
            elif tipo == "fecha":
                salida.append(w.date().toString("yyyy-MM-dd"))
            else:
                salida.append(w.currentData())
        return salida


# ============================================================
#  ARRANQUE
# ============================================================
def configurar_apariencia(app):
    global FUENTE
    familias = set(QFontDatabase.families())
    for candidata in ("Inter", "Segoe UI Variable Text", "Segoe UI", "Helvetica Neue", "Arial"):
        if candidata in familias:
            FUENTE = candidata
            break
    app.setStyle("Fusion")
    paleta = QPalette()
    for rol, color in ((QPalette.ColorRole.Window, OBSIDIANA), (QPalette.ColorRole.WindowText, BLANCO),
                       (QPalette.ColorRole.Base, ABISMO), (QPalette.ColorRole.AlternateBase, OBSIDIANA),
                       (QPalette.ColorRole.Text, BLANCO), (QPalette.ColorRole.Button, ABISMO),
                       (QPalette.ColorRole.ButtonText, BLANCO), (QPalette.ColorRole.Highlight, NEON),
                       (QPalette.ColorRole.HighlightedText, OBSIDIANA),
                       (QPalette.ColorRole.PlaceholderText, PIZARRA),
                       (QPalette.ColorRole.ToolTipBase, CARBON), (QPalette.ColorRole.ToolTipText, BLANCO)):
        paleta.setColor(rol, QColor(color))
    app.setPalette(paleta)
    app.setFont(fuente(14))
    app.setStyleSheet(QSS)


def main():
    load_dotenv()
    if len(sys.argv) == 3 and sys.argv[1] == "--hash":
        print(generar_hash(sys.argv[2]))
        return
    app = QApplication(sys.argv)
    configurar_apariencia(app)
    login = VentanaLogin()
    login.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()