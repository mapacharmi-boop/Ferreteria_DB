# -*- coding: utf-8 -*-
"""
Conexión a la base de datos: PostgreSQL y SQL Server en un solo archivo.

Las dos clases hacen exactamente lo mismo, solo cambia el driver y la
cadena de conexión:
    1. __init__           -> lee los datos de conexión del archivo .env
    2. Crear_conexion     -> abre la conexión
    3. Ejecutar_consulta  -> ejecuta un SQL y regresa la respuesta en JSON
    4. Cerrar_conexion    -> cierra la conexión
"""
import json
import os
from dotenv import load_dotenv

load_dotenv()


# ============================================================
#  POSTGRESQL
# ============================================================
class ConexionPostgres():

    # Así se escriben los parámetros en PostgreSQL:  WHERE id = %s
    MARCADOR = "%s"

    # 1. CONSTRUCTOR
    def __init__(self):
        self.SERVER = os.environ.get("PG_HOST", "localhost")
        self.PORT = os.environ.get("PG_PORT", "5432")
        self.DATABASE_NAME = os.environ.get("PG_DB", "ferreteria_db")
        self.USER = os.environ.get("PG_USER", "postgres")
        self.PASSWORD = os.environ.get("PG_PASSWORD", "")

        self.CNX = None     # Gestionar la conexion
        self.CURSOR = None  # Gestionar las consultas
        self.ERROR = None   # Texto del último error al conectar (lo muestra el login)

    # 2. METODO PARA CREAR LA CONEXION
    def Crear_conexion(self):
        try:
            import psycopg2  # aquí para no necesitar el driver del otro motor

            # client_encoding=WIN1252 evita el UnicodeDecodeError cuando
            # PostgreSQL en Windows manda mensajes con acentos
            cadena_conexion = (
                f"host={self.SERVER} "
                f"port={self.PORT} "
                f"dbname={self.DATABASE_NAME} "
                f"user={self.USER} "
                f"password={self.PASSWORD} "
                f"client_encoding=WIN1252"
            )
            self.CNX = psycopg2.connect(cadena_conexion)
            self.CNX.set_client_encoding("UTF8")
            self.CURSOR = self.CNX.cursor()
            self.ERROR = None
            print(f"Conectado al servidor {self.SERVER}")
            return self.CNX

        except UnicodeDecodeError as e:
            # Muestra el mensaje real del servidor si aun asi falla
            self.ERROR = e.object.decode("latin-1")
            print(f"Error al conectarse al servidor {self.SERVER}:", self.ERROR)
            self.CNX = None
            self.CURSOR = None
            return None

        except Exception as e:
            self.ERROR = str(e)
            print(f"Error al conectarse al servidor {self.SERVER}:", self.ERROR)
            self.CNX = None
            self.CURSOR = None
            return None

    # 3. METODO PARA REALIZAR LAS CONSULTAS SQL A LA BASE DE DATOS
    def Ejecutar_consulta(self, sql, parametros=None):
        try:
            # Si no hay conexión, intento abrirla
            if self.CNX is None and self.Crear_conexion() is None:
                return json.dumps(
                    {
                        "estado": False,
                        "mensaje": "No fue posible establecer la conexión",
                        "error": self.ERROR
                    },
                    ensure_ascii=False
                )

            # Ejecutar consulta
            if parametros:
                self.CURSOR.execute(sql, parametros)
            else:
                self.CURSOR.execute(sql)

            # Identificar operación (primera palabra del SQL)
            tipo = sql.strip().split()[0].upper()

            if tipo == "SELECT":
                # Nombres de las columnas
                columnas = []
                for columna in self.CURSOR.description:
                    columnas.append(columna[0])
                # Cada fila se convierte en un diccionario {columna: valor}
                registros = []
                for fila in self.CURSOR.fetchall():
                    registros.append(dict(zip(columnas, fila)))
                respuesta = {
                    "estado": True,
                    "tipo": tipo,
                    "registros": registros
                }
            else:
                # INSERT, UPDATE, DELETE...
                filas = self.CURSOR.rowcount  # Numero de registros afectados
                self.CNX.commit()             # Guarda los cambios
                respuesta = {
                    "estado": True,
                    "tipo": tipo,
                    "mensaje": "Operación realizada correctamente",
                    "filas_afectadas": filas
                }

            # default=str: si no sabe convertir algo (fechas, decimales), usa str()
            # ensure_ascii=False: para los acentos
            return json.dumps(respuesta, default=str, ensure_ascii=False)

        # CUALQUIER ERROR (llave foránea, SQL mal escrito, etc.)
        except Exception as e:
            if self.CNX:
                self.CNX.rollback()  # Deshace lo que no alcanzó a guardarse
            return json.dumps(
                {
                    "estado": False,
                    "mensaje": "No se pudo completar la operación",
                    "error": str(e)
                },
                ensure_ascii=False
            )

    # 4. METODO PARA CERRAR LA CONEXION DE LA BASE DE DATOS
    def Cerrar_conexion(self):
        try:
            if self.CURSOR:
                self.CURSOR.close()
                self.CURSOR = None
            if self.CNX:
                self.CNX.close()
                self.CNX = None
            print(f"Se ha cerrado la conexion al servidor {self.SERVER}")
            return True
        except Exception as e:
            print("Error al desconectarse del servidor de base de datos:", e)
            return False


