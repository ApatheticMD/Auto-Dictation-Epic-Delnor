import sys
import os
import time

import cv2
import numpy as np
import pyautogui
import time
import os

from win32clipboard import OpenClipboard, GetClipboardData, CloseClipboard, EmptyClipboard, SetClipboardText
from keyboard import press_and_release
from pywinauto import Desktop
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow, ShowWindow
from win32con import SW_MAXIMIZE
from pathlib import Path
from PIL import Image, ImageGrab
from screeninfo import get_monitors

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

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

def grab_clipboard():
    """
    Grabs the clipboard contents and returns them.
    """
    OpenClipboard()
    try:
        clipboard = GetClipboardData()
    except:
        clipboard = None
    CloseClipboard()
    return clipboard

def set_clipboard(contents):
    """
    Fills the clipboard with desired contents.

    Args:
        contents (str, required): String to be placed on the clipboard.
    """
    OpenClipboard()
    EmptyClipboard()
    SetClipboardText(contents)
    CloseClipboard()

def empty_clipboard():
    """
    Empties the clipboard of all contents.
    """
    OpenClipboard()
    EmptyClipboard()
    CloseClipboard()

def undo_prior(option=1):
    """
    Presses ctrl+z as many times as desired. Defaults to once.

    Args:
        option (int, optional): How many times to press ctrl+z. Defaults to 1.
    """
    while option > 0:
        press_and_release('ctrl+z')
        option = option - 1
        
def list_windows():
    """
    Prints a list of all windows by name.
    """
    windows = Desktop(backend="uia").windows()
    print(f"INFO: Windows identified = {[w.window_text() for w in windows]}")

def active_window_handle():
    """
    Returns the handle of the window currently in the foreground.
    """
    return GetForegroundWindow()

def active_window_name():
    """
    Returns the handle of the window currently in the foreground.
    """
    return GetWindowText(GetForegroundWindow())

def activate_window(handle):
    """
    Set a window in foreground and active by window handle id.

    Args:
        handle (handle obj, required): Input window handle pulled via pywinwauto.windows().
    """

    SetForegroundWindow(handle)
    ShowWindow(handle, SW_MAXIMIZE)
    SetForegroundWindow(handle)

def search_screen(image_path, threshold=0.9):
    loc=False
    method = cv2.TM_CCOEFF_NORMED
    
    screenshot = pyautogui.screenshot()
    screen_np = np.array(screenshot)
    screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
    
    if not os.path.exists(image_path):
        return False 

    # Load the image from the database
    script_dir = Path(__file__).parent.resolve()
    safe_path = script_dir / image_path
    try:
        pil_image = Image.open(safe_path).convert('L')
        template = np.array(pil_image)
    except FileNotFoundError:
        print(f"Error: File truly does not exist at {safe_path}")
    except Exception as e:
        print(f"ERROR: Failed to load image: {e}")

    # Perform template matching
    result = cv2.matchTemplate(screen_gray, template, method)

    # Get the location of matches above the specified threshold
    loc = np.where(result >= threshold)
    
    return loc

