from dataclasses import dataclass, asdict
import re
import json
import os
from pybck import logger
LOG_CLASSE = "[BackupConfig] - "

@dataclass
class BackupConfig:
    backup_drive: str # Porta del  drive di backup
    backup_root: str # Cartella radice del backup
    source_drives: list # Elenco delle unità sorgente da includere nel backup
    user_folders: list # Elenco delle cartelle utente da includere nel backup
    keep_last_n: int # Numero di giorni per mantenere i backup            

    def __post_init__(self):
        logger.debug(LOG_CLASSE + "__post_init__ - Verifica cartelle utente")
        self.validate()

    def validate(self):
        logger.debug(LOG_CLASSE + "validate - Inizio validate")  
        logger.debug(LOG_CLASSE + "validate - Oggetto cofiguraizone: %s", asdict(self))    
        patternDrive = r'^[A-Z]:$'
        patternPath = r'^[A-Z][a-zA-Z0-9]+$'

        if not self.backup_drive.strip():
            raise ValueError("Backup drive deve essere specificato.")
        else :
            if not re.fullmatch(patternDrive, self.backup_drive):
                raise ValueError("Backup drive deve essere una lettera di unità valida (es. 'G:').")
            
        if not self.backup_root.strip():
            raise ValueError("Backup root deve essere specificato.")
        else :
            if not re.fullmatch(patternPath, self.backup_root):
                raise ValueError("Backup root deve essere solo il nome della cartella valido (es. 'BackupPC').")
        
        if not self.source_drives:
            raise ValueError("Almeno un'unità sorgente deve essere specificata.")
        else:
            for drive in self.source_drives:
                if not re.fullmatch(patternDrive, drive):
                    raise ValueError(f"Unità sorgente non valida: {drive}. Deve essere una lettera di unità valida (es. 'C:').")
        
        if not self.user_folders:
            raise ValueError("Almeno una cartella utente deve essere specificata.")
        
        if self.keep_last_n > 0 and self.keep_last_n < 7:
            raise ValueError("Keep last n Deve essere maggiore di 0 e minore di 7.")
        logger.debug(LOG_CLASSE + "validate - Fine validate")   
    
    def save(self, filepath="config.json"):
        with open(filepath, "w") as file:
            json.dump(asdict(self), file, indent=2,ensure_ascii=False)  # Leggibile
        
    @classmethod
    def load(cls, filepath="config.json"):
        logger.debug(LOG_CLASSE + "load - Inizio load.")   
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File di configurazione non trovato: {filepath}")
        
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
            logger.debug(LOG_CLASSE + "load - Fine load.")   
        
        return cls(**data)
    
    @staticmethod
    def file_exists(filepath) -> bool:
        logger.debug(LOG_CLASSE + "file_exists - Inizio file_exists.")   
        if not os.path.exists(filepath):
            logger.debug(LOG_CLASSE + "file_exists - File non esiste.")
            return False
        logger.debug(LOG_CLASSE + "file_exists - File esiste.")
        return True