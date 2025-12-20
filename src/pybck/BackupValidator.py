from dataclasses import dataclass, asdict
# Questa classe gestisce la validazione delle condizioni per effettuare un backup
# Verifica quindi: che il dispositivo sia colllegato, che la cartella di backup esista, che le cartelle utente esistano
# e che ci sia spazio sufficiente sul drive di backup.

import psutil
import os
from pathlib import Path
from typing import List

from pybck.BackupConfig import BackupConfig
from pybck import logger
LOG_CLASSE = "[ValidatorBackup] - "


class BackupValidator:
    validate : bool
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.validate = False
    
    def is_drive_connected(self, drive_letter: str) -> bool:
        logger.debug(LOG_CLASSE + "is_drive_connected - Inizio is_drive_connected")  
        
        if not drive_letter.endswith(":"):
            drive_letter = drive_letter + ":"
        
        partitions = psutil.disk_partitions()
        for partition in partitions:
            if partition.device.startswith(drive_letter):
                logger.debug(LOG_CLASSE + "is_drive_connected - Drive è connesso")
                return True
        logger.debug(LOG_CLASSE + "is_drive_connected - Drive non è connesso")
        return False
    
    def validate_sources_exist(self) -> bool:
        logger.debug(LOG_CLASSE + "validate_sources_exist - Inizio validate_sources_exist")  
        for drive in self.config.source_drives:
            drive_path = Path(drive + "\\")
            if not drive_path.exists():
                logger.debug(LOG_CLASSE + f"validate_sources_exist - Unità sorgente non esiste: {drive}")
                return False
        logger.debug(LOG_CLASSE + "validate_sources_exist - Tutte le unità sorgente esistono")
        return True
    
    def validate_user_folders_exist(self) -> bool:
        logger.debug(LOG_CLASSE + "validate_user_folders_exist - Inizio validate_user_folders_exist")  
        for folder in self.config.user_folders:
            folder_found = False
            for drive in self.config.source_drives:
                folder_path = Path(drive + "\\" + folder)
                if folder_path.exists():
                    folder_found = True
                    break
            if not folder_found:
                logger.debug(LOG_CLASSE + f"validate_user_folders_exist - Cartella utente non esiste: {folder}")
                return False
        logger.debug(LOG_CLASSE + "validate_user_folders_exist - Tutte le cartelle utente esistono")
        return True