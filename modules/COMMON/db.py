# modules/COMMON/db.py
import oracledb
import sys
import os

# --- Lógica de importación de config (centralizada) ---
# Así no tienes que poner el sys.path.append en cada archivo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
try:
    import config
except ImportError:
    # Fallback o manejo de error
    import config

def get_db_connection():
    """
    Retorna una conexión a la base de datos Oracle.
    Usada por todos los módulos.
    """
    return oracledb.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        dsn=config.DB_DSN
    )