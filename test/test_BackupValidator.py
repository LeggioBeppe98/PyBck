import pytest
import os

from pathlib import Path
import psutil

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
    
def test_validate_user_folders_exist():  
    # Crea una configurazione di backup valida
    config = BackupConfig(  
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents", "Downloads"],
        retention_days=3
    )
    validator = BackupValidator(config) 
    
    assert validator.validate_user_folders_exist() == True
    
        
def test_validate_user_folders_not_exist(monkeypatch):
    # Crea una configurazione di backup valida
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents", "Pictures", "NonExistentFolder"],
        retention_days=3
    )
    
    validator = BackupValidator(config)
    
    def mock_exists(path):
        # Ora i path saranno tipo "C:\Users\Tuonome\Documents"
        path_str = str(path)
        
        # Usa os.path.basename per estrarre solo il nome della cartella finale
        folder_name = os.path.basename(path_str)
        
        if folder_name in ["Documents", "Pictures"]:
            return True
        return False
    
    monkeypatch.setattr("pathlib.Path.exists", lambda self: mock_exists(str(self)))
    assert validator.validate_user_folders_exist() == False
    
def test_has_sufficient_space_true(monkeypatch):
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)
    
    def mock_disk_usage(path):
        # Normalizza: togli backslash finale
        normalized = str(path).rstrip("\\")
        
        if normalized == "C:":
            return type('obj', (object,), {
                'used': 100 * 1024**3,
                'free': 10 * 1024**3,
                'total': 110 * 1024**3
            })()
        elif normalized == "D:":
            return type('obj', (object,), {
                'used': 50 * 1024**3,
                'free': 20 * 1024**3,
                'total': 70 * 1024**3
            })()
        elif normalized == "G:":
            return type('obj', (object,), {
                'used': 100 * 1024**3,
                'free': 200 * 1024**3,
                'total': 300 * 1024**3
            })()
        else:
            raise ValueError(f"Path non mockato: {path}")
    
    def mock_path_exists(self):
        return True
    
    monkeypatch.setattr(psutil, "disk_usage", mock_disk_usage)
    monkeypatch.setattr("pathlib.Path.exists", mock_path_exists)
    
    approx_os_space = 20.0
    result = validator.has_sufficient_space(approx_os_space)
    
    assert result == True, f"Expected True, got {result}"
    
def test_has_sufficient_space_false(monkeypatch):
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)
    
    def mock_disk_usage(path):
        # Normalizza: togli backslash finale
        normalized = str(path).rstrip("\\")
        
        if normalized == "C:":
            return type('obj', (object,), {
                'used': 100 * 1024**3,
                'free': 10 * 1024**3,
                'total': 110 * 1024**3
            })()
        elif normalized == "D:":
            return type('obj', (object,), {
                'used': 50 * 1024**3,
                'free': 20 * 1024**3,
                'total': 70 * 1024**3
            })()
        elif normalized == "G:":
            return type('obj', (object,), {
                'used': 100 * 1024**3,
                'free': 10 * 1024**3,
                'total': 300 * 1024**3
            })()
        else:
            raise ValueError(f"Path non mockato: {path}")
    
    def mock_path_exists(self):
        return True
    
    monkeypatch.setattr(psutil, "disk_usage", mock_disk_usage)
    monkeypatch.setattr("pathlib.Path.exists", mock_path_exists)
    
    approx_os_space = 20.0
    
    assert validator.has_sufficient_space(approx_os_space) == False
    
    
def test_can_perform_backup_all_valid(monkeypatch):
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)
    
    # Mock is_drive_connected to return True
    monkeypatch.setattr(validator, "is_drive_connected", lambda drive: True)
    
    #Mock validate_sources_exist to return True
    monkeypatch.setattr(validator, "validate_sources_exist", lambda: True)
    
    # Mock validate_user_folders_exist to return True
    monkeypatch.setattr(validator, "validate_user_folders_exist", lambda: True)
    
    # Mock has_sufficient_space to return True
    monkeypatch.setattr(validator, "has_sufficient_space", lambda approx_os_space: True)
    
    approx_os_space = 20.0
    assert validator.can_perform_backup(approx_os_space) == True
    
def test_can_perform_backup_drive_not_connected(monkeypatch):
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)

    # Mock is_drive_connected to return False
    monkeypatch.setattr(validator, "is_drive_connected", lambda drive: False)
    
    approx_os_space = 20.0 
    assert validator.can_perform_backup(approx_os_space) == False

def test_can_perform_backup_sources_not_exist(monkeypatch):  
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)
    
    # Mock is_drive_connected to return True
    monkeypatch.setattr(validator, "is_drive_connected", lambda drive: True)

    #Mock validate_sources_exist to return True
    monkeypatch.setattr(validator, "validate_sources_exist", lambda: False)
    
    approx_os_space = 20.0 
    assert validator.can_perform_backup(approx_os_space) == False
    
def test_can_perform_backup_user_folders_not_exist(monkeypatch):  
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)

    # Mock is_drive_connected to return True
    monkeypatch.setattr(validator, "is_drive_connected", lambda drive: True)
    
    #Mock validate_sources_exist to return True
    monkeypatch.setattr(validator, "validate_sources_exist", lambda: True)
    
    # Mock validate_user_folders_exist to return False
    monkeypatch.setattr(validator, "validate_user_folders_exist", lambda: False)
    
    approx_os_space = 20.0 
    assert validator.can_perform_backup(approx_os_space) == False
    
def test_can_perform_backup_insufficient_space(monkeypatch):  
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:"],
        user_folders=["Documents"],
        retention_days=3
    )
    
    validator = BackupValidator(config)

    # Mock is_drive_connected to return True
    monkeypatch.setattr(validator, "is_drive_connected", lambda drive: True)
    
    #Mock validate_sources_exist to return True
    monkeypatch.setattr(validator, "validate_sources_exist", lambda: True)
    
    # Mock validate_user_folders_exist to return True
    monkeypatch.setattr(validator, "validate_user_folders_exist", lambda: True)
    
    # Mock has_sufficient_space to return False
    monkeypatch.setattr(validator, "has_sufficient_space", lambda approx_os_space: False)
    
    approx_os_space = 20.0 
    assert validator.can_perform_backup(approx_os_space) == False