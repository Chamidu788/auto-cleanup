# ui_main.py
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import threading
import time
import webbrowser
import sys
import os

import system_utils
import backup_utils

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


DARK_GRAY = "#242424"
MEDIUM_GRAY = "#2b2b2b"
LIGHT_GRAY = "#323232"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#00A67E"
LINK_COLOR = "#00C1FF"
RED = "#FF5733"
YELLOW = "#FFC300"
GREEN = "#00A67E"

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("Pro System Optimizer")
        self.geometry("1000x720")
        self.configure(fg_color=DARK_GRAY)
        self.overrideredirect(True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_title_bar()
        
        self.tab_view = ctk.CTkTabview(self, fg_color=DARK_GRAY, segmented_button_fg_color=DARK_GRAY, segmented_button_selected_color=MEDIUM_GRAY, segmented_button_selected_hover_color=LIGHT_GRAY, segmented_button_unselected_hover_color=LIGHT_GRAY)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        self.tab_view.add("Dashboard")
        self.tab_view.add("About")
        
        self._create_dashboard_tab(self.tab_view.tab("Dashboard"))
        self._create_about_tab(self.tab_view.tab("About"))

        self.update_realtime_stats()
        self.bind("<FocusIn>", self.handle_focus_in)

    def _create_title_bar(self):
        self.title_bar = ctk.CTkFrame(self, height=40, fg_color=MEDIUM_GRAY, corner_radius=0)
        self.title_bar.grid(row=0, column=0, sticky="ew")

        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        logo_image = ctk.CTkImage(Image.open(resource_path("assets/logo.png")), size=(24, 24))
        logo_label = ctk.CTkLabel(self.title_bar, image=logo_image, text="")
        logo_label.pack(side="left", padx=10)

        title_label = ctk.CTkLabel(self.title_bar, text="Pro System Optimizer", font=("Roboto", 14, "bold"), text_color=TEXT_COLOR)
        title_label.pack(side="left")

        close_button = ctk.CTkButton(self.title_bar, text="✕", width=40, height=40, command=self.quit, fg_color="transparent", hover_color=RED)
        close_button.pack(side="right")
        
        minimize_button = ctk.CTkButton(self.title_bar, text="—", width=40, height=40, command=self.minimize_window, fg_color="transparent", hover_color=LIGHT_GRAY)
        minimize_button.pack(side="right")

    def _create_dashboard_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        info_frame = ctk.CTkFrame(tab, fg_color=MEDIUM_GRAY)
        info_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(10, 10))
        info_frame.grid_columnconfigure(1, weight=1)
        self._create_static_info_panel(info_frame)

        monitor_frame = ctk.CTkFrame(tab, fg_color=MEDIUM_GRAY)
        monitor_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(10, 10))
        self._create_monitor_panel(monitor_frame)

        optimization_frame = ctk.CTkFrame(tab, fg_color=MEDIUM_GRAY)
        optimization_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        self._create_optimization_panel(optimization_frame)
    
    def _create_static_info_panel(self, parent):
        parent.grid_rowconfigure(5, weight=1)
        title = ctk.CTkLabel(parent, text="System Information", font=("Roboto", 18, "bold"), text_color=ACCENT_COLOR)
        title.grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="w")
        
        self.info_labels = {}
        info_map = {"OS": "os", "CPU": "cpu", "Total RAM": "ram", "GPU": "gpu"}
        
        for i, (label_text, key) in enumerate(info_map.items()):
            label = ctk.CTkLabel(parent, text=f"{label_text}:", font=("Roboto", 12, "bold"))
            label.grid(row=i+1, column=0, sticky="w", padx=20, pady=5)
            self.info_labels[key] = ctk.CTkLabel(parent, text="Fetching...", font=("Roboto", 12))
            self.info_labels[key].grid(row=i+1, column=1, sticky="w", padx=10, pady=5)

        threading.Thread(target=self.load_static_info, daemon=True).start()

    def _create_monitor_panel(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        title = ctk.CTkLabel(parent, text="Real-Time Monitor", font=("Roboto", 18, "bold"), text_color=ACCENT_COLOR)
        title.grid(row=0, column=0, columnspan=3, pady=10, padx=20, sticky="w")

        self.health_label = ctk.CTkLabel(parent, text="System Health: Fetching...", font=("Roboto", 14, "bold"))
        self.health_label.grid(row=1, column=0, columnspan=3, pady=(0, 15), padx=20, sticky="w")
        
        ctk.CTkLabel(parent, text="CPU Usage", font=("Roboto", 12)).grid(row=2, column=0, padx=20, sticky="w")
        self.cpu_progress = ctk.CTkProgressBar(parent, progress_color=GREEN)
        self.cpu_progress.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))
        self.cpu_label = ctk.CTkLabel(parent, text="0%")
        self.cpu_label.grid(row=3, column=2, padx=10)
        
        ctk.CTkLabel(parent, text="RAM Usage", font=("Roboto", 12)).grid(row=4, column=0, padx=20, sticky="w")
        self.ram_progress = ctk.CTkProgressBar(parent, progress_color=GREEN)
        self.ram_progress.grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))
        self.ram_label = ctk.CTkLabel(parent, text="0%")
        self.ram_label.grid(row=5, column=2, padx=10)
        
        ctk.CTkLabel(parent, text="Disk Usage (C:)", font=("Roboto", 12)).grid(row=6, column=0, padx=20, sticky="w")
        self.disk_progress = ctk.CTkProgressBar(parent, progress_color=GREEN)
        self.disk_progress.grid(row=7, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        self.disk_label = ctk.CTkLabel(parent, text="0%")
        self.disk_label.grid(row=7, column=2, padx=10)

    def _create_optimization_panel(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        title = ctk.CTkLabel(title_frame, text="System Optimizations", font=("Roboto", 18, "bold"), text_color=ACCENT_COLOR)
        title.pack(side="left")

        
        self.optimizations = {
            "Clean Temporary Files": system_utils.clean_temp_files,
            "Clear Windows Update Cache": system_utils.clean_windows_update_cache,
            "Empty Recycle Bin": system_utils.empty_recycle_bin,
            "Clear DNS Cache": system_utils.clear_dns_cache,
            "Optimize System Disk (Defrag/TRIM)": system_utils.optimize_disk,
            "Set High Performance Power Plan": system_utils.set_high_performance_power_plan,
            "Adjust Visual Effects for Performance": system_utils.adjust_visual_effects,
            "Disable Background Apps (Global)": system_utils.disable_background_apps,
        }
        
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color=DARK_GRAY)
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        
        self.opt_checkboxes = {}
        for i, (name, func) in enumerate(self.optimizations.items()):
            var = ctk.StringVar(value="on")
            cb = ctk.CTkCheckBox(scroll_frame, text=name, variable=var, onvalue="on", offvalue="off", font=("Roboto", 14))
            cb.grid(row=i, column=0, sticky="w", padx=10, pady=8)
            self.opt_checkboxes[name] = var

        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=15)
        button_frame.grid_columnconfigure((0, 1), weight=1)

        apply_btn = ctk.CTkButton(button_frame, text="Apply Selected Optimizations", command=self.run_optimizations, font=("Roboto", 14, "bold"), fg_color=ACCENT_COLOR, hover_color="#008a69")
        apply_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        restore_btn = ctk.CTkButton(button_frame, text="Restore Settings", command=self.restore_settings, font=("Roboto", 14, "bold"), fg_color=LIGHT_GRAY, hover_color="#454545")
        restore_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _create_about_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        about_frame = ctk.CTkFrame(tab, fg_color=MEDIUM_GRAY)
        about_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        about_frame.grid_columnconfigure(0, weight=1)
        
        def create_link(parent, text, url):
            link = ctk.CTkLabel(parent, text=text, text_color=LINK_COLOR, font=("Roboto", 12, "underline"), cursor="hand2")
            link.bind("<Button-1>", lambda e: webbrowser.open_new(url))
            return link

        ctk.CTkLabel(about_frame, text="About Pro System Optimizer", font=("Roboto", 20, "bold"), text_color=ACCENT_COLOR).pack(pady=(20, 10))
        ctk.CTkLabel(about_frame, text="Version 2.0 (Stable)", font=("Roboto", 12)).pack(pady=(0, 20))
        
        info_text = (
            "This tool is designed to help you monitor your system's health and apply "
            "common optimizations to improve performance and free up disk space. "
            "All operations are performed using standard Windows utilities and commands."
        )
        ctk.CTkLabel(about_frame, text=info_text, font=("Roboto", 14), wraplength=700, justify="center").pack(padx=20, pady=10)
        
        ctk.CTkFrame(about_frame, height=2, fg_color=LIGHT_GRAY).pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(about_frame, text="Developed By", font=("Roboto", 18, "bold"), text_color=ACCENT_COLOR).pack(pady=(10, 10))
        
        dev1_frame = ctk.CTkFrame(about_frame, fg_color="transparent")
        dev1_frame.pack(pady=5)
        ctk.CTkLabel(dev1_frame, text="Chamindu Kavishka:", font=("Roboto", 14, "bold")).pack(side="left", padx=5)
        create_link(dev1_frame, "chamindu1.vercel.app", "https://chamindu1.vercel.app").pack(side="left")

        dev2_frame = ctk.CTkFrame(about_frame, fg_color="transparent")
        dev2_frame.pack(pady=5)
        ctk.CTkLabel(dev2_frame, text="Maheshika Devindya:", font=("Roboto", 14, "bold")).pack(side="left", padx=5)
        create_link(dev2_frame, "maheshika1.vercel.app", "https://maheshika1.vercel.app").pack(side="left")
        
        ctk.CTkLabel(about_frame, text="Presented By", font=("Roboto", 18, "bold"), text_color=ACCENT_COLOR).pack(pady=(20, 10))
        
        company_frame = ctk.CTkFrame(about_frame, fg_color="transparent")
        company_frame.pack(pady=5)
        ctk.CTkLabel(company_frame, text="MC Digital Innovate:", font=("Roboto", 14, "bold")).pack(side="left", padx=5)
        create_link(company_frame, "mcdi.vercel.app", "https://mcdi.vercel.app").pack(side="left")
        
        ctk.CTkLabel(about_frame, text="© 2024 MC Digital Innovate. All rights reserved.", font=("Roboto", 10), text_color=LIGHT_GRAY).pack(pady=(30, 10))

    def load_static_info(self):
        data = system_utils.get_static_info()
        self.after(0, lambda: self.update_static_info_ui(data))

    def update_static_info_ui(self, data):
        self.info_labels["os"].configure(text=data["os"])
        self.info_labels["cpu"].configure(text=data["cpu"])
        self.info_labels["ram"].configure(text=data["ram"])
        self.info_labels["gpu"].configure(text=data["gpu"])

    def update_realtime_stats(self):
        stats = system_utils.get_realtime_stats()
        
        cpu = stats['cpu_usage']
        ram = stats['ram_usage']
        disk = stats['disk_usage']

        self.cpu_progress.set(cpu / 100)
        self.cpu_label.configure(text=f"{cpu:.1f}%")
        self.ram_progress.set(ram / 100)
        self.ram_label.configure(text=f"{ram:.1f}%")
        self.disk_progress.set(disk / 100)
        self.disk_label.configure(text=f"{disk:.1f}%")

        max_usage = max(cpu, ram, disk)
        if max_usage > 80:
            health_text, health_color = "Poor 🔴", RED
        elif max_usage > 50:
            health_text, health_color = "Average 🟡", YELLOW
        else:
            health_text, health_color = "Good 🟢", GREEN
        
        self.health_label.configure(text=f"System Health: {health_text}", text_color=health_color)
        self.cpu_progress.configure(progress_color=health_color)
        self.ram_progress.configure(progress_color=health_color)
        self.disk_progress.configure(progress_color=health_color)
        
        self.after(2000, self.update_realtime_stats)

    def run_optimizations(self):
        selected_opts = {name: self.optimizations[name] for name, var in self.opt_checkboxes.items() if var.get() == "on"}
        
        if not selected_opts:
            messagebox.showinfo("No Selection", "Please select at least one optimization to apply.")
            return

        self.show_progress_screen()
        system_utils.run_optimizations(
            selected_opts,
            self.update_progress,
            self.on_optimization_complete
        )

    def show_progress_screen(self):
        self.progress_window = ctk.CTkToplevel(self)
        self.progress_window.title("Optimizing...")
        self.progress_window.geometry("400x150")
        self.progress_window.transient(self)
        self.progress_window.grab_set()
        self.progress_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self.progress_window.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.progress_window, text="Applying Optimizations...", font=("Roboto", 16, "bold")).grid(row=0, pady=10)
        self.progress_label = ctk.CTkLabel(self.progress_window, text="Starting...", font=("Roboto", 12))
        self.progress_label.grid(row=1, pady=5)
        self.progress_bar = ctk.CTkProgressBar(self.progress_window, mode='indeterminate', progress_color=ACCENT_COLOR)
        self.progress_bar.grid(row=2, sticky="ew", padx=20, pady=10)
        self.progress_bar.start()

    def update_progress(self, message):
        self.progress_label.configure(text=message)
        
    def on_optimization_complete(self, before, after, results):
        self.progress_window.destroy()
        
        report = "--- Optimization Report ---\n\n"
        report += "Resource Usage (Before -> After):\n"
        report += f"  - CPU Usage: {before['cpu_usage']:.1f}% -> {after['cpu_usage']:.1f}%\n"
        report += f"  - RAM Usage: {before['ram_usage']:.1f}% -> {after['ram_usage']:.1f}%\n\n"
        report += "Actions Taken:\n"
        for name, result in results.items():
            report += f"  - {name}: {result}\n"
        
        messagebox.showinfo("Optimization Complete", report)

    def restore_settings(self):
        if messagebox.askyesno("Confirm Restore", "Are you sure you want to restore the settings from the last backup? This will revert changes made by the optimizer."):
            if backup_utils.restore_critical_settings():
                messagebox.showinfo("Success", "Settings have been successfully restored.")
            else:
                messagebox.showerror("Error", "Failed to restore settings. A backup might not exist or is corrupted.")

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
        
    def minimize_window(self):
        self.overrideredirect(False)
        self.iconify()

    def handle_focus_in(self, event):
        if self.state() == "normal":
            self.overrideredirect(True)