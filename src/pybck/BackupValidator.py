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
    error : str
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.validate = False
        self.error = None
    
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
            # Costruisci il percorso CORRETTO: C:\Users\<tuonome>\Downloads
            user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Default")
            folder_path = Path(user_profile) / folder
            
            logger.debug(LOG_CLASSE + f"Controllo: {folder_path}")
            
            if not folder_path.exists():
                logger.debug(LOG_CLASSE + f"Cartella utente non esiste: {folder}")
                return False  # Appena una manca, ritorna False
        
        logger.debug(LOG_CLASSE + "Tutte le cartelle utente esistono")
        return True  # Solo se TUTTE esistono
    
    def has_sufficient_space(self, approx_os_space) -> bool:
        logger.debug(LOG_CLASSE + "has_sufficient_space - Inizio has_sufficient_space")  
        #per ogni disco diverso da C calcolo lo spazio totale da backuppare
        used_space = 0
        free_space = 0 
        MARGIN = 1.15  # <<< AGGIUNGI: il tuo margine di sicurezza originale
        for drive in self.config.source_drives:
            drive_path = Path(drive + "\\") 
            if drive_path.exists() :
                    
                    if drive_path.drive == "C:":
                        used_space += (psutil.disk_usage(drive_path)).used / 1024**3 - approx_os_space  # Spazio in GB
                    else:
                        used_space += (psutil.disk_usage(drive_path)).used / 1024**3
                    
                    logger.debug(LOG_CLASSE + f"Spazio da backuppare sul drive {drive} (GB): {used_space}")  
            else :
                logger.debug(LOG_CLASSE + f"Unità sorgente non esiste durante il calcolo spazio: {drive}")  
                return False
                
                
        logger.debug(LOG_CLASSE + f"Spazio totale da backuppare (GB): {used_space}")    
        # Controlla lo spazio disponibile sul drive di backup
        backup_drive_path = Path(self.config.backup_drive + "\\")    

        if backup_drive_path.exists():
            free_space = (psutil.disk_usage(backup_drive_path)).free / 1024**3  # Spazio libero in GB
        else :
            logger.debug(LOG_CLASSE + f"Drive di backup non esiste durante il calcolo spazio: {self.config.backup_drive}")  
            return False

        if free_space >= (used_space * MARGIN):
            logger.debug(LOG_CLASSE + f"has_sufficient_space - Spazio sufficiente disponibile Spazio da copiare / spazio libero {used_space} / {free_space}")
            return True 
        else:
            logger.debug(LOG_CLASSE + f"has_sufficient_space - Spazio insufficiente disponibile Spazio da copiare / spazio libero {used_space} / {free_space}")
            return False    
        
    def can_perform_backup(self, approx_os_space):
        logger.debug(LOG_CLASSE + "can_perform_backup - Inizio can_perform_backup") 
    
        # Lista di controlli in sequenza logica
        checks = [
            (self.is_drive_connected, [self.config.backup_drive], "Drive di backup non connesso"),
            (self.validate_sources_exist, [], "Una o più sorgenti non esistono"),
            (self.validate_user_folders_exist, [], "Una o più cartelle utente non esistono"),
            (self.has_sufficient_space, [approx_os_space], "Spazio insufficiente sul drive di backup")
        ]   
        
        for check_func, check_args, error_msg in checks:
            if not check_func(*check_args):
                logger.error(f"{LOG_CLASSE} {error_msg}")
                self._last_error = error_msg  # Memorizza l'errore per eventuale consultazione
                return False
        
        logger.info(f"{LOG_CLASSE}✅ Tutti i controlli superati")
        return True