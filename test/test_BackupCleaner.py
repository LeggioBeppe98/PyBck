import pytest
import datetime
from pathlib import Path

# Importa la tua classe da testare
from pybck.BackupCleaner import BackupCleaner
from pybck.BackupConfig import BackupConfig

def test_getDataLimit():   
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:", "E:"],
        user_folders=["Documents", "Pictures", "Download"],
        keep_last_n=3
    )
    
    cleaner = BackupCleaner(config)
    
    data_limit = cleaner.getDataLimit()
    
    expected_date = datetime.datetime.now() - datetime.timedelta(days=config.keep_last_n)
    
    # Confronta solo la data (ignorando ore, minuti, secondi)
    assert data_limit.date() == expected_date.date()    
    
def test_get_backup_folders():   
    config = BackupConfig(
        backup_drive="G:",
        backup_root="BackupPC",
        source_drives=["C:", "D:", "E:"],
        user_folders=["Documents", "Pictures", "Download"],
        keep_last_n=3
    )
    
    cleaner = BackupCleaner(config)
    
    date_limit = datetime.datetime(2025, 1, 1, 10, 30, 45)
    
    backup_folder_path = cleaner._get_backup_folders(date_limit)
    
    expected_path = Path("G:\\BackupPC\\2025-01-01_10-30-45")
    
    assert backup_folder_path == expected_path
    

