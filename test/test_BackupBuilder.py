import pytest
import logging

# Creo un logger
logger = logging.getLogger("PyBck")
logger.setLevel(logging.DEBUG) 

from pathlib import Path
from unittest.mock import Mock, patch 
from datetime import datetime

# Importa la tua classe da testare
from pybck.BackupConfig import BackupConfig
from pybck.BackupBuilder import BackupBuilder


def test_create_temp_backup_folder():
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents", "Pictures"],  # Required
        retention_days=3
    )
    
    backup_builder = BackupBuilder(config)
    expected_path = f"{config.backup_drive}\\{config.backup_root}\\.tmp_backup_{backup_builder.timestamp}"

    with patch.object(Path, 'mkdir') as mock_mkdir:
        temp_folder = backup_builder._create_temp_backup_folder()
        
        assert temp_folder == expected_path
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

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
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["D:"],
        user_folders=["Documents", "Pictures"],
        retention_days=3
    )
    backup_builder = BackupBuilder(config)
    source_drive = "D:"
    dest_folder = f"...{backup_builder.timestamp}..."

    with patch("pybck.BackupBuilder.subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "Successo"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        backup_builder._copy_drive(source_drive, dest_folder)
        
        mock_run.assert_called_once_with(
            ["robocopy", f"{source_drive}\\", dest_folder, "/MIR", "/R:3", "/W:5", "/NP", "/NJH", "/NJS"],
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
        
def test_execute_backup_success():
    """Test del flusso completo con successo"""
    # Configurazione
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["D:", "E:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    # Mock datetime per timestamp fisso
    from datetime import datetime
    fixed_time = datetime(2024, 1, 1, 10, 0, 0)
    
    with patch("pybck.BackupBuilder.datetime") as mock_datetime, \
        patch("pybck.BackupBuilder.subprocess.run") as mock_run, \
        patch.object(Path, 'mkdir') as mock_mkdir, \
        patch.object(Path, 'rename') as mock_rename:
        
        # Mock datetime.now() per timestamp prevedibile
        mock_datetime.now.return_value = fixed_time
        
        # Crea builder con timestamp fisso
        builder = BackupBuilder(config)
        
        # Mock per subprocess.run (robocopy successo)
        mock_result = Mock()
        mock_result.returncode = 1  # Robocopy successo
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Esegui il backup
        builder.execute_backup()
        
        # VERIFICA: Stato finale corretto
        assert builder.executed == True, "Builder dovrebbe essere executed=True"
        assert builder.error is None, "Nessun errore dovrebbe essere impostato"
        
        # VERIFICA: Temp folder creata
        expected_temp = "G:\\BackupPC\\.tmp_backup_2024-01-01_10-00-00"
        # mock_mkdir dovrebbe essere chiamato per creare la cartella temporanea
        assert mock_mkdir.call_count >= 1, "mkdir dovrebbe essere chiamato"
        
        # VERIFICA: Robocopy chiamato per ogni drive NON-C
        assert mock_run.call_count == 2, f"Dovrebbero esserci 2 chiamate robocopy (D:, E:), ottenute: {mock_run.call_count}"
        
        # VERIFICA: Robocopy chiamato con parametri corretti
        for call_args in mock_run.call_args_list:
            cmd = call_args[0][0]
            assert cmd[0] == "robocopy"
            assert "/MIR" in cmd
            assert "/NP" in cmd
        
        # VERIFICA: Finalize chiamato (rinomina cartella)
        mock_rename.assert_called_once()
        # Verifica che rinominasse da .tmp_backup_ a senza .tmp_backup_
        rename_call = mock_rename.call_args[0][0]  # Primo argomento di rename()
        assert ".tmp_backup_" not in str(rename_call), "La rinomina dovrebbe rimuovere .tmp_backup_"


def test_execute_backup_failure():
    """Test del flusso completo con fallimento robocopy"""
    # Configurazione
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    fixed_time = datetime(2024, 1, 1, 10, 0, 0)
    
    with patch("pybck.BackupBuilder.datetime") as mock_datetime, \
        patch("pybck.BackupBuilder.subprocess.run") as mock_run, \
        patch.object(Path, 'mkdir') as mock_mkdir, \
        patch.object(Path, 'rename') as mock_rename:
        
        mock_datetime.now.return_value = fixed_time
        builder = BackupBuilder(config)
        
        # Mock robocopy che FALLISCE (errore grave)
        mock_result = Mock()
        mock_result.returncode = 8  # Errore grave robocopy
        mock_result.stdout = ""
        mock_result.stderr = "Accesso negato"
        mock_run.return_value = mock_result
        
        # Esegui - dovrebbe fallire
        builder.execute_backup()
        
        # VERIFICA: Stato di fallimento corretto
        assert builder.executed == False, "Builder dovrebbe essere executed=False"
        assert builder.error is not None, "Errore dovrebbe essere impostato"
        assert "Errore durante la copia del drive D:" in builder.error
        
        # VERIFICA: Robocopy chiamato (ma fallisce)
        mock_run.assert_called_once()
        
        # VERIFICA: FINALIZE NON chiamato (nessuna rinomina)
        mock_rename.assert_not_called(), "Non dovrebbe essere chiamato rename() in caso di fallimento"
        
        # VERIFICA: Temp folder creata (per il Cleaner)
        assert mock_mkdir.call_count >= 1, "mkdir dovrebbe essere chiamato per creare .tmp_backup_"
        
        # IMPORTANTE: .tmp_backup_* NON eliminato - rimane per il Cleaner!
        # Questo è testato verificando che rename() non sia chiamato