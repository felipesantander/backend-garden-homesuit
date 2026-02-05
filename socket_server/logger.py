import logging
import os
from logging.handlers import RotatingFileHandler

# Definir la ruta del archivo de log
LOG_FILE = "socket_server.log"

def setup_logger():
    """Configura un logger que escribe en consola y en un archivo rotativo."""
    logger = logging.getLogger("socket_server")
    logger.setLevel(logging.INFO)

    # Evitar duplicados si se llama varias veces
    if logger.handlers:
        return logger

    # Formato de los logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler para la consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para archivo (rotativo de 5MB, mantiene 3 versiones)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5*1024*1024, backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Instancia global del logger para ser importada
logger = setup_logger()