def search_and_click(image_path, method=cv2.TM_CCOEFF_NORMED, confidence_threshold=0.8, button="left"):
    """
    Search for an image on the screen by the path. Optimized (almost entirely by an LLM, lol) to be fast.
    Only use if UI element is not interactable using pyautogui.

    Args:
        image_path (string): path to image that is being searched for.
        method (cv2 search type, optional): Method to use for search. Defaults to cv2.TM_CCOEFF_NORMED.
        confidence_threshold (float, optional): Level of confidence returned from the cv2 search. Defaults to 0.8.
        button (str, optional): Which mouse button to click ("left" or "right" usually). Defaults to "left".

    Returns:
        bool: True if clicked, False if not.
    """
    script_dir = Path(__file__).parent.resolve()
    if isinstance(image_path, str):
        safe_path = Path(image_path) if Path(image_path).is_absolute() else script_dir / image_path
    else:
        safe_path = image_path

    try:
        pil_image = Image.open(safe_path).convert('L')
        template_base = np.array(pil_image)
    except Exception as e:
        print(f"ERROR: Error loading template image: {e}")
        return False

    try:
        monitors = get_monitors()
    except Exception as e:
        print(f"ERROR: Could not retrieve monitor setups: {e}")
        return False

    min_system_x = min(m.x for m in monitors)
    min_system_y = min(m.y for m in monitors)

    full_canvas = ImageGrab.grab(all_screens=True)
    full_canvas_gray = cv2.cvtColor(np.array(full_canvas), cv2.COLOR_RGB2GRAY)
    primary_monitor = next((m for m in monitors if m.is_primary), monitors)

    def click_match(max_loc, template_w, template_h, offset_x=0, offset_y=0, button=button):
        matched_x, matched_y = max_loc
        screen_x = matched_x + offset_x + min_system_x
        screen_y = matched_y + offset_y + min_system_y
        click_x = screen_x + (template_w // 2)
        click_y = screen_y + (template_h // 2)
        
        pyautogui.click(click_x, click_y, button=button)
        time.sleep(0.15)
        return True

    crop_x_start = primary_monitor.x + int(primary_monitor.width * 0.5)
    crop_x_end = primary_monitor.x + primary_monitor.width
    crop_y_start = primary_monitor.y
    crop_y_end = primary_monitor.y + int(primary_monitor.height * 0.5)

    pil_crop_x1 = crop_x_start - min_system_x
    pil_crop_x2 = crop_x_end - min_system_x
    pil_crop_y1 = crop_y_start - min_system_y
    pil_crop_y2 = crop_y_end - min_system_y
    
    roi_image = full_canvas.crop((pil_crop_x1, pil_crop_y1, pil_crop_x2, pil_crop_y2))
    roi_gray = cv2.cvtColor(np.array(roi_image), cv2.COLOR_RGB2GRAY)

    # STAGE 1: FAST SEARCH
    fast_scale = 0.5
    roi_small = cv2.resize(roi_gray, (0, 0), fx=fast_scale, fy=fast_scale, interpolation=cv2.INTER_AREA)
    template_small = cv2.resize(template_base, (0, 0), fx=fast_scale, fy=fast_scale, interpolation=cv2.INTER_AREA)
    if template_small.shape[0] <= roi_small.shape[0] and template_small.shape[1] <= roi_small.shape[1]:
        res_s1 = cv2.matchTemplate(roi_small, template_small, method)
        _, max_val, _, max_loc = cv2.minMaxLoc(res_s1)
        if max_val >= confidence_threshold:
            print(f"INFO: found {image_path} during step 1 (Fast Search)")
            roi_matched_x = int(max_loc[0] / fast_scale)
            roi_matched_y = int(max_loc[1] / fast_scale)
            h, w = template_base.shape[:2]
            return click_match((roi_matched_x, roi_matched_y), w, h, offset_x=(crop_x_start - min_system_x), offset_y=(crop_y_start - min_system_y))

    # STAGE 2: SEARCH PRIMARY MONITOR TOP-RIGHT AT NATIVE SCALE
    if template_base.shape[0] <= roi_gray.shape[0] and template_base.shape[1] <= roi_gray.shape[1]:
        res_s2 = cv2.matchTemplate(roi_gray, template_base, method)
        _, max_val, _, max_loc = cv2.minMaxLoc(res_s2)
        if max_val >= confidence_threshold:
            print(f"INFO: found {image_path} during step 2 (Native ROI)")
            h, w = template_base.shape[:2]
            return click_match(max_loc, w, h, offset_x=(crop_x_start - min_system_x), offset_y=(crop_y_start - min_system_y))

    # STAGE 3: SEARCH ALL MONITORS AT NATIVE DISPLAY SCALE
    if template_base.shape[0] <= full_canvas_gray.shape[0] and template_base.shape[1] <= full_canvas_gray.shape[1]:
        res_s3 = cv2.matchTemplate(full_canvas_gray, template_base, method)
        _, max_val, _, max_loc = cv2.minMaxLoc(res_s3)
        if max_val >= confidence_threshold:
            print(f"INFO: found {image_path} during step 3 (All Monitors Native)")
            h, w = template_base.shape[:2]
            return click_match(max_loc, w, h)

    # STAGE 4: RESCALE DOWN (SEARCH ALL MONITORS)
    down_scales = [100.0 / 150.0, 0.8, 0.5]
    for scale in down_scales:
        w_new = int(template_base.shape[1] * scale)
        h_new = int(template_base.shape[0] * scale)
        if w_new < 5 or h_new < 5: continue
        template_down = cv2.resize(template_base, (w_new, h_new), interpolation=cv2.INTER_AREA)
        if template_down.shape[0] <= full_canvas_gray.shape[0] and template_down.shape[1] <= full_canvas_gray.shape[1]:
            res_s4 = cv2.matchTemplate(full_canvas_gray, template_down, method)
            _, max_val, _, max_loc = cv2.minMaxLoc(res_s4)
            if max_val >= confidence_threshold:
                print(f"INFO: found {image_path} during step 4 (Scaled Down)")
                return click_match(max_loc, w_new, h_new)

    # STAGE 5: RESCALE UP (SEARCH ALL MONITORS)
    up_scales = [1.2, 1.5, 150.0 / 100.0]
    for scale in up_scales:
        w_new = int(template_base.shape[1] * scale)
        h_new = int(template_base.shape[0] * scale)
        template_up = cv2.resize(template_base, (w_new, h_new), interpolation=cv2.INTER_CUBIC)
        if template_up.shape[0] <= full_canvas_gray.shape[0] and template_up.shape[1] <= full_canvas_gray.shape[1]:
            res_s5 = cv2.matchTemplate(full_canvas_gray, template_up, method)
            _, max_val, _, max_loc = cv2.minMaxLoc(res_s5)
            if max_val >= confidence_threshold:
                print(f"INFO: found {image_path} during step 5 (Scaled Up)")
                return click_match(max_loc, w_new, h_new)
    return False

def main():
    list_windows()
      
if __name__ == "__main__":
    main()