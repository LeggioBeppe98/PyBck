import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock

# Importa la tua classe da testare
from pybck.BackupCleaner import BackupCleaner
from pybck.BackupConfig import BackupConfig


def test_getListBackups_old():
    # Crea percorso reale temporaneo
    with tempfile.TemporaryDirectory() as tmpdir:
        # DEVI usare tmpdir come base
        config = Mock()
        config.backup_drive = tmpdir  # Usa il temp dir
        config.backup_root = ""       # Niente sottocartella
        
        cleaner = BackupCleaner(config)
        
        # Crea cartelle DENTRO la directory temporanea
        os.makedirs(os.path.join(tmpdir, "2024-01-22_10-30-45"))
        os.makedirs(os.path.join(tmpdir, "2025-01-22_10-30-45"))
        os.makedirs(os.path.join(tmpdir, "10-30-45"))  # Non dovrebbe matchare
        os.makedirs(os.path.join(tmpdir, "altro_file"))  # Altro non-match
        
        # Test
        result = cleaner._getListBackups(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$")
        
        # Assert: solo le cartelle che matchano il pattern
        assert len(result) == 2
        assert "2024-01-22_10-30-45" in result
        assert "2025-01-22_10-30-45" in result
        assert "10-30-45" not in result  # Pattern non matcha


def test_getListBackups_failed():
    # Crea percorso reale temporaneo
    with tempfile.TemporaryDirectory() as tmpdir:
        # DEVI usare tmpdir come base
        config = Mock()
        config.backup_drive = tmpdir  # Usa il temp dir
        config.backup_root = ""       # Niente sottocartella
        
        cleaner = BackupCleaner(config)
        
        # Crea cartelle DENTRO la directory temporanea
        os.makedirs(os.path.join(tmpdir, ".tmp_backup_2024-01-22_10-30-45"))
        os.makedirs(os.path.join(tmpdir, ".tmp_backup_2025-01-22_10-30-45"))
        os.makedirs(os.path.join(tmpdir, "10-30-45"))  # Non dovrebbe matchare
        os.makedirs(os.path.join(tmpdir, "altro_file"))  # Altro non-match
        
        # Test
        result = cleaner._getListBackups(r"^\.tmp_backup_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$")
        
        # Assert: solo le cartelle che matchano il pattern
        assert len(result) == 2
        assert ".tmp_backup_2024-01-22_10-30-45" in result
        assert ".tmp_backup_2025-01-22_10-30-45" in result
        assert "10-30-45" not in result  # Pattern non matcha