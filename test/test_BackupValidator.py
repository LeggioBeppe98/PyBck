import pytest
import tempfile
import os
import re

# Importa la tua classe da testare
from pybck.BackupValidator import BackupValidator
from pybck.BackupConfig import BackupConfig

def test_drive_connected(monkeypatch):
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)
    
    # Monkeypatch psutil.disk_partitions per simulare un drive connesso
    def mock_disk_partition():
        class MockPartition:
            def __init__(self, device):
                self.device = device
        return [MockPartition("G:"), MockPartition("D:")]
    
    monkeypatch.setattr("psutil.disk_partitions", mock_disk_partition)
    
    assert validator.is_drive_connected("G:") == True
    
def test_drive_not_connected(monkeypatch):
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)
    
    # Monkeypatch psutil.disk_partitions per simulare nessun drive connesso
    def mock_disk_partitions():
        class MockPartition:
            def __init__(self, device):
                self.device = device
        return [MockPartition("C:"), MockPartition("D:")]
    
    monkeypatch.setattr("psutil.disk_partitions", mock_disk_partitions)
    
    assert validator.is_drive_connected("G:") == False
    assert validator.is_drive_connected("D:") == True
    
def test_drive_connected_real():
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)
    
    # Usa il comportamento reale di psutil.disk_partitions  

    assert validator.is_drive_connected("G:") == False  # Modifica in base ai drive effettivamente connessi

def test_validate_sources_exist(tmp_path):
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)
    
    # Monkeypatch Path.exists per simulare l'esistenza delle unità sorgente
    original_exists = os.path.exists
    
    def mock_exists(path):
        if path.startswith("C:\\") or path.startswith("D:\\"):
            return True
        return original_exists(path)
    
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("pathlib.Path.exists", lambda self: mock_exists(str(self)))
    
    assert validator.validate_sources_exist() == True
    
    # Ripristina il comportamento originale
    monkeypatch.undo()
    
def test_validate_sources_not_exist(monkeypatch):
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)
    
    # Monkeypatch Path.exists per simulare l'assenza di un'unità sorgente
    def mock_exists(path):
        if path.startswith("C:\\"):
            return True
        return False
    
    monkeypatch.setattr("pathlib.Path.exists", lambda self: mock_exists(str(self)))
    
    assert validator.validate_sources_exist() == False