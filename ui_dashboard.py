"""
DASHBOARD: muestra el resultado de las consultas del entregable 2.

Los datos salen de consultas.py (funciones bd.dashboard_...).
Las gráficas se dibujan a mano con QPainter (no hace falta instalar nada más).
"""
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QHeaderView,
                             QLabel, QPushButton, QScrollArea, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from estilos import CARBON, CREMA, GRIS, NARANJA, NEGRO, ROJO, VERDE, fuente
from ui_catalogo import dinero

COLORES = [NEGRO, NARANJA, VERDE, CARBON, GRIS]   # colores de las gráficas


# ============================================================
# GRÁFICAS
# Todas reciben una lista de (etiqueta, valor) en el método poner().
# ============================================================
class Grafica(QWidget):
    def __init__(self, formato=str):
        super().__init__()
        self.datos = []
        self.formato = formato          # función para escribir el número (dinero, entero...)
        self.setMinimumHeight(220)

    def poner(self, datos):
        self.datos = [(str(e), float(v)) for e, v in datos]
        # al pasar el mouse se ven todos los valores
        self.setToolTip("\n".join(f"{e}: {self.formato(v)}" for e, v in self.datos))
        self.update()

    def sin_datos(self, p):
        p.setPen(QColor(GRIS))
        p.setFont(fuente(12, titulo=True))
        p.drawText(QRectF(self.rect()), Qt.AlignmentFlag.AlignCenter, "SIN DATOS")


class GraficaColumnas(Grafica):
    """Columnas verticales (ventas por método de pago)."""

    def paintEvent(self, evento):
        p = QPainter(self)
        if not self.datos:
            return self.sin_datos(p)
        maximo = max(v for _, v in self.datos) or 1
        ancho_slot = self.width() / len(self.datos)
        base = self.height() - 28
        p.setPen(QPen(QColor(NEGRO), 2))
        p.drawLine(0, int(base), self.width(), int(base))
        for i, (etiqueta, valor) in enumerate(self.datos):
            alto = (base - 30) * valor / maximo
            x = i * ancho_slot + ancho_slot * 0.25
            barra = QRectF(x, base - alto, ancho_slot * 0.5, alto)
            p.fillRect(barra, QColor(COLORES[i % len(COLORES)]))
            p.setPen(QColor(NEGRO))
            p.drawRect(barra)
            p.setFont(fuente(12, negrita=True))
            p.drawText(QRectF(i * ancho_slot, base - alto - 24, ancho_slot, 22),
                       Qt.AlignmentFlag.AlignCenter, self.formato(valor))
            p.setFont(fuente(12))
            p.drawText(QRectF(i * ancho_slot, base + 4, ancho_slot, 22),
                       Qt.AlignmentFlag.AlignCenter, etiqueta)


class GraficaBarras(Grafica):
    """Barras horizontales (top 5 productos)."""

    def paintEvent(self, evento):
        p = QPainter(self)
        if not self.datos:
            return self.sin_datos(p)
        maximo = max(v for _, v in self.datos) or 1
        alto_fila = self.height() / len(self.datos)
        col_texto = self.width() * 0.45
        ancho_util = self.width() - col_texto - 70
        p.setFont(fuente(12))
        for i, (etiqueta, valor) in enumerate(self.datos):
            y = i * alto_fila
            p.setPen(QColor(NEGRO))
            texto = p.fontMetrics().elidedText(etiqueta, Qt.TextElideMode.ElideRight, int(col_texto - 10))
            p.drawText(QRectF(0, y, col_texto - 10, alto_fila), Qt.AlignmentFlag.AlignVCenter, texto)
            barra = QRectF(col_texto, y + alto_fila * 0.3, ancho_util * valor / maximo, alto_fila * 0.4)
            p.fillRect(barra, QColor(VERDE if i == 0 else NEGRO))
            p.drawText(QRectF(col_texto + barra.width() + 8, y, 70, alto_fila),
                       Qt.AlignmentFlag.AlignVCenter, self.formato(valor))


