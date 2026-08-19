import sys
import os
from ctypes import windll

windll.user32.ShowWindow(windll.kernel32.GetConsoleWindow(), 1)

def resource_path(relative_path):
    """
    Takes in the relative_path of the file, and converts if needed to allow compiling.
    Should use whenever importing or reading a file stored in a directory.
    Try to change to _MEIPASS2 if having import errors.
    Args:
        relative_path (string): Relative path to file of interest.

    Returns:
        String: Correct path for use raw vs compiled.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def test():
    print("Import test: success")

def main():
    from functions import epic_control, template_handler
    
    #ec = epic_control.EpicControlNative()
    #specimen_dict = ec.run_safe_automation()
    #print(specimen_dict)
    
    #sc = template_handler.SignoutCleanup(template_dict=specimen_dict)
    #print(sc.build_signout_template())

if __name__ == "__main__":
    main()