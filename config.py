# config.py
import os
import oracledb
from dotenv import load_dotenv

# 1. Cargar las variables del archivo .env (si existe)
#    Esto es para desarrollo local. En producción, no existirá
#    y las variables vendrán directamente del sistema.
load_dotenv()

# 2. Leer las variables del entorno (cargadas por load_dotenv() o por el sistema)
#    os.environ.get('NOMBRE_VARIABLE', 'valor_por_defecto')
#    Usar un valor por defecto es opcional pero bueno para desarrollo.

DB_USER = os.environ.get('DB_USER', 'usuario_por_defecto')
DB_PASSWORD = os.environ.get('DB_PASSWORD', None) # 
DB_DSN = os.getenv('DB_DSN')

# --- PRUEBA DE DEPURACIÓN RÁPIDA ---
# Agrega esto temporalmente para ver qué está leyendo:
print(f"DEBUG: Conectando con DSN={DB_DSN}") 
# ------------------------------------

try:
    # Tu código de conexión
    connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    print("¡Conexión exitosa!")
    # ...
except Exception as e:
    print(f"Error al conectar a la base de datos Oracle.")
    print(f"Detalle del error: {e}")