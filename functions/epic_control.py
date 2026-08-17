import sys
import os
import inspect
import time
import threading
import pyautogui
import re
import pyperclip

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from pywinauto import Application, findwindows

from functions import computer_control

epic_window_name = r"Foundation Production"

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

class EpicControlNative:
    def __init__(self):
        self.computer_control = computer_control
        self._pause_event = threading.Event()
        self._pause_event.set()
        self.app = None
        self.main_window = None
        self._cached_hwnd = None
        self.raw_clipboard = None
        self.specimens_image = resource_path("functions/images/specimens_image.png")
        self.connect_to_epic()

    def connect_to_epic(self):
        """
        Connects directly to Epic's backend UI tree using UIA. Some limitations due to administrator restrictions.
        """
        try:
            self._cached_hwnd = findwindows.find_window(title_re=epic_window_name)
            self.app = Application(backend="uia").connect(handle=self._cached_hwnd)
            self.main_window = self.app.window(handle=self._cached_hwnd)
        except Exception as e:
            print(f"ERROR: Could not connect to Epic UI Tree: {e}")
            self._cached_hwnd = None

    def epic_handle(self):
        if self._cached_hwnd:
            return self._cached_hwnd
        try:
            self._cached_hwnd = findwindows.find_window(title_re=epic_window_name)
        except:
            self._cached_hwnd = None
        return self._cached_hwnd

    def check_epic_active(self):
        epic_handle = self.epic_handle()
        active_handle = self.computer_control.active_window_handle()
        return epic_handle == active_handle if epic_handle else False

    def reactivate_epic(self):
        hwnd = self.epic_handle()
        if hwnd:
            import ctypes
            ctypes.windll.user32.ShowWindow(hwnd, 3)
            ctypes.windll.user32.SetForegroundWindow(hwnd)

    def monitor_window(self, stop_event):
        while not stop_event.is_set():
            if self.check_epic_active():
                self._pause_event.set() 
            else:
                self._pause_event.clear()
                self.reactivate_epic()
                
            time.sleep(0.05)

    def wait_if_paused(self):
        self._pause_event.wait()

    def navigate_to_specimens(self):
        snapshot_tab = self.main_window.child_window(
            title="Snapshot", 
            auto_id="0|LAB_SXS_DETAIL_SUMMARY_tab_846", 
            control_type="TabItem"
        )
        snapshot_tab.wait('visible', timeout=1)
        snapshot_tab.select()
        
        summary_btn = self.main_window.child_window(title="Summary", control_type="Button")
        summary_btn.wait('visible', timeout=1)
        time.sleep(0.2)

        rect = summary_btn.rectangle()
        click_x = rect.left + (rect.width() // 2)
        click_y = rect.top + (rect.height() // 2)
        
        pyautogui.click(click_x, click_y, duration=0.1)
        time.sleep(0.8)

    def click_specimens(self):
        raw_clipboard = None
        computer_control.empty_clipboard()
        self.click_specimen_coords()
        self.copy_all_specimens()
        
        try:
            raw_clipboard = pyperclip.paste()
        except pyperclip.PyperclipException as e:
            print(f"ERROR: Error accessing clipboard: {e}")
        
        if not raw_clipboard:
            return False
        
        self.raw_clipboard = raw_clipboard
        return True
            
    def click_specimen_coords(self):
        specimen_image = self.main_window.child_window(title="Specimens", control_type="Text")
        specimen_image.wait('visible', timeout=1)

        rect = specimen_image.rectangle()
        click_x = rect.left + (rect.width() // 2)
        click_y = rect.top + (rect.height() // 2)
        
        pyautogui.click(click_x, click_y, duration=0.1, button="right")
        
    def copy_all_specimens(self):
        for _ in range(4):
            pyautogui.press('down')
        pyautogui.press('enter')
          
    def get_specimens(self):
        status = None
        try:
            status = self.click_specimens()
        except:
            try:
                self.wait_if_paused()
                self.navigate_to_specimens()
                self.wait_if_paused()
                status = self.click_specimens()
                
            except Exception as e:
                print(f"ERROR: Execution failed: {e}")
                print(f"INFO: Please ensure Epic is opened and a case is selected and re-run program.")
        return status

    def process_specimens(self):
        input_list = self.raw_clipboard.splitlines(True)
        i=0
        while i < len(input_list):
            check_list = input_list[i].split()
            try:
                if check_list[0]=="ID" and check_list[1]=="Protocol":
                    table_start = i
            except:
                pass
            i += 1
        table_start_list = input_list[table_start:]
        combined_list = []
        for element in table_start_list:
            element = element.replace("\t", "|")
            if element==f"\r\n":
                break
            element = element.replace("\r\n", "")
            combined_list.append(element)
        
        id = ""
        protocol = ""
        description = ""
        parts_dict = {}
        for element in combined_list[1:]:
            parts = element.split("|")
            if re.match(r"^[A-Z]{1,2}\s?\|", element):
                id = parts[0].strip()
                protocol = parts[1]   
                if not parts[2] == "Collected:":
                    description = parts[3] 
                if not id:
                    print("ERROR: Specimen ID not found within the extracted specimens.")
            elif re.match(r"^\|Attributes\:", element):
                next
            elif re.match(r"^\|Source\:", element):
                next
            elif re.match(r"^\|Description\:", element):
                description = parts[2]
            if id:
                if protocol:
                    if description:
                        parts_dict[id] = [protocol, description]
                        id = ""
                        protocol = ""
                        description = ""
        return(parts_dict)
    
    def run_safe_automation(self):
        stop_event = threading.Event()
        monitor_thread = threading.Thread(target=self.monitor_window, args=(stop_event,), daemon=True)
        monitor_thread.start()
        
        i=0
        while i < 3:
            try:
                if self.get_specimens():
                    if self.process_specimens():
                        #print(self.process_specimens())
                        return self.process_specimens()
                    else:
                        i += 1
                        print(f"WARN: Failed to process specimens on attempt {i}. Retrying")
                else:
                    i += 1
                    print(f"WARN: Failed to get specimens on attempt {i}. Retrying")
                if not i < 3:
                    print(f"ERROR: Failed to get specimens after {i} attempts. Please re-run program.")
            finally:
                stop_event.set()
                monitor_thread.join()
            
def main():
    ec = EpicControlNative()
    start_time = time.perf_counter()
    print(ec.run_safe_automation())
    end_time = time.perf_counter()
    print(f"INFO: The script took {end_time - start_time:.4f} seconds to run.")

if __name__ == "__main__":
    main()