"""
Ventana de inicio de sesión.

Aquí se CREAN LAS CONEXIONES a la base de datos:
    - PostgreSQL  -> ConexionPostgres()   (archivo conpost.py)
    - SQL Server  -> ConexionSqlServer()  (archivo consql.py)

Modos:
    - Mixto: se abren las DOS conexiones y cada módulo usa la que diga modulos.py
    - Solo PostgreSQL / Solo SQL Server: todos los módulos usan la misma

Luego se revisa el usuario con iniciar_sesion() (archivo consultas.py).
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget)

from conpost import ConexionPostgres
from consql import ConexionSqlServer
from consultas import Consultas
from estilos import ROJO, Cuadricula, Marquesina
from modulos import MOTOR_DE_CADA_MODULO


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
        sub = QLabel("Ferretería Picazo · Sahuayo\nControl de inventarios · SQL Server + PostgreSQL")
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
        self.motor.addItems(["Mixto (SQL Server + PostgreSQL)", "Solo PostgreSQL", "Solo SQL Server"])
        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("admin")
        self.clave = QLineEdit()
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave.returnPressed.connect(self.entrar)

        for texto, campo in (("MODO DE BASE DE DATOS", self.motor), ("USUARIO", self.usuario),
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
        modo = self.motor.currentText()

        # 1. ¿Qué motores hay que abrir?
        if modo.startswith("Mixto"):
            motores = ["PostgreSQL", "SQL Server"]
        elif modo == "Solo PostgreSQL":
            motores = ["PostgreSQL"]
        else:
            motores = ["SQL Server"]

        # 2. Crear una conexión por cada motor
        abiertas = {}                       # "PostgreSQL" -> Consultas(...)
        for motor in motores:
            if motor == "PostgreSQL":
                conexion = ConexionPostgres()
            else:
                conexion = ConexionSqlServer()

            if conexion.Crear_conexion() is None:
                for bd in abiertas.values():   # cerrar las que sí se abrieron
                    bd.cerrar()
                self.error.setText(f"No se pudo conectar a {motor}. Revisa el archivo .env y que "
                                   f"el servidor esté encendido.\n{conexion.ERROR or ''}")
                return
            abiertas[motor] = Consultas(conexion)

        # 3. Decidir qué conexión usa cada módulo
        bases = {}
        for modulo, motor in MOTOR_DE_CADA_MODULO.items():
            if len(motores) == 2:
                bases[modulo] = abiertas[motor]        # mixto: lo que diga modulos.py
            else:
                bases[modulo] = abiertas[motores[0]]   # un solo motor para todo

        # 4. Revisar usuario y contraseña (SELECT en la tabla usuarios)
        usuario, mensaje = bases["login"].iniciar_sesion(self.usuario.text().strip(), self.clave.text())
        if usuario is None:
            for bd in abiertas.values():
                bd.cerrar()
            self.error.setText(mensaje)
            return

        # 5. Abrir la ventana principal y ocultar el login
        from ui_principal import VentanaPrincipal
        nombre_modo = "Mixto" if len(motores) == 2 else motores[0]
        self.principal = VentanaPrincipal(bases, list(abiertas.values()), nombre_modo, usuario, self)
        self.principal.show()
        self.hide()

    def reiniciar(self):
        """Se llama al cerrar sesión."""
        self.clave.clear()
        self.error.setText("")
        self.show()
