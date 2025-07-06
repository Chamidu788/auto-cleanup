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

# --- "The Guard Clause" - ආරක්ෂක පියවර ---
# App එකේ කිසිම UI එකක් load වීමට පෙර, මෙය ක්‍රියාත්මක වේ.
if not is_admin():
    # Admin නොවේ නම්, messagebox එක පෙන්වා, සම්පූර්ණයෙන්ම exit වෙනවා.
    # මේ නිසා loop වෙන්න කිසිදු ඉඩක් ඉතිරි නොවේ.
    messagebox.showerror(
        "Administrator Privileges Required",
        "This application requires administrator privileges to run.\nPlease right-click the program and select 'Run as administrator'."
    )
    sys.exit() # මෙතනින් program එකේ ක්‍රියාකාරීත්වය 100% ක්ම නතර වේ.

# --- ඉහත if statement එක pass වුනොත් විතරක්, පහළ කේතය run වේ ---
# ඒ කියන්නේ, මේ වන විට අපි 100% ක්ම Administrator ලෙස ක්‍රියාත්මක වේ.

# දැන් පමණක් UI එකට අදාළ දේවල් import කරමු.
from ui_main import App

# App එක සාමාන්‍ය පරිදි run කරන්න
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = App()
    app.mainloop()