# PyBck

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)

**PyBck** è uno strumento di backup da riga di comando per sistemi **Windows**.  
Peermette di eseguire **backup automatici** di unità disco e cartelle utente su dischi esterni.

---

## ✨ Caratteristiche

- 🔄 **Backup multipli**  
  Backup di unità disco (`D:`, `E:` ecc.) e cartelle utente (`Downloads`, `Desktop`, `Documents`)

- 📊 **Verifica spazio**  
  Controllo automatico dello spazio disponibile prima del backup

- 🗑️ **Gestione retention**  
  Eliminazione automatica dei backup vecchi (configurabile)

- ⚡ **Progress reporting**  
  Barra di avanzamento e log dettagliato

- 🔒 **Sicurezza**  
  Verifica dei permessi amministrativi

- 🛡️ **Gestione errori**  
  Meccanismi robusti di recupero errori

- ⚙️ **Configurazione**  
  File di configurazione JSON per personalizzazione avanzata

⚙️ Configurazione

PyBck supporta configurazioni tramite:

Argomenti CLI → impostazioni temporanee

File JSON → impostazioni permanenti

{
  "backup_drive": "G:",
  "backup_root": "Backup_PC",
  "source_drives": ["D:", "E:"],
  "user_folders": ["Downloads", "Desktop", "Documents"],
  "keep_last_n": 7,
  "min_free_space_gb": 100,
  "verify_backup": true,
  "log_level": "INFO"
}

📁 Struttura dei backup
G:\Backup_PC\
├── Backup_C_2024-01-15_10-30-45\
│   ├── Downloads\
│   ├── Desktop\
│   └── Documents\
├── Disco_D_Backup_2024-01-15_10-30-45\
└── Disco_E_Backup_2024-01-15_10-30-45\



