from dataclasses import dataclass, asdict
# Questa classe gestisce la validazione delle condizioni per effettuare un backup
# Verifica quindi: che il dispositivo sia colllegato, che la cartella di backup esista, che le cartelle utente esistano
# e che ci sia spazio sufficiente sul drive di backup.

from re import match
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from pybck.BackupConfig import BackupConfig
from pybck import logger
LOG_CLASSE = "[BackupCleaner] - "


class BackupCleaner:
    cleanedOld : bool
    cleanedFailed : bool
    error : str
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.cleanedOld = False
        self.cleanedFailed = False
        self.error = None
    
    def clean_old_backups(self):
        logger.debug(LOG_CLASSE + "clean_old_backups - Inizio clean_old_backups")  
        TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
        patternTimestamp = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$"
        
        # Calcolo la lista dei backup
        listFoldersBackups = self._getListBackups(patternTimestamp)
        sizeList = len(listFoldersBackups)
        
        if sizeList > self.config.keep_last_n :
            # Ordino la lista dal più recente al più vecchio
            listFoldersBackups.sort(key=lambda x: datetime.strptime(x, TIMESTAMP_FORMAT), reverse=True)
            
            # identifico la sottolista da eliminare
            folders_to_delete = listFoldersBackups[self.config.keep_last_n:]
            
            # Eseguo pulizia
            try:
                for folder_name in folders_to_delete:
                    pathBackupTmp = Path(self.config.backup_drive) / self.config.backup_root / folder_name
                    if pathBackupTmp.exists() and pathBackupTmp.is_dir() :
                        shutil.rmtree(pathBackupTmp)

                self.cleanedOld = True
                logger.info(LOG_CLASSE + "Pulizia dei vecchi backup eseguita con successo.")
            except Exception as e:
                logger.error(LOG_CLASSE + f"Errore durante la pulizia dei vecchi backup: {e}")
                self.error = f"Errore durante la pulizia dei vecchi backup: {e}"
                self.cleanedOld = False
        
        logger.debug(LOG_CLASSE + "clean_old_backups - Fine clean_old_backups")
        
    def clean_failed_backups(self):
        logger.debug(LOG_CLASSE + "clean_failed_backups - Inizio clean_failed_backups")  
        TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
        patternTmpFolder = r"^\.tmp_backup_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$"
        
        # Calcolo la lista dei backup
        listFoldersBackups = self._getListBackups(patternTmpFolder)
        sizeList = len(listFoldersBackups)
        if sizeList > 0 :
            # Eseguo pulizia
            try:
                for folder in listFoldersBackups :
                    pathBackupTmp = (Path(self.config.backup_drive)/self.config.backup_root / folder)
                    if pathBackupTmp.exists() and pathBackupTmp.is_dir() :
                        shutil.rmtree(pathBackupTmp)

                self.cleanedFailed = True
                logger.info(LOG_CLASSE + "Pulizia dei backup falliti eseguita con successo.")
            except Exception as e:
                logger.error(LOG_CLASSE + f"Errore durante la pulizia dei backup falliti: {e}")
                self.error = f"Errore durante la pulizia dei backup falliti: {e}"
                self.cleanedFailed = False
    
        logger.debug(LOG_CLASSE + "clean_failed_backups - Fine clean_failed_backups")
    
    def _getListBackups(self, pattern) -> List:
        # Crea lista di cartelle dei backup effettuati
        listFolders = []
        backup_base_path = Path(self.config.backup_drive) / self.config.backup_root
        
        for item in backup_base_path.iterdir():
            if item.is_dir():
                # Controlla se il nome della cartella corrisponde al formato di un backup
                if match(pattern, item.name):
                    listFolders.append(item.name)
        return listFolders
