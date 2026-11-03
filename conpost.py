import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Lee el archivo .env (usuario, contraseña, servidor...)


class ConexionPostgres():

    # En PostgreSQL los parámetros de una consulta se escriben con %s
    # Ejemplo:  SELECT * FROM clientes WHERE id_cliente = %s
    MARCADOR = "%s"
    MOTOR = "PostgreSQL"          # nombre que se muestra en la ventana

    # 1. CONSTRUCTOR
    def __init__(self):
        # Datos de conexión que vienen del archivo .env
        self.SERVER = os.environ.get("PG_HOST")
        self.PORT = os.environ.get("PG_PORT", "5432")
        self.DATABASE_NAME = os.environ.get("PG_DB")
        self.USER = os.environ.get("PG_USER")
        self.PASSWORD = os.environ.get("PG_PASSWORD")

        self.CNX = None     # Gestionar la conexion
        self.CURSOR = None  # Gestionar las consultas
        self.ERROR = None   # Guarda el último error al conectar (lo muestra el login)

    # 2. METODO PARA CREAR LA CONEXION
    def Crear_conexion(self):
        # Crear la cadena de conexion
        try:
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
            print(f"Conectado al servidor {self.SERVER}")
            return self.CNX

        except UnicodeDecodeError as e:
            # Muestra el mensaje real del servidor si aun asi falla
            print(f"Error al conectarse al servidor {self.SERVER} de base de datos")
            self.ERROR = e.object.decode("latin-1")
            print("Mensaje real del servidor:", self.ERROR)
            self.CNX = None
            self.CURSOR = None
            return None

        except psycopg2.Error as e:
            print(f"Error al conectarse al servidor {self.SERVER} de base de datos")
            print(e)
            self.ERROR = str(e)
            self.CNX = None
            self.CURSOR = None
            return None

    # 3. METODO PARA REALIZAR LAS CONSULTAS SQL A LA BASE DE DATOS
    def Ejecutar_consulta(self, sql, parametros=None):
        try:
            # Verificar conexión
            if self.CNX is None:
                # Intento conectarme
                if self.Crear_conexion() is None:
                    return json.dumps(
                        {
                            "estado": False,
                            "mensaje": "No fue posible establecer la conexión"
                        },
                        ensure_ascii=False
                    )

            # Ejecutar consulta
            # Los valores van en "parametros" y NO pegados al texto del SQL
            # (así se evita la inyección SQL)
            if parametros:
                self.CURSOR.execute(
                    sql,
                    parametros
                )
            else:
                self.CURSOR.execute(sql)

            # Identificar operación (la primera palabra del SQL)
            tipo = sql.strip().split()[0].upper()
            # SELECT
            if tipo == "SELECT":
                # Obtener nombres de columnas
                columnas = []
                for columna in self.CURSOR.description:
                    columnas.append(columna[0])
                # Obtener registros
                registros = self.CURSOR.fetchall()
                resultado = []
                for registro in registros:
                    # Cada fila se convierte en un diccionario {columna: valor}
                    fila = {}
                    for i, valor in enumerate(registro):
                        fila[columnas[i]] = valor
                    resultado.append(fila)

                return json.dumps(
                    {
                        "estado": True,
                        "tipo": "SELECT",
                        "registros": resultado
                    },
                    default=str,  # Si no sabe como convertir, aplicale la funcion str()
                    ensure_ascii=False  # Para caracteres latinoamericanos
                )
            # INSERT
            elif tipo == "INSERT":
                filas = self.CURSOR.rowcount  # Obtiene el numero de registros afectados
                self.CNX.commit()  # Comete la transacción
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": "INSERT",
                        "mensaje": "Registro insertado correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )
            # UPDATE
            elif tipo == "UPDATE":
                filas = self.CURSOR.rowcount
                self.CNX.commit()
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": "UPDATE",
                        "mensaje": "Registro actualizado correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )
            # DELETE
            elif tipo == "DELETE":
                filas = self.CURSOR.rowcount
                self.CNX.commit()
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": "DELETE",
                        "mensaje": "Registro eliminado correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )
            # OTRAS OPERACIONES
            else:
                filas = self.CURSOR.rowcount
                self.CNX.commit()
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": tipo,
                        "mensaje": "Consulta ejecutada correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )
        # ERROR DE INTEGRIDAD (llave repetida, llave foránea, CHECK...)
        except psycopg2.IntegrityError as e:
            if self.CNX:
                self.CNX.rollback()  # Deshace lo que quedó a medias
            return json.dumps(
                {
                    "estado": False,
                    "tipo": "IntegrityError",
                    "mensaje": "Violación de integridad en la base de datos",
                    "error": str(e)
                },
                ensure_ascii=False
            )
        # ERROR DE PROGRAMACIÓN SQL (SQL mal escrito, tabla que no existe...)
        except psycopg2.ProgrammingError as e:
            if self.CNX:
                self.CNX.rollback()
            return json.dumps(
                {
                    "estado": False,
                    "tipo": "ProgrammingError",
                    "mensaje": "Error en la consulta SQL",
                    "error": str(e)
                },
                ensure_ascii=False
            )
        # ERROR GENERAL DE LA BASE DE DATOS
        except psycopg2.Error as e:
            if self.CNX:
                self.CNX.rollback()
            return json.dumps(
                {
                    "estado": False,
                    "tipo": "DatabaseError",
                    "mensaje": "Error en la base de datos",
                    "error": str(e)
                },
                ensure_ascii=False
            )
        # ERROR DE PYTHON
        except Exception as e:
            if self.CNX:
                self.CNX.rollback()
            return json.dumps(
                {
                    "estado": False,
                    "tipo": "Error",
                    "mensaje": "Error inesperado",
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
        except psycopg2.Error as e:
            print("Error al desconectarse del servidor de base de datos")
            print(e)
            return False


# Prueba rápida: python conpost.py
if __name__ == '__main__':
    cnn = ConexionPostgres()
    cnn.Crear_conexion()
    sql_select = """
                    SELECT p.nombre, c.nombre AS categoria, p.precio_venta
                    FROM productos p
                    INNER JOIN categorias c ON p.id_categoria = c.id_categoria
                    ORDER BY p.nombre;
                """
    result = cnn.Ejecutar_consulta(sql_select)
    cnn.Cerrar_conexion()
    # Impresion de 1 en 1
    datos = json.loads(result)
    if datos["estado"]:
        for r in datos["registros"]:
            print(r)
    else:
        print(datos)
