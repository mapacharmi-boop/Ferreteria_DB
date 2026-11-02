# Sistema de inventario · Ferretería

Taller de Bases de Datos · TecNM Campus Jiquilpan · Arturo Sánchez Encina

## Cómo ejecutar

```
pip install -r requirements.txt
python main.py
```

Usuario: `admin` · Contraseña: `admin123` (se crea con `usuarios.sql`).
Los datos de conexión van en `.env` (copia `.env.example` y pon tus contraseñas). El `.env` NO se sube a GitHub.

## ¿Dónde se hace cada cosa?

| Archivo | Qué hace |
|---|---|
| `conpost.py` | Clase `ConexionPostgres`: `Crear_conexion`, `Ejecutar_consulta`, `Cerrar_conexion` (psycopg2) |
| `consql.py` | Clase `ConexionSqlServer`: los mismos tres métodos (mssql_python) |
| `consultas.py` | **Todo el SQL**: login, CRUD de las 6 tablas maestras y consultas del dashboard |
| `seguridad.py` | Cifrado de contraseñas (PBKDF2) para la tabla `usuarios` |
| `main.py` | Arranque: abre la ventana de login |
| `ui_login.py` | Ventana de login. Aquí se **crea la conexión** según el motor elegido |
| `ui_principal.py` | Menú principal: Archivo · **Catálogos** · Ayuda, y barra lateral |
| `ui_catalogo.py` | Pantalla de cada catálogo: Insertar / Actualizar / Eliminar / Consultar |
| `ui_dashboard.py` | Tarjetas y gráficas con las consultas del entregable 2 |
| `estilos.py` | **Solo apariencia**: colores, letras, QSS, marquesina |
| `fuentes/` | Letras Silkscreen y Space Mono (licencia OFL) |
| `*.sql` | Scripts de la base de datos para PostgreSQL y SQL Server, y la tabla `usuarios` |

## Recorrido de una operación (ejemplo: insertar categoría)

1. Clic en **+ INSERTAR** (`ui_catalogo.py` → `PaginaCatalogo.insertar`)
2. Se abre el formulario y se juntan los datos (`DialogoRegistro.datos`)
3. Se llama `bd.categorias_insertar(datos)` (`consultas.py`), que arma el `INSERT`
4. Ese SQL se manda a `Ejecutar_consulta` de `conpost.py` o `consql.py`
5. La respuesta (JSON con `estado`, `mensaje`…) regresa y se recarga la tabla
