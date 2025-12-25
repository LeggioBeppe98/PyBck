"""PyBck - Professional Backup Tool"""
__version__ = "0.1.0"

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE_PATH = "logs/backup.log"

# Creo la cartella dei log se non esiste
os.makedirs("logs", exist_ok=True)

# Creo il logger principale
logger = logging.getLogger("PyBck")
logger.setLevel(logging.DEBUG)  # livello debug globale

# Formattazione dei log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Handler per il file con rotazione
file_handler = RotatingFileHandler(
    LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=1
)
file_handler.setFormatter(formatter)

# Handler per la console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Aggiungo gli handler al logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