# ============================================================
#  SQL SERVER
# ============================================================
class ConexionSqlServer():

    # Así se escriben los parámetros en SQL Server:  WHERE id = ?
    MARCADOR = "?"

    # 1. CONSTRUCTOR
    def __init__(self):
        self.SERVER = os.environ.get("SQL_SERVER", "localhost")
        self.DATABASE_NAME = os.environ.get("SQL_DB", "ferreteria_db")
        self.USER = os.environ.get("SQL_USER", "sa")
        self.PASSWORD = os.environ.get("SQL_PASSWORD", "")

        self.CNX = None     # Gestionar la conexion
        self.CURSOR = None  # Gestionar las consultas
        self.ERROR = None   # Texto del último error al conectar (lo muestra el login)

    # 2. METODO PARA CREAR LA CONEXION
    def Crear_conexion(self):
        try:
            import mssql_python  # aquí para no necesitar el driver del otro motor

            cadena_conexion = (
                f"SERVER={self.SERVER};"
                f"DATABASE={self.DATABASE_NAME};"
                f"UID={self.USER};"
                f"PWD={self.PASSWORD};"
                "Encrypt=yes;"
                "TrustServerCertificate=yes;"
            )
            self.CNX = mssql_python.connect(cadena_conexion)
            self.CURSOR = self.CNX.cursor()
            self.ERROR = None
            print(f"Conectado al servidor {self.SERVER}")
            return self.CNX

        except Exception as e:
            self.ERROR = str(e)
            print(f"Error al conectarse al servidor {self.SERVER}:", self.ERROR)
            self.CNX = None
            self.CURSOR = None
            return None

    # 3. METODO PARA REALIZAR LAS CONSULTAS SQL A LA BASE DE DATOS
    def Ejecutar_consulta(self, sql, parametros=None):
        try:
            # Si no hay conexión, intento abrirla
            if self.CNX is None and self.Crear_conexion() is None:
                return json.dumps(
                    {
                        "estado": False,
                        "mensaje": "No fue posible establecer la conexión",
                        "error": self.ERROR
                    },
                    ensure_ascii=False
                )

            # Ejecutar consulta
            if parametros:
                self.CURSOR.execute(sql, parametros)
            else:
                self.CURSOR.execute(sql)

            # Identificar operación (primera palabra del SQL)
            tipo = sql.strip().split()[0].upper()

            if tipo == "SELECT":
                # Nombres de las columnas
                columnas = []
                for columna in self.CURSOR.description:
                    columnas.append(columna[0])
                # Cada fila se convierte en un diccionario {columna: valor}
                registros = []
                for fila in self.CURSOR.fetchall():
                    registros.append(dict(zip(columnas, fila)))
                respuesta = {
                    "estado": True,
                    "tipo": tipo,
                    "registros": registros
                }
            else:
                # INSERT, UPDATE, DELETE...
                filas = self.CURSOR.rowcount  # Numero de registros afectados
                self.CNX.commit()             # Guarda los cambios
                respuesta = {
                    "estado": True,
                    "tipo": tipo,
                    "mensaje": "Operación realizada correctamente",
                    "filas_afectadas": filas
                }

            # default=str: si no sabe convertir algo (fechas, decimales), usa str()
            # ensure_ascii=False: para los acentos
            return json.dumps(respuesta, default=str, ensure_ascii=False)

        # CUALQUIER ERROR (llave foránea, SQL mal escrito, etc.)
        except Exception as e:
            if self.CNX:
                self.CNX.rollback()  # Deshace lo que no alcanzó a guardarse
            return json.dumps(
                {
                    "estado": False,
                    "mensaje": "No se pudo completar la operación",
                    "error": str(e)
                },
                ensure_ascii=False
            )

    # 4. METODO PARA CERRAR LA CONEXION DE LA BASE DE DATOS
    def Cerrar_conexion(self):
        try:
            if self.CURSOR:
                self.CURSOR.close()
                self.CURSOR = None
            if self.CNX:
                self.CNX.close()
                self.CNX = None
            print(f"Se ha cerrado la conexion al servidor {self.SERVER}")
            return True
        except Exception as e:
            print("Error al desconectarse del servidor de base de datos:", e)
            return False


# Prueba rápida:  python conexion.py
if __name__ == '__main__':
    cnn = ConexionPostgres()   # cambia por ConexionSqlServer() para probar SQL Server
    cnn.Crear_conexion()
    result = cnn.Ejecutar_consulta("SELECT * FROM categorias ORDER BY id_categoria")
    cnn.Cerrar_conexion()
    # Impresion de 1 en 1
    datos = json.loads(result)
    if datos["estado"]:
        for r in datos["registros"]:
            print(r)
    else:
        print(datos)