# main.py
import customtkinter as ctk
import ctypes
import sys
from tkinter import messagebox

def is_admin():
    """Checks for administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
 
    messagebox.showerror(
        "Administrator Privileges Required",
        "This application requires administrator privileges to run.\nPlease right-click the program and select 'Run as administrator'."
    )
    sys.exit() 


from ui_main import App


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = App()
    app.mainloop()