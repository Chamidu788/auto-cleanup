# backup_utils.py
import winreg
import json
import os

BACKUP_FILE = os.path.join(os.getenv('APPDATA'), "SystemOptimizer_backup.json")

SETTINGS_TO_BACKUP = {
    "VisualEffects": {
        "key": winreg.HKEY_CURRENT_USER,
        "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
        "value_name": "VisualFxSetting"
    }
}

def backup_critical_settings():
    backup_data = {}
    
    try:
        setting = SETTINGS_TO_BACKUP["VisualEffects"]
        with winreg.OpenKey(setting["key"], setting["path"], 0, winreg.KEY_READ) as reg_key:
            value, reg_type = winreg.QueryValueEx(reg_key, setting["value_name"])
            backup_data["VisualEffects"] = value
    except FileNotFoundError:
        print("Visual Effects setting not found in registry. Skipping backup for this item.")
        backup_data["VisualEffects"] = 1 
    except Exception as e:
        print(f"An unexpected error occurred during Visual Effects backup: {e}")

    print("Settings backed up.")
    try:
        with open(BACKUP_FILE, "w") as f:
            json.dump(backup_data, f)
        return True
    except Exception as e:
        print(f"Failed to write backup file: {e}")
        return False

def restore_critical_settings():
    if not os.path.exists(BACKUP_FILE):
        print("No backup file found.")
        return False
    
    try:
        with open(BACKUP_FILE, "r") as f:
            backup_data = json.load(f)
    except Exception as e:
        print(f"Could not read backup file: {e}")
        return False

    try:
        if "VisualEffects" in backup_data:
            setting = SETTINGS_TO_BACKUP["VisualEffects"]
            with winreg.CreateKey(setting["key"], setting["path"]) as reg_key:
                winreg.SetValueEx(reg_key, setting["value_name"], 0, winreg.REG_DWORD, backup_data["VisualEffects"])
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, 0, 0x0002)
    except Exception as e:
        print(f"Could not restore Visual Effects: {e}")
        return False
        
    print("Settings restored.")
    return True