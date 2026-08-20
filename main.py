print(f"SETUP: Importing sys.")
import sys
print(f"SETUP: Importing os.")
import os
print(f"SETUP: Importing ctypes.")
from ctypes import windll

print(f"SETUP: Importing top_level_gui.")
from gui import top_level_gui

print(f"SETUP: Establishing windows.")
windll.user32.ShowWindow(windll.kernel32.GetConsoleWindow(), 1)

print(f"SETUP: Setup complete.")

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
    gui = top_level_gui.TopLevelGUI()

if __name__ == "__main__":
    main()