class GraficaDona(Grafica):
    """Dona con leyenda (ventas por categoría)."""

    def paintEvent(self, evento):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        total = sum(v for _, v in self.datos)
        if not self.datos or total <= 0:
            return self.sin_datos(p)
        lado = min(self.height() - 20, self.width() * 0.45)
        grosor = lado * 0.22
        caja = QRectF(10 + grosor / 2, (self.height() - lado) / 2 + grosor / 2, lado - grosor, lado - grosor)
        inicio = 90 * 16
        for i, (_, valor) in enumerate(self.datos):
            barrido = int(-360 * 16 * valor / total)
            p.setPen(QPen(QColor(COLORES[i % len(COLORES)]), grosor, cap=Qt.PenCapStyle.FlatCap))
            p.drawArc(caja, inicio, barrido)
            inicio += barrido
        p.setPen(QColor(NEGRO))
        p.setFont(fuente(14, negrita=True))
        p.drawText(caja, Qt.AlignmentFlag.AlignCenter, self.formato(total))
        # leyenda
        x = lado + 30
        p.setFont(fuente(12))
        for i, (etiqueta, valor) in enumerate(self.datos):
            y = 20 + i * 28
            p.fillRect(QRectF(x, y + 4, 14, 14), QColor(COLORES[i % len(COLORES)]))
            p.drawRect(QRectF(x, y + 4, 14, 14))
            p.drawText(QRectF(x + 22, y, self.width() - x - 22, 22), Qt.AlignmentFlag.AlignVCenter,
                       f"{etiqueta}  {valor / total * 100:.0f}%")


class GraficaLinea(Grafica):
    """Línea con puntos (ventas por fecha)."""

    def paintEvent(self, evento):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.datos:
            return self.sin_datos(p)
        maximo = max(v for _, v in self.datos) * 1.2 or 1
        izq, der, arriba, abajo = 40, 40, 26, 28
        ancho = self.width() - izq - der
        alto = self.height() - arriba - abajo
        n = len(self.datos)

        def punto(i):
            x = izq + (ancho * i / (n - 1) if n > 1 else ancho / 2)
            return QPointF(x, arriba + alto - alto * self.datos[i][1] / maximo)

        p.setPen(QPen(QColor(NEGRO), 2))
        p.drawLine(izq, arriba + alto, izq + ancho, arriba + alto)
        camino = QPainterPath(punto(0))
        for i in range(1, n):
            camino.lineTo(punto(i))
        p.setPen(QPen(QColor(NEGRO), 3))
        p.drawPath(camino)
        p.setFont(fuente(11))
        for i, (fecha, valor) in enumerate(self.datos):
            pt = punto(i)
            p.setBrush(QColor(NARANJA))
            p.setPen(QPen(QColor(NEGRO), 2))
            p.drawRect(QRectF(pt.x() - 5, pt.y() - 5, 10, 10))   # punto cuadrado (estilo pixel)
            p.drawText(QRectF(pt.x() - 40, pt.y() - 24, 80, 18), Qt.AlignmentFlag.AlignCenter,
                       self.formato(valor))
            p.drawText(QRectF(pt.x() - 30, arriba + alto + 6, 60, 18), Qt.AlignmentFlag.AlignCenter,
                       f"{fecha[8:10]}/{fecha[5:7]}")


# ============================================================
# PÁGINA DEL DASHBOARD
# ============================================================
class Tarjeta(QFrame):
    """Tarjeta con un número grande."""

    def __init__(self, titulo, nota):
        super().__init__()
        self.setObjectName("tarjeta")
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 12)
        etiqueta = QLabel(titulo.upper())
        etiqueta.setObjectName("seccion")
        v.addWidget(etiqueta)
        self.valor = QLabel("—")
        self.valor.setObjectName("numero")
        v.addWidget(self.valor)
        texto = QLabel(nota)
        texto.setObjectName("subtitulo")
        v.addWidget(texto)

    def poner(self, texto, color=NEGRO):
        self.valor.setText(texto)
        self.valor.setStyleSheet(f"color: {color};")   # verde, rojo o negro


def panel(titulo, contenido):
    """Recuadro con título para una gráfica o tabla."""
    marco = QFrame()
    marco.setObjectName("tarjeta")
    v = QVBoxLayout(marco)
    v.setContentsMargins(16, 12, 16, 12)
    etiqueta = QLabel(titulo.upper())
    etiqueta.setObjectName("panelTitulo")
    v.addWidget(etiqueta)
    v.addWidget(contenido, 1)
    return marco


