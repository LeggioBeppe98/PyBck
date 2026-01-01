# Questa classe si occupa di effettuare la copia dei dati di backup

"""
# TEMPORANEA (durante copia)
G:\Backup_PC\.tmp_backup_2024-01-22_10-30-45\
├── Disco_C_Backup_2024-01-22_10-30-45\      # Cartelle utente
│   ├── Documents\
│   └── ...
├── Disco_D_Backup_2024-01-22_10-30-45\  # Drive D:
└── Disco_E_Backup_2024-01-22_10-30-45\  # Drive E:

# FINALE (dopo rename)
G:\Backup_PC\2024-01-22_10-30-45\
├── Disco_C_Backup_2024-01-22_10-30-45\
├── Disco_D_Backup_2024-01-22_10-30-45\
└── Disco_E_Backup_2024-01-22_10-30-45\
    
_create_temp_backup_folder() → crea .tmp_backup_TIMESTAMP

_copy_drive(drive_letter) → copia un intero drive

_copy_user_folders() → copia cartelle utente da C:

_finalize_backup() → rinomina .tmp_backup_* in definitiv
    
"""


import subprocess
from datetime import datetime
import os
from pathlib import Path

from pybck.BackupConfig import BackupConfig
from pybck import logger
LOG_CLASSE = "[BackupBuilder] - "


class BackupBuilder:
    executed : bool
    error : str
    timestamp : str
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.executed = False
        self.error = None
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
    def execute_backup(self):
        logger.debug(LOG_CLASSE + "execute_backup - Inizio execute_backup")  
        
        temp_backup_folder = self._create_temp_backup_folder()
        
        for drive in self.config.source_drives:
            logger.debug(LOG_CLASSE + f"execute_backup - Copia drive: {drive}")  
            
            drive_folder = self._create_folder_drive(drive, temp_backup_folder)
            
            try:
                if(drive != 'C'):
                    self._copy_drive(drive, drive_folder)
                    
                else:
                    self._copy_user_folders(drive_folder)

            except Exception as e:
                logger.error(LOG_CLASSE + f"Errore durante la copia del drive {drive}: {e}")
                self.error = f"Errore durante la copia del drive {drive}: {e}"
                self.executed = False
                return  # Esce in caso di errore
    
        
        self.executed = True
        self._finalize_backup(temp_backup_folder)
        logger.info(LOG_CLASSE + "Backup eseguito con successo.")
        logger.debug(LOG_CLASSE + "execute_backup - Fine execute_backup")
    
    def _create_temp_backup_folder(self):

        # Costruisco il percorso della cartella temporanea G:\Backup_PC\.tmp_backup_2024-01-22_10-30-45\
        destination = f"{self.config.backup_drive}\\{self.config.backup_root}\\.tmp_backup_{self.timestamp}"
        
        logger.debug(LOG_CLASSE + f"_create_temp_backup_folder - Creazione cartella temporanea: {destination}")  
        
        # Codice per creare la cartella temporanea  
        Path(destination).mkdir(parents=True, exist_ok=True)
        
        return destination  
    
    def _create_folder_drive(self, drive_letter, temp_backup_folder):
        # Rimuovo i due punti dalla lettera di unità per creare il nome della cartella
        drive_name = drive_letter.replace(":", "")
        
        # Costruisco il percorso della cartella di destinazione per il drive
        destination = f"{temp_backup_folder}\\Disco_{drive_name}_Backup_{self.timestamp}"
        
        logger.debug(LOG_CLASSE + f"_create_folder_drive - Creazione cartella per drive: {destination}")  
        
        # Comando per creare la cartella del drive
        Path(destination).mkdir(parents=True, exist_ok=True)
        
        return destination
    
    def _finalize_backup(self, temp_backup_folder):
        # Codice per rinominare la cartella temporanea in definitiva
        Path(temp_backup_folder).rename(temp_backup_folder.replace(".tmp_backup_", ""))
        
        logger.debug(LOG_CLASSE + f"_finalize_backup - Rinomina cartella temporanea in definitiva: {temp_backup_folder.replace('.tmp_backup_', '')}")
        
    def _copy_drive(self, drive_letter: str, dest_folder: Path):
        logger.debug(LOG_CLASSE + f"_copy_drive - Inizio copia drive {drive_letter} in {dest_folder}")  
        
        robocopy = [
            "robocopy",
            drive_letter + "\\",  # sorgente
            dest_folder,
            "/MIR",                   # Mirror
            "/R:3", "/W:5",           # Retry/Wait  
            "/NP", "/NJH", "/NJS",    # Logging minimo (come in _copy_drive)
            # "/P" progress potrebbe generare output eccessivo
            #logger.LOG_FILE_PATH
        ]
        
        result = subprocess.run(
            robocopy,
            capture_output=True,
            text=True,
            shell=False,
            encoding='utf-8',
            errors='ignore'  
        )
        
        if result.returncode >= 8:
            raise Exception(f"Robocopy failed with code {result.returncode}: {result.stderr}")
        elif result.returncode > 1:
            logger.warning(f"Robocopy warnings (code {result.returncode}): {result.stdout[:500]}")
            
        logger.debug(LOG_CLASSE + f"_copy_drive - Fine copia drive {drive_letter} in {dest_folder}")

    def _copy_user_folders(self, dest_folder: Path):
        logger.debug(LOG_CLASSE + f"_copy_user_folders - Inizio copia cartelle utente in {dest_folder}")
        path_source = os.environ.get("USERPROFILE", "C:\\Users\\Default")

        for drive in self.config.user_folders:  
            
            source = os.path.join(path_source, drive)
            destination = os.path.join(dest_folder, drive)
            
            Path(destination).mkdir(parents=True, exist_ok=True)
            
            logger.debug(f"{LOG_CLASSE}Copio {source} → {destination}")
            
            robocopy = [
                "robocopy",
                source,  # sorgente
                destination,
                "/MIR",                   # Mirror
                "/R:3", "/W:5",           # Retry/Wait  
                "/NP", "/NJH", "/NJS",    # Logging minimo (come in _copy_drive)
                # "/P" progress potrebbe generare output eccessivo
                #logger.LOG_FILE_PATH
            ]
        
            result = subprocess.run(
                robocopy,
                capture_output=True,
                text=True,
                shell=False,
                encoding='utf-8',
                errors='ignore'
                #logger.LOG_FILE_PATH
            )
            
            if result.returncode >= 8:
                raise Exception(f"Robocopy failed with code {result.returncode}: {result.stderr}")
            elif result.returncode > 1:
                logger.warning(f"Robocopy warnings (code {result.returncode}): {result.stdout[:500]}")
            
        logger.debug(LOG_CLASSE + f"_copy_user_folders - Fine copia cartelle utente in {dest_folder}")