"""
SOLO APARIENCIA. Aquí no hay nada de base de datos.

Estilo "mostrador de ferretería retro": fondo crema, bordes negros gruesos,
letra pixel, una franja naranja con texto que corre (marquesina) y
el verde reservado para la acción principal (Insertar, Guardar, Entrar).

Contenido:
    1. Colores
    2. Fuentes (las .ttf de la carpeta fuentes/)
    3. Hoja de estilos QSS (es como el CSS de las páginas web)
    4. Piezas decorativas: Marquesina y Cuadricula
"""
import os

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPainter
from PyQt6.QtWidgets import QWidget

# ------------------------------------------------------------
# 1. COLORES
# ------------------------------------------------------------
CREMA = "#f3e5df"         # fondo de toda la app
CREMA_CLARO = "#fbf4f0"   # fondo de tablas y campos de texto
NEGRO = "#000000"         # texto y bordes
GRIS_PIXEL = "#e5e7eb"    # líneas finas
CARBON = "#333333"        # texto secundario
GRIS = "#737373"          # texto apagado / deshabilitado
NARANJA = "#faa21f"       # solo la marquesina
VERDE = "#128e44"         # solo el botón principal
ROJO = "#b42318"          # eliminar y errores

# ------------------------------------------------------------
# 2. FUENTES
# ------------------------------------------------------------
FUENTE_TITULO = "Silkscreen"   # letra pixel para títulos, menú y botones
FUENTE_TEXTO = "Space Mono"    # letra para tablas, campos y párrafos


def cargar_fuentes():
    carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuentes")
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".ttf"):
            QFontDatabase.addApplicationFont(os.path.join(carpeta, archivo))


def fuente(tam=13, negrita=False, titulo=False):
    f = QFont(FUENTE_TITULO if titulo else FUENTE_TEXTO)
    f.setPixelSize(tam)
    f.setBold(negrita)
    return f


