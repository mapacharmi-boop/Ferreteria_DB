"""
Contraseñas seguras.

La contraseña NUNCA se guarda tal cual en la base de datos. Se guarda un "hash":
un texto que se calcula a partir de la contraseña y del que no se puede regresar
a la contraseña original.

Formato que se guarda en la columna usuarios.contrasena:
    pbkdf2_sha256$200000$<sal>$<hash>
    - pbkdf2_sha256 : el algoritmo
    - 200000        : cuántas veces se repite el cálculo (lo hace lento para los atacantes)
    - sal           : 16 bytes al azar, distintos para cada usuario
    - hash          : el resultado

Para sacar el hash de una contraseña nueva:   python seguridad.py MiClave
"""
import hashlib
import hmac
import os
import sys


def generar_hash(contrasena, iteraciones=200000):
    sal = os.urandom(16)  # 16 bytes al azar
    h = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), sal, iteraciones)
    return f"pbkdf2_sha256${iteraciones}${sal.hex()}${h.hex()}"


def verificar_contrasena(contrasena, guardado):
    """Vuelve a calcular el hash con la MISMA sal y lo compara con el guardado."""
    try:
        _, iteraciones, sal, esperado = guardado.split("$")
        h = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"),
                                bytes.fromhex(sal), int(iteraciones))
        return hmac.compare_digest(h.hex(), esperado)
    except (ValueError, AttributeError):
        return False


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print(generar_hash(sys.argv[1]))
    else:
        print("Uso: python seguridad.py MiClave")
