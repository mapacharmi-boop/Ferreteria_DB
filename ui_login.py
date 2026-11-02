"""
Ventana de inicio de sesión.

Aquí se CREA LA CONEXIÓN a la base de datos:
    - Si se elige PostgreSQL  -> ConexionPostgres()   (archivo conpost.py)
    - Si se elige SQL Server  -> ConexionSqlServer()  (archivo consql.py)
Luego se revisa el usuario con bd.iniciar_sesion() (archivo consultas.py).
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget)

from conpost import ConexionPostgres
from consql import ConexionSqlServer
from consultas import Consultas
from estilos import ROJO, Cuadricula, Marquesina


class VentanaLogin(QWidget):

    def __init__(self):
        super().__init__()
        self.principal = None
        self.setObjectName("fondo")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setWindowTitle("Ferretería · Iniciar sesión")
        self.resize(980, 600)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(Marquesina("★ FERRETERÍA ★ TORNILLERÍA ★ PINTURA ★ HERRAMIENTA "
                                  "★ PLOMERÍA ★ ELECTRICIDAD"))

        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.setSpacing(0)
        cuerpo.addWidget(self.panel_marca(), 1)
        cuerpo.addWidget(self.panel_formulario(), 1)
        raiz.addLayout(cuerpo, 1)

    # ---------- Lado izquierdo: tablero con el nombre ----------
    def panel_marca(self):
        tablero = Cuadricula(40)
        capa = QVBoxLayout(tablero)
        capa.setContentsMargins(40, 40, 40, 40)
        capa.addStretch()
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        t = QVBoxLayout(tarjeta)
        t.setContentsMargins(24, 22, 24, 22)
        titulo = QLabel("FERRETERÍA")
        titulo.setObjectName("titulo")
        t.addWidget(titulo)
        sub = QLabel("Sistema de control de inventarios\nSQL Server · PostgreSQL")
        sub.setObjectName("subtitulo")
        t.addWidget(sub)
        capa.addWidget(tarjeta)
        capa.addStretch()
        return tablero

    # ---------- Lado derecho: formulario ----------
    def panel_formulario(self):
        contenedor = QWidget()
        v = QVBoxLayout(contenedor)
        v.setContentsMargins(56, 40, 56, 40)
        v.addStretch()

        titulo = QLabel("ENTRAR")
        titulo.setObjectName("titulo")
        v.addWidget(titulo)
        sub = QLabel("Escribe tu usuario del sistema.")
        sub.setObjectName("subtitulo")
        v.addWidget(sub)
        v.addSpacing(18)

        self.motor = QComboBox()
        self.motor.addItems(["PostgreSQL", "SQL Server"])
        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("admin")
        self.clave = QLineEdit()
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave.returnPressed.connect(self.entrar)

        for texto, campo in (("BASE DE DATOS", self.motor), ("USUARIO", self.usuario),
                             ("CONTRASEÑA", self.clave)):
            etiqueta = QLabel(texto)
            etiqueta.setObjectName("seccion")
            v.addWidget(etiqueta)
            v.addWidget(campo)
            v.addSpacing(10)

        self.error = QLabel("")
        self.error.setStyleSheet(f"color: {ROJO};")
        self.error.setWordWrap(True)
        v.addWidget(self.error)

        self.boton = QPushButton("ENTRAR  ▶")
        self.boton.setObjectName("primario")
        self.boton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton.clicked.connect(self.entrar)
        v.addWidget(self.boton)
        v.addStretch()
        return contenedor

    # ---------- Al presionar ENTRAR ----------
    def entrar(self):
        self.error.setText("")

        # 1. Crear la conexión según el motor elegido
        if self.motor.currentText() == "PostgreSQL":
            conexion = ConexionPostgres()
        else:
            conexion = ConexionSqlServer()

        if conexion.Crear_conexion() is None:
            self.error.setText("No se pudo conectar. Revisa el archivo .env y que el servidor "
                               f"esté encendido.\n{conexion.ERROR or ''}")
            return

        # 2. Revisar usuario y contraseña (SELECT en la tabla usuarios)
        bd = Consultas(conexion)
        usuario, mensaje = bd.iniciar_sesion(self.usuario.text().strip(), self.clave.text())
        if usuario is None:
            bd.cerrar()
            self.error.setText(mensaje)
            return

        # 3. Abrir la ventana principal y ocultar el login
        from ui_principal import VentanaPrincipal
        self.principal = VentanaPrincipal(bd, self.motor.currentText(), usuario, self)
        self.principal.show()
        self.hide()

    def reiniciar(self):
        """Se llama al cerrar sesión."""
        self.clave.clear()
        self.error.setText("")
        self.show()