# ------------------------------------------------------------
# 3. HOJA DE ESTILOS (QSS)
#    #nombre se refiere a widget.setObjectName("nombre")
# ------------------------------------------------------------
QSS = f"""
QWidget {{ color: {NEGRO}; font-family: "{FUENTE_TEXTO}"; font-size: 13px; }}
QMainWindow, QDialog, #fondo {{ background: {CREMA}; }}
QLabel {{ background: transparent; }}

/* Títulos */
QLabel#titulo {{ font-family: "{FUENTE_TITULO}"; font-size: 26px; }}
QLabel#subtitulo {{ color: {CARBON}; font-size: 13px; }}
QLabel#numero {{ font-family: "{FUENTE_TITULO}"; font-size: 26px; }}
QLabel#panelTitulo {{ font-family: "{FUENTE_TITULO}"; font-size: 13px; }}
QLabel#seccion {{ font-family: "{FUENTE_TITULO}"; font-size: 11px; color: {GRIS}; }}

/* Menú de arriba (Archivo · Catálogos · Ayuda) */
QMenuBar {{ background: {CREMA}; border-bottom: 2px solid {NEGRO};
           font-family: "{FUENTE_TITULO}"; font-size: 12px; padding: 2px 6px; }}
QMenuBar::item {{ padding: 6px 12px; border-radius: 6px; background: transparent; }}
QMenuBar::item:selected {{ background: {NEGRO}; color: {CREMA}; }}
QMenu {{ background: {CREMA}; border: 2px solid {NEGRO}; padding: 4px;
        font-family: "{FUENTE_TITULO}"; font-size: 12px; }}
QMenu::item {{ padding: 7px 28px 7px 14px; border-radius: 4px; }}
QMenu::item:selected {{ background: {NEGRO}; color: {CREMA}; }}
QMenu::separator {{ height: 2px; background: {NEGRO}; margin: 4px 6px; }}

/* Encabezado y barra lateral */
#encabezado {{ background: {CREMA}; border-bottom: 2px solid {NEGRO}; }}
#barraLateral {{ background: {CREMA}; border-right: 2px solid {NEGRO}; }}
QPushButton#nav {{ text-align: left; padding: 10px 12px; border: 2px solid transparent;
                  border-radius: 6px; background: transparent;
                  font-family: "{FUENTE_TITULO}"; font-size: 13px; }}
QPushButton#nav:hover {{ border-color: {NEGRO}; }}
QPushButton#nav:checked {{ background: {NEGRO}; color: {CREMA}; border-color: {NEGRO}; }}

/* Etiquetas tipo pastilla (motor de BD, usuario) */
QLabel#pastilla {{ border: 2px solid {NEGRO}; border-radius: 13px; padding: 2px 12px;
                  font-family: "{FUENTE_TITULO}"; font-size: 11px; background: {CREMA_CLARO}; }}

/* Botones: 6px de radio, borde negro */
QPushButton {{ background: {CREMA_CLARO}; border: 2px solid {NEGRO}; border-radius: 6px;
              padding: 8px 16px; font-family: "{FUENTE_TITULO}"; font-size: 12px; }}
QPushButton:hover {{ background: {GRIS_PIXEL}; }}
QPushButton:pressed {{ background: {NEGRO}; color: {CREMA}; }}
QPushButton:disabled {{ color: {GRIS}; border-color: {GRIS}; background: transparent; }}
QPushButton#primario {{ background: {VERDE}; color: white; }}
QPushButton#primario:hover {{ background: #0f7a3a; }}
QPushButton#peligro {{ color: {ROJO}; border-color: {ROJO}; }}
QPushButton#peligro:hover {{ background: #f6d6d2; }}
QPushButton#peligro:disabled {{ color: {GRIS}; border-color: {GRIS}; background: transparent; }}

/* Campos de captura */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background: {CREMA_CLARO}; border: 2px solid {NEGRO}; border-radius: 6px;
    padding: 6px 10px; min-height: 20px;
    selection-background-color: {NEGRO}; selection-color: {CREMA}; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    background: white; }}
QLineEdit:read-only {{ background: {GRIS_PIXEL}; color: {GRIS}; }}
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{ width: 0; border: none; }}
QComboBox::drop-down, QDateEdit::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{ background: {CREMA_CLARO}; border: 2px solid {NEGRO};
    selection-background-color: {NEGRO}; selection-color: {CREMA}; outline: none; }}

/* Tarjetas: 12px de radio, borde negro */
#tarjeta {{ background: {CREMA_CLARO}; border: 2px solid {NEGRO}; border-radius: 12px; }}

/* Tablas */
QTableWidget {{ background: {CREMA_CLARO}; alternate-background-color: {CREMA};
               border: 2px solid {NEGRO}; border-radius: 8px; gridline-color: {GRIS_PIXEL};
               selection-background-color: {NEGRO}; selection-color: {CREMA}; }}
QTableWidget::item {{ padding: 0 8px; }}
QHeaderView::section {{ background: {NEGRO}; color: {CREMA}; border: none; padding: 8px;
                       font-family: "{FUENTE_TITULO}"; font-size: 11px; }}
QTableCornerButton::section {{ background: {NEGRO}; border: none; }}

/* Barras de desplazamiento */
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: {CREMA}; width: 12px; border-left: 2px solid {NEGRO}; }}
QScrollBar::handle:vertical {{ background: {NEGRO}; min-height: 30px; }}
QScrollBar:horizontal {{ background: {CREMA}; height: 12px; border-top: 2px solid {NEGRO}; }}
QScrollBar::handle:horizontal {{ background: {NEGRO}; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}

/* Mensajes y tooltips */
QMessageBox {{ background: {CREMA}; }}
QToolTip {{ background: {NEGRO}; color: {CREMA}; border: none; padding: 6px; }}
QCalendarWidget QWidget {{ background: {CREMA_CLARO}; alternate-background-color: {CREMA}; }}
"""


def aplicar_estilo(app):
    cargar_fuentes()
    app.setStyle("Fusion")
    app.setFont(fuente(13))
    app.setStyleSheet(QSS)


# ------------------------------------------------------------
# 4. PIEZAS DECORATIVAS
# ------------------------------------------------------------
class Marquesina(QWidget):
    """Franja naranja con un texto que se mueve de derecha a izquierda."""

    def __init__(self, texto):
        super().__init__()
        self.texto = texto + "     "
        self.desplazamiento = 0
        self.setFixedHeight(30)
        self.temporizador = QTimer(self)
        self.temporizador.timeout.connect(self.avanzar)
        self.temporizador.start(40)  # cada 40 ms se mueve 1 pixel

    def avanzar(self):
        self.desplazamiento += 1
        self.update()

    def paintEvent(self, evento):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(NARANJA))
        p.setPen(QColor(NEGRO))
        p.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        p.setFont(fuente(12, titulo=True))
        ancho_texto = p.fontMetrics().horizontalAdvance(self.texto)
        x = -(self.desplazamiento % ancho_texto)
        while x < self.width():  # repite el texto hasta llenar la franja
            p.drawText(QRectF(x, 0, ancho_texto, self.height()),
                       Qt.AlignmentFlag.AlignVCenter, self.texto)
            x += ancho_texto


class Cuadricula(QWidget):
    """Tablero de cuadros negro / crema (decoración)."""

    def __init__(self, lado=32):
        super().__init__()
        self.lado = lado

    def paintEvent(self, evento):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(CREMA))
        for fila in range(self.height() // self.lado + 1):
            for col in range(self.width() // self.lado + 1):
                if (fila + col) % 2 == 0:
                    p.fillRect(col * self.lado, fila * self.lado, self.lado, self.lado, QColor(NEGRO))
