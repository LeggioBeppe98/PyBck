from dataclasses import dataclass, asdict
import re
import json
import os

@dataclass
class BackupConfig:
    backup_drive: str # Porta del  drive di backup
    backup_root: str # Cartella radice del backup
    source_drives: list # Elenco delle unità sorgente da includere nel backup
    user_folders: list # Elenco delle cartelle utente da includere nel backup
    retention_days: int # Numero di giorni per mantenere i backup            

    def __post_init__(self):
        self.validate()

    def validate(self):
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
        
        if self.retention_days <= 1 or self.retention_days > 6:
            raise ValueError("Retention days Deve essere maggiore di 1 e minore di 7.")
    
    def save(self, filepath="config.json"):
        with open(filepath, "w") as file:
            json.dump(asdict(self), file, indent=2,ensure_ascii=False)  # Leggibile
        
    @classmethod
    def load(cls, filepath="config.json"):
        """Carica configurazione da file JSON."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File di configurazione non trovato: {filepath}")
        
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        return cls(**data)
    
    @staticmethod
    def file_exists(filepath) -> bool:
        if not os.path.exists(filepath):
            return False
        return True