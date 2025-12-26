import pytest
import os

from pathlib import Path
from unittest.mock import patch 
import logging

# Creo un logger
logger = logging.getLogger("PyBck")
logger.setLevel(logging.DEBUG) 

# Importa la tua classe da testare
from pybck.BackupConfig import BackupConfig
from pybck.BackupBuilder import BackupBuilder


def test_create_temp_backup_folder():
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents", "Pictures"],
        retention_days=3
    )
    
    # Crea un'istanza di BackupBuilder
    backup_builder = BackupBuilder(config)
    
    expected_path = f"{config.backup_drive}\\{config.backup_root}\\.tmp_backup_{backup_builder.timestamp}"

    with patch("pybck.BackupBuilder.Path") as mock_path:
        mock_instance = mock_path.return_value
        mock_instance.mkdir.return_value = None

        temp_folder = backup_builder._create_temp_backup_folder()

        # verifica path ritornato
        assert temp_folder == expected_path

        # verifica mkdir chiamato correttamente
        mock_instance.mkdir.assert_called_once_with(
            parents=True,
            exist_ok=True
        )
def test_create_folder_drive():
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents", "Pictures"],
        retention_days=3
    )
    
    # Crea un'istanza di BackupBuilder
    backup_builder = BackupBuilder(config)
    
    temp_backup_folder = f"{config.backup_drive}\\{config.backup_root}\\.tmp_backup_{backup_builder.timestamp}"
    
    drive = "D:"
    expected_folder = f"{temp_backup_folder}\\Disco_D_Backup_{backup_builder.timestamp}"
    
    with patch("pybck.BackupBuilder.Path") as mock_path:
        mock_instance = mock_path.return_value
        mock_instance.mkdir.return_value = None

        drive_folder = backup_builder._create_folder_drive(drive, temp_backup_folder)

        # verifica path ritornato
        assert drive_folder == expected_folder

        # verifica mkdir chiamato correttamente
        mock_instance.mkdir.assert_called_once_with(
            parents=True,
            exist_ok=True
        )
    
def test_finalize_backup():
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["D:"],
        user_folders=["Documents", "Pictures"],
        retention_days=3
    )
    
    # Crea un'istanza di BackupBuilder
    backup_builder = BackupBuilder(config)
    
    temp_backup_folder = f"{config.backup_drive}\\{config.backup_root}\\.tmp_backup_{backup_builder.timestamp}"
    
    with patch("pybck.BackupBuilder.Path") as mock_path:
        mock_instance = mock_path.return_value
        mock_instance.rename.return_value = None
        
        backup_builder._finalize_backup(temp_backup_folder)
        
        # verifica rename chiamato correttamente
        # Parte da mockare: Path(temp_backup_folder).rename(temp_backup_folder.replace(".tmp_backup_", ""))
        mock_instance.rename.assert_called_once_with(
            temp_backup_folder.replace(".tmp_backup_", "")
        )
        
def test_copy_drive_success():
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["D:"],
        user_folders=["Documents", "Pictures"],
        retention_days=3
    )

    # Crea un'istanza di BackupBuilder
    backup_builder = BackupBuilder(config)

    source_drive = "D:"
    dest_folder = f"{config.backup_drive}\\{config.backup_root}\\.tmp_backup_{backup_builder.timestamp}\\Disco_D_Backup_{backup_builder.timestamp}"

    with patch("pybck.BackupBuilder.subprocess") as mock_subprocess:
        mock_subprocess.run.return_value.returncode = 1
        mock_subprocess.run.return_value.stdout = "Successo"
        mock_subprocess.run.return_value.stderr = ""

        backup_builder._copy_drive(source_drive, dest_folder)

        # verifica subprocess.run chiamato correttamente
        mock_subprocess.run.assert_called_once_with(
            ["robocopy", f"{source_drive}\\", dest_folder,
            "/MIR",                   # Mirror
            "/R:3", "/W:5",           # Retry/Wait  
            "/NP", "/NJH", "/NJS"],
            capture_output=True,
            text=True,
            shell=False,
            encoding='utf-8',
            errors='ignore'  
        )    
        
def test_copy_drive_warning(caplog):
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["D:"],
        user_folders=["Documents", "Pictures"],
        retention_days=3
    )

    # Crea un'istanza di BackupBuilder
    backup_builder = BackupBuilder(config)

    source_drive = "D:"
    dest_folder = f"{config.backup_drive}\\{config.backup_root}\\.tmp_backup_{backup_builder.timestamp}\\Disco_D_Backup_{backup_builder.timestamp}"

    with patch("pybck.BackupBuilder.subprocess") as mock_subprocess:
        mock_subprocess.run.return_value.returncode = 2
        mock_subprocess.run.return_value.stdout = "Warning"
        mock_subprocess.run.return_value.stderr = "Warning details"
        
        with caplog.at_level(logging.WARNING):
            backup_builder._copy_drive(source_drive, dest_folder)

        # verifica subprocess.run chiamato correttamente
        mock_subprocess.run.assert_called_once_with(
            ["robocopy", f"{source_drive}\\", dest_folder,
            "/MIR",                   # Mirror
            "/R:3", "/W:5",           # Retry/Wait  
            "/NP", "/NJH", "/NJS"],
            capture_output=True,
            text=True,
            shell=False,
            encoding='utf-8',
            errors='ignore'  
        )  
        
        assert "Robocopy warnings" in caplog.text  

def test_copy_drive_error(caplog):
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["D:"],
        user_folders=["Documents", "Pictures"],
        retention_days=3
    )

    # Crea un'istanza di BackupBuilder
    backup_builder = BackupBuilder(config)

    source_drive = "D:"
    dest_folder = f"{config.backup_drive}\\{config.backup_root}\\.tmp_backup_{backup_builder.timestamp}\\Disco_D_Backup_{backup_builder.timestamp}"

    with patch("pybck.BackupBuilder.subprocess") as mock_subprocess:
        mock_subprocess.run.return_value.returncode = 8
        mock_subprocess.run.return_value.stdout = "Error"
        mock_subprocess.run.return_value.stderr = "Error details"
        
        # Verifica che venga alzata un’eccezione
        with pytest.raises(Exception, match="Robocopy failed"):
            backup_builder._copy_drive(source_drive, dest_folder)

        # verifica subprocess.run chiamato correttamente
        mock_subprocess.run.assert_called_once_with(
            ["robocopy", f"{source_drive}\\", dest_folder,
            "/MIR",                   # Mirror
            "/R:3", "/W:5",           # Retry/Wait  
            "/NP", "/NJH", "/NJS"],
            capture_output=True,
            text=True,
            shell=False,
            encoding='utf-8',
            errors='ignore'  
        )   
        