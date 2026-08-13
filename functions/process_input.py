import sys
import os


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

class ProcessSignout:
    
    def __init__(self, input_dict):
        self.input_dict = input_dict
    
    def get_signout_templates(self):
        pass
    
    def fix_typo_errors(self):
        pass
    
    def process_signout_input(self):
        pass
    
    