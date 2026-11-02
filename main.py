"""
ARRANQUE DEL PROGRAMA.   Ejecutar:   python main.py

Orden de los archivos:
    main.py         -> abre la ventana de login
    ui_login.py     -> crea la conexión (conpost.py o consql.py) y revisa el usuario
    ui_principal.py -> menú principal (Archivo · Catálogos · Ayuda) y barra lateral
    ui_catalogo.py  -> pantallas de Insertar / Actualizar / Eliminar / Consultar
    ui_dashboard.py -> gráficas y tarjetas
    consultas.py    -> TODO el SQL del sistema
    estilos.py      -> SOLO colores, letras y apariencia
"""
import sys

from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication

from estilos import aplicar_estilo
from ui_login import VentanaLogin

load_dotenv()   # lee el archivo .env (servidor, usuario y contraseña de la BD)

app = QApplication(sys.argv)
aplicar_estilo(app)
ventana = VentanaLogin()
ventana.show()
sys.exit(app.exec())
