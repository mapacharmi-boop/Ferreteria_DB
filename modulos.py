"""
QUÉ BASE DE DATOS USA CADA MÓDULO DEL SISTEMA.

El sistema trabaja con los dos motores al mismo tiempo (modo "Mixto"):
cada módulo guarda y lee sus datos en el motor que diga esta tabla.
Para cambiar un módulo de motor, solo cambia el texto aquí.

Las dos bases tienen las mismas 12 tablas (se crearon con el mismo script),
por eso cualquier módulo puede vivir en cualquiera de las dos.
"""

MOTOR_DE_CADA_MODULO = {
    # Módulo de INVENTARIO -> PostgreSQL
    "categorias": "PostgreSQL",
    "productos": "PostgreSQL",
    "almacenes": "PostgreSQL",
    "dashboard": "PostgreSQL",

    # Módulo de PERSONAS (con quién trata la ferretería) -> SQL Server
    "proveedores": "SQL Server",
    "clientes": "SQL Server",
    "empleados": "SQL Server",
    "login": "SQL Server",          # la tabla usuarios
}
