"""
VENTANA PRINCIPAL (el menú del sistema).

Partes de la ventana:
    1. Menú de arriba:  Archivo · Catálogos · Ayuda
       "Catálogos" tiene un submenú por cada tabla maestra con
       Insertar / Actualizar / Eliminar / Consultar.
    2. Marquesina naranja y encabezado (nombre, motor de BD, usuario).
    3. Barra lateral con botones para cambiar de página.
    4. Las páginas (Dashboard y una por cada catálogo) dentro de un QStackedWidget.

Aquí NO se escribe SQL: las páginas llaman a las funciones de consultas.py.
"""
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                             QPushButton, QStackedWidget, QVBoxLayout, QWidget)

from estilos import Marquesina
from ui_catalogo import PaginaCatalogo, definir_catalogos
from ui_dashboard import PaginaDashboard


class VentanaPrincipal(QMainWindow):

    def __init__(self, bd, motor, usuario, login):
        super().__init__()
        self.bd = bd              # objeto Consultas (ya trae la conexión abierta)
        self.login = login        # ventana de login, para regresar al cerrar sesión
        self.saliendo_a_login = False
        self.setWindowTitle(f"Ferretería · {motor}")
        self.resize(1240, 780)

        # ---------- Crear las páginas ----------
        self.paginas = QStackedWidget()
        self.indice = {}          # clave -> número de página
        self.botones = {}         # clave -> botón de la barra lateral

        self.dashboard = PaginaDashboard(bd)
        self.agregar_pagina("dashboard", self.dashboard)

        self.catalogos = {}       # clave -> PaginaCatalogo
        for cfg in definir_catalogos(bd):
            pagina = PaginaCatalogo(bd, cfg)
            self.catalogos[cfg["clave"]] = pagina
            self.agregar_pagina(cfg["clave"], pagina)

        # ---------- Armar la ventana ----------
        self.crear_menu(definir_catalogos(bd))

        central = QWidget()
        central.setObjectName("fondo")
        raiz = QVBoxLayout(central)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(Marquesina("★ CONTROL DE INVENTARIOS ★ TORNILLOS ★ PINTURA ★ "
                                  "HERRAMIENTA ★ PLOMERÍA ★ ELECTRICIDAD"))
        raiz.addWidget(self.crear_encabezado(motor, usuario))

        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.setSpacing(0)
        cuerpo.addWidget(self.crear_barra_lateral(definir_catalogos(bd)))
        cuerpo.addWidget(self.paginas, 1)
        raiz.addLayout(cuerpo, 1)
        self.setCentralWidget(central)

        self.ir("dashboard")

    def agregar_pagina(self, clave, pagina):
        self.indice[clave] = self.paginas.addWidget(pagina)

    # ============================================================
    # 1. MENÚ DE ARRIBA
    # ============================================================
    def crear_menu(self, catalogos):
        barra = self.menuBar()

        archivo = barra.addMenu("Archivo")
        archivo.addAction("Dashboard", lambda: self.ir("dashboard"))
        archivo.addSeparator()
        archivo.addAction("Cerrar sesión", self.cerrar_sesion)
        archivo.addAction("Salir", self.close)

        menu_catalogos = barra.addMenu("Catálogos")
        for cfg in catalogos:
            clave = cfg["clave"]
            sub = menu_catalogos.addMenu(cfg["titulo"])
            # lambda con c=clave para que cada opción recuerde SU tabla
            sub.addAction("Insertar", lambda c=clave: self.accion(c, "insertar"))
            sub.addAction("Actualizar", lambda c=clave: self.accion(c, "actualizar"))
            sub.addAction("Eliminar", lambda c=clave: self.accion(c, "eliminar"))
            sub.addAction("Consultar", lambda c=clave: self.ir(c))

        ayuda = barra.addMenu("Ayuda")
        acerca = QAction("Acerca de", self)
        acerca.triggered.connect(self.acerca_de)
        ayuda.addAction(acerca)

    def accion(self, clave, operacion):
        """Abre la página del catálogo y ejecuta la operación elegida en el menú."""
        self.ir(clave)
        pagina = self.catalogos[clave]
        if operacion == "insertar":
            pagina.insertar()
        elif operacion == "actualizar":
            pagina.actualizar()
        elif operacion == "eliminar":
            pagina.eliminar()

    # ============================================================
    # 2. ENCABEZADO
    # ============================================================
    def crear_encabezado(self, motor, usuario):
        encabezado = QFrame()
        encabezado.setObjectName("encabezado")
        h = QHBoxLayout(encabezado)
        h.setContentsMargins(24, 12, 24, 12)

        marca = QLabel("FERRETERÍA")
        marca.setObjectName("titulo")
        h.addWidget(marca)
        h.addStretch()

        for texto in (f"● {motor}", f"USUARIO: {usuario['nombre']}"):
            pastilla = QLabel(texto)
            pastilla.setObjectName("pastilla")
            h.addWidget(pastilla)

        salir = QPushButton("CERRAR SESIÓN")
        salir.clicked.connect(self.cerrar_sesion)
        h.addWidget(salir)
        return encabezado

    # ============================================================
    # 3. BARRA LATERAL
    # ============================================================
    def crear_barra_lateral(self, catalogos):
        barra = QFrame()
        barra.setObjectName("barraLateral")
        barra.setFixedWidth(220)
        v = QVBoxLayout(barra)
        v.setContentsMargins(14, 18, 14, 18)
        v.setSpacing(4)

        grupo = QButtonGroup(self)        # solo un botón marcado a la vez

        def boton(clave, texto):
            b = QPushButton(texto)
            b.setObjectName("nav")
            b.setCheckable(True)
            b.clicked.connect(lambda: self.ir(clave))
            grupo.addButton(b)
            self.botones[clave] = b
            v.addWidget(b)

        etiqueta = QLabel("GENERAL")
        etiqueta.setObjectName("seccion")
        v.addWidget(etiqueta)
        boton("dashboard", "▣ DASHBOARD")

        v.addSpacing(14)
        etiqueta = QLabel("CATÁLOGOS")
        etiqueta.setObjectName("seccion")
        v.addWidget(etiqueta)
        for cfg in catalogos:
            boton(cfg["clave"], "▸ " + cfg["titulo"].upper())

        v.addStretch()
        return barra

    # ============================================================
    # 4. CAMBIAR DE PÁGINA
    # ============================================================
    def ir(self, clave):
        self.paginas.setCurrentIndex(self.indice[clave])
        self.botones[clave].setChecked(True)
        # al entrar a una página se vuelven a leer los datos de la BD
        if clave == "dashboard":
            self.dashboard.actualizar()
        else:
            self.catalogos[clave].cargar()

    # ============================================================
    # SESIÓN Y CIERRE
    # ============================================================
    def acerca_de(self):
        QMessageBox.information(self, "Acerca de",
                                "Sistema de control de inventarios para ferretería.\n"
                                "Taller de Bases de Datos · TecNM Campus Jiquilpan")

    def cerrar_sesion(self):
        self.saliendo_a_login = True
        self.close()

    def closeEvent(self, evento):
        self.bd.cerrar()                 # siempre se cierra la conexión
        if self.saliendo_a_login:
            self.login.reiniciar()
        evento.accept()
