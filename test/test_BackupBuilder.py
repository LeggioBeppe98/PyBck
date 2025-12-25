import pytest
import os

from pathlib import Path
import psutil

# Importa la tua classe da testare
from pybck.BackupConfig import BackupConfig
from pybck.BackupBuilder import BackupBuilder


def test_execute_backup(monkeypatch):
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
    
    # Mock dei metodi PRIVATI
    mock_temp_folder = "/fake/path/.tmp_backup_2024-01-01_10-00-00"
    
    def mock_create_temp(self):
        return mock_temp_folder
    
    def mock_create_drive(self, drive, temp):
        return f"{temp}/Disco_D_Backup_2024-01-01_10-00-00"
    
    def mock_copy_drive(self, drive, dest):
        pass  # Successo silenzioso
    
    def mock_finalize(self, temp):
        pass  # Successo silenzioso
    
    monkeypatch.setattr(BackupBuilder, "_create_temp_backup_folder", mock_create_temp)
    monkeypatch.setattr(BackupBuilder, "_create_folder_drive", mock_create_drive)
    monkeypatch.setattr(BackupBuilder, "_copy_drive", mock_copy_drive)
    monkeypatch.setattr(BackupBuilder, "_finalize_backup", mock_finalize)
    
    # Esegui
    backup_builder.execute_backup()
    
    # Verifica
    assert backup_builder.executed == True
    assert backup_builder.error is None