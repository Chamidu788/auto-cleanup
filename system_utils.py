# system_utils.py
import os
import platform
import shutil
import subprocess
import threading
import time
import ctypes
import winreg

import psutil
from cpuinfo import get_cpu_info
import winshell

def get_static_info():
    """Fetches static system information without using the WMI Python library."""
    
    gpu_info = "N/A"
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        command = "wmic path win32_videocontroller get name"
        result = subprocess.check_output(command, startupinfo=startupinfo, text=True, stderr=subprocess.DEVNULL)
        lines = result.strip().split('\n')
        if len(lines) > 1 and lines[1].strip():
            gpu_info = lines[1].strip()
        else:
            gpu_info = "Not Found"
    except (subprocess.CalledProcessError, FileNotFoundError):
        gpu_info = "N/A (WMIC check failed)"
        print("Could not get GPU info via WMIC.")

    os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
    cpu_info_raw = get_cpu_info()
    cpu_info = f"{cpu_info_raw.get('brand_raw', 'N/A')} ({psutil.cpu_count(logical=True)} Cores)"
    total_ram = f"{psutil.virtual_memory().total / (1024**3):.2f} GB"

    disks = []
    for part in psutil.disk_partitions(all=False):
        if 'cdrom' in part.opts or part.fstype == '':
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disk_info = {
                "device": part.device,
                "total": f"{usage.total / (1024**3):.2f} GB",
                "used": f"{usage.used / (1024**3):.2f} GB",
                "percent": usage.percent
            }
            disks.append(disk_info)
        except Exception as e:
            print(f"Could not get disk info for {part.device}: {e}")

    return {
        "os": os_info,
        "cpu": cpu_info,
        "ram": total_ram,
        "gpu": gpu_info,
        "disks": disks,
    }

def get_realtime_stats():
    """Fetches real-time system usage stats."""
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "ram_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }

def clean_temp_files(progress_callback):
    progress_callback("Cleaning temporary files...")
    temp_folders = [os.environ.get('TEMP', ''), os.path.join(os.environ.get('windir', ''), 'Temp')]
    error_count = 0
    for folder in temp_folders:
        if folder and os.path.exists(folder):
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception:
                    error_count += 1
    time.sleep(1)
    return f"Temp files cleaned. Could not remove {error_count} locked file(s)."

def clean_windows_update_cache(progress_callback):
    progress_callback("Cleaning Windows Update cache...")
    try:
        creation_flags = subprocess.CREATE_NO_WINDOW
        subprocess.run(['net', 'stop', 'wuauserv'], check=True, capture_output=True, creationflags=creation_flags)
        update_cache_path = os.path.join(os.environ.get('windir'), 'SoftwareDistribution')
        if os.path.exists(update_cache_path):
            shutil.rmtree(update_cache_path, ignore_errors=True)
            time.sleep(0.5)
            os.makedirs(update_cache_path, exist_ok=True)
        subprocess.run(['net', 'start', 'wuauserv'], check=True, capture_output=True, creationflags=creation_flags)
        time.sleep(2)
        return "Windows Update cache cleared successfully."
    except Exception as e:
        subprocess.run(['net', 'start', 'wuauserv'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return f"Failed to clear Update cache: {e}"

def empty_recycle_bin(progress_callback):
    progress_callback("Emptying Recycle Bin...")
    try:
        if winshell.recycle_bin().size() == 0:
            return "Recycle Bin is already empty."
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        time.sleep(1)
        return "Recycle Bin emptied successfully."
    except Exception as e:
        return f"Failed to empty Recycle Bin: {e}"

def clear_dns_cache(progress_callback):
    progress_callback("Clearing DNS cache...")
    try:
        subprocess.run(['ipconfig', '/flushdns'], check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(1)
        return "DNS cache flushed successfully."
    except Exception as e:
        return f"Failed to flush DNS cache: {e}"

def optimize_disk(progress_callback):
    progress_callback("Optimizing system disk (Defrag/TRIM)...")
    try:
        subprocess.run(['defrag', 'C:', '/O'], check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(2)
        return "System disk optimization complete."
    except Exception as e:
        return f"Disk optimization failed: {e}"

def set_high_performance_power_plan(progress_callback):
    progress_callback("Setting power plan to High Performance...")
    try:
        command = ['powercfg', '/l']
        result = subprocess.run(command, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        for line in result.stdout.splitlines():
            if "high performance" in line.lower():
                guid = line.split()[3]
                subprocess.run(['powercfg', '/s', guid], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(1)
                return "Power plan set to High Performance."
        return "High Performance plan not found."
    except Exception as e:
        return f"Failed to set power plan: {e}"

def adjust_visual_effects(progress_callback):
    progress_callback("Adjusting visual effects for performance...")
    try:
        key = winreg.HKEY_CURRENT_USER
        path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
        with winreg.CreateKey(key, path) as reg_key:
            winreg.SetValueEx(reg_key, "VisualFxSetting", 0, winreg.REG_DWORD, 2)
        ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, 0, 0x0002)
        time.sleep(1)
        return "Visual effects adjusted for performance."
    except Exception as e:
        return f"Failed to adjust visual effects: {e}"

def disable_background_apps(progress_callback):
    progress_callback("Disabling background apps...")
    try:
        key = winreg.HKEY_CURRENT_USER
        path = r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications"
        with winreg.CreateKey(key, path) as reg_key:
            winreg.SetValueEx(reg_key, "GlobalUserDisabled", 0, winreg.REG_DWORD, 1)
        time.sleep(1)
        return "Background apps setting disabled."
    except Exception as e:
        return f"Failed to disable background apps: {e}"

def run_optimizations(selected_optimizations, progress_callback, completion_callback):
    def task():
        results = {}
        before_stats = get_realtime_stats()
        
        progress_callback("Backing up critical settings...")
        backup_utils.backup_critical_settings()
        time.sleep(0.5)
        
        for name, func in selected_optimizations.items():
            results[name] = func(progress_callback)
        
        time.sleep(2) 
        after_stats = get_realtime_stats()
        
        completion_callback(before_stats, after_stats, results)

    global backup_utils
    import backup_utils
    
    thread = threading.Thread(target=task)
    thread.daemon = True
    thread.start()