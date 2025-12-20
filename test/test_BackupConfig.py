import pytest
import tempfile
import os
import re

# Importa la tua classe da testare
from pybck.BackupConfig import BackupConfig

# Test per la validazione della configurazione di backup e per i metodi di salvataggio/caricamento

def test_valid_config():   
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:", "E:"],
        user_folders=["Documents", "Pictures", "Download"],
        retention_days=3
    )
    
    assert config.backup_drive == "G:"
    assert config.backup_root == "BackupPC"
    assert config.source_drives == ["C:", "D:", "E:"]
    assert config.user_folders == ["Documents", "Pictures", "Download"]
    assert config.retention_days == 3
    
def test_invalid_backup_drive():
    with pytest.raises(ValueError, match=re.escape("Backup drive deve essere una lettera di unità valida (es. 'G:').")):
        BackupConfig(
            backup_drive="InvalidDrive",
            backup_root="BackupPC",
            source_drives=["C:", "D:"],
            user_folders=["Documents"],
            retention_days=3
        )
        
def test_invalid_backup_drive_empty():
    with pytest.raises(ValueError, match="Backup drive deve essere specificato"):
        BackupConfig(
            backup_drive="",
            backup_root="BackupPC",
            source_drives=["C:", "D:"],
            user_folders=["Documents"],
            retention_days=3
        )
def test_invalid_backup_root():
    with pytest.raises(ValueError, match=re.escape("Backup root deve essere solo il nome della cartella valido (es. 'BackupPC').")):
        BackupConfig(
            backup_drive="G:",
            backup_root="Invalid/Path",
            source_drives=["C:", "D:"],
            user_folders=["Documents"],
            retention_days=3
        )
def test_invalid_backup_root_empty():
    with pytest.raises(ValueError, match="Backup root deve essere specificato"):
        BackupConfig(
            backup_drive="G:",
            backup_root="",
            source_drives=["C:", "D:"],
            user_folders=["Documents"],
            retention_days=3
        )
def test_invalid_source_drives():
    with pytest.raises(ValueError, match=re.escape("Unità sorgente non valida: InvalidDrive. Deve essere una lettera di unità valida (es. 'C:').")):
        BackupConfig(
            backup_drive="G:",
            backup_root="BackupPC",
            source_drives=["C:", "InvalidDrive"],
            user_folders=["Documents"],
            retention_days=3
        )
def test_empty_source_drives():
    with pytest.raises(ValueError, match="Almeno un'unità sorgente deve essere specificata."):
        BackupConfig(
            backup_drive="G:",
            backup_root="BackupPC",
            source_drives=[],
            user_folders=["Documents"],
            retention_days=3
        )   
def test_empty_user_folders():
    with pytest.raises(ValueError, match="Almeno una cartella utente deve essere specificata."):
        BackupConfig(
            backup_drive="G:",
            backup_root="BackupPC",
            source_drives=["C:", "D:"],
            user_folders=[],
            retention_days=3
        )   
def test_invalid_retention_days():
    with pytest.raises(ValueError, match="Retention days Deve essere maggiore di 1 e minore di 7."):
        BackupConfig(
            backup_drive="G:",
            backup_root="BackupPC",
            source_drives=["C:", "D:"],
            user_folders=["Documents"],
            retention_days=1
        )
def test_invalid_retention_days_too_high():
    with pytest.raises(ValueError, match="Retention days Deve essere maggiore di 1 e minore di 7."):
        BackupConfig(
            backup_drive="G:",
            backup_root="BackupPC",
            source_drives=["C:", "D:"],
            user_folders=["Documents"],
            retention_days=7
        )
def test_save_and_load_config():
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents", "Pictures"],
        retention_days=3
    )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "config.json")
        
        # Salva la configurazione
        config.save(config_path)
        
        # Carica la configurazione
        loaded_config = BackupConfig.load(config_path)
        
        assert loaded_config.backup_drive == config.backup_drive
        assert loaded_config.backup_root == config.backup_root
        assert loaded_config.source_drives == config.source_drives
        assert loaded_config.user_folders == config.user_folders
        assert loaded_config.retention_days == config.retention_days
        
def test_load_nonexistent_file():
    with pytest.raises(FileNotFoundError, match=re.escape("File di configurazione non trovato: nonexistent_config.json")):
        BackupConfig.load("nonexistent_config.json")
        
def test_file_exists_method():
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents", "Pictures"],
        retention_days=3
    )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "config.json")
        
        # Initially, the file should not exist
        assert not BackupConfig.file_exists(config_path)
        
        # Save the configuration to create the file
        config.save(config_path)
        
        # Now, the file should exist
        assert BackupConfig.file_exists(config_path)