class PaginaDashboard(QWidget):

    def __init__(self, bd):
        super().__init__()
        self.bd = bd

        # El contenido va dentro de un área con scroll por si la ventana es chica
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        area = QScrollArea()
        area.setWidgetResizable(True)
        raiz.addWidget(area)
        contenido = QWidget()
        contenido.setObjectName("fondo")
        area.setWidget(contenido)
        v = QVBoxLayout(contenido)
        v.setContentsMargins(28, 24, 28, 24)
        v.setSpacing(14)

        encabezado = QHBoxLayout()
        titulo = QLabel("DASHBOARD")
        titulo.setObjectName("titulo")
        encabezado.addWidget(titulo)
        encabezado.addStretch()
        actualizar = QPushButton("↻ ACTUALIZAR")
        actualizar.clicked.connect(self.actualizar)
        encabezado.addWidget(actualizar)
        v.addLayout(encabezado)

        # Fila de tarjetas
        self.t_ventas = Tarjeta("Ventas", "Total vendido")
        self.t_compras = Tarjeta("Compras", "Total comprado")
        self.t_balance = Tarjeta("Balance", "Ventas - compras")
        self.t_productos = Tarjeta("Productos", "En el catálogo")
        self.t_clientes = Tarjeta("Clientes", "Registrados")
        self.t_stock = Tarjeta("Stock bajo", "Bajo su mínimo")
        fila = QGridLayout()
        fila.setSpacing(12)
        for i, t in enumerate([self.t_ventas, self.t_compras, self.t_balance,
                               self.t_productos, self.t_clientes, self.t_stock]):
            fila.addWidget(t, i // 3, i % 3)
        v.addLayout(fila)

        # Gráficas
        self.g_metodo = GraficaColumnas(dinero)
        self.g_categoria = GraficaDona(dinero)
        self.g_top = GraficaBarras(lambda n: f"{n:.0f} uds")
        self.g_fecha = GraficaLinea(lambda n: f"${n:,.0f}")

        self.tabla_stock = QTableWidget(0, 3)
        self.tabla_stock.setHorizontalHeaderLabels(["PRODUCTO", "EXISTENCIA", "MÍNIMO"])
        self.tabla_stock.verticalHeader().setVisible(False)
        self.tabla_stock.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_stock.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_stock.setMinimumHeight(200)

        rejilla = QGridLayout()
        rejilla.setSpacing(12)
        rejilla.addWidget(panel("Ventas por fecha", self.g_fecha), 0, 0, 1, 2)
        rejilla.addWidget(panel("2 · Ventas por método de pago", self.g_metodo), 1, 0)
        rejilla.addWidget(panel("3 · Ventas por categoría", self.g_categoria), 1, 1)
        rejilla.addWidget(panel("4 · Top 5 más vendidos", self.g_top), 2, 0)
        rejilla.addWidget(panel("5 · Productos con stock bajo", self.tabla_stock), 2, 1)
        rejilla.setColumnStretch(0, 1)   # las dos columnas del mismo ancho
        rejilla.setColumnStretch(1, 1)
        v.addLayout(rejilla)

    def actualizar(self):
        bd = self.bd

        # Tarjetas
        r = bd.dashboard_totales()
        if r["estado"]:
            fila = r["registros"][0]
            ventas, compras = float(fila["ventas"]), float(fila["compras"])
            self.t_ventas.poner(dinero(ventas))
            self.t_compras.poner(dinero(compras))
            self.t_balance.poner(dinero(ventas - compras), VERDE if ventas >= compras else ROJO)
            self.t_productos.poner(str(fila["productos"]))
            self.t_clientes.poner(str(fila["clientes"]))

        # Consulta 2: método de pago
        r = bd.dashboard_ventas_metodo_pago()
        self.g_metodo.poner([(x["metodo_pago"], x["total"]) for x in r["registros"]] if r["estado"] else [])

        # Consulta 3: por categoría
        r = bd.dashboard_ventas_categoria()
        self.g_categoria.poner([(x["categoria"], x["total"]) for x in r["registros"]] if r["estado"] else [])

        # Consulta 4: top 5 (la consulta trae todos ordenados, aquí se toman 5)
        r = bd.dashboard_top_productos()
        self.g_top.poner([(x["nombre"], x["unidades"]) for x in r["registros"]][:5] if r["estado"] else [])

        # Ventas por fecha
        r = bd.dashboard_ventas_por_fecha()
        self.g_fecha.poner([(x["fecha"], x["total"]) for x in r["registros"]] if r["estado"] else [])

        # Consulta 5: stock bajo
        r = bd.dashboard_stock_bajo()
        registros = r["registros"] if r["estado"] else []
        self.t_stock.poner(str(len(registros)), ROJO if registros else VERDE)
        self.tabla_stock.setRowCount(len(registros))
        for i, x in enumerate(registros):
            self.tabla_stock.setItem(i, 0, QTableWidgetItem(x["nombre"]))
            self.tabla_stock.setItem(i, 1, QTableWidgetItem(str(x["existencia"])))
            self.tabla_stock.setItem(i, 2, QTableWidgetItem(str(x["stock_minimo"])))
