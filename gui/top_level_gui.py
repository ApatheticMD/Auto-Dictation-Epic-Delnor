import sys
import os
print(f"SETUP: Importing inspect.")
import inspect
print(f"SETUP: Importing time.")
import time
import ctypes
print(f"SETUP: Importing customtkinter.")
import customtkinter as tk
print(f"SETUP: Importing pywinstyles.")
import pywinstyles
import cv2
print(f"SETUP: Importing pillow.")
import PIL
print(f"SETUP: Importing pyautogui.")
import pyautogui
print(f"SETUP: Importing screeninfo.")
import screeninfo
print(f"SETUP: Importing keyboard.")
import keyboard

print(f"SETUP: Stabilizing path.")
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

print(f"SETUP: Importing template_handler.")
from functions import template_handler

print(f"SETUP: Importing epic_control.")
from functions import epic_control, computer_control

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

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

class TopLevelGUI:

    def __init__(self):
        self.root = tk.CTk()
        tk.set_default_color_theme("dark-blue")
        tk.set_appearance_mode("dark")
        
        monitors = screeninfo.get_monitors()
        if len(monitors) > 1:
            self.target_monitor = monitors[1]
        else:
            self.target_monitor = monitors[0]
            
        self.scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        self.screen_width = int(self.root.winfo_screenwidth() / self.scale_factor)
        self.screen_height = int(self.root.winfo_screenheight() / self.scale_factor)
        self.active_frame_name = None
        self.scheduled_callbacks = []
        
        self.icon_frames = self.extract_frames_from_video(resource_path('gui/assets/animated_icon.mp4'), 32, 32)
        self.icon_frame = 1
        self.icon_forward=True
        self.background_frame = 1
        self.background_forward=True
        self.animate_on=False
        self.animation_pad=-100
        self.background_animate=True
        self.logo_size_modifier = 1
        
        self.configure_ui()
        
        try:
            self.animate_icon()
        except:
            print("WARN: Error loading animated icon. Using static icon.")
            self.root.after(201, lambda :self.root.iconbitmap(resource_path('gui/assets/icon.ico')))
        try:
            self.background_intro()
        except:
            print("WARN: Error animating the background. Using default.")
            pywinstyles.set_opacity(self.background_label, value=0.2)
           
        print("INFO: Completed UI configuration.")
        self.root.mainloop()
        
    def configure_ui(self):            
        self.root.title("Auto Dictation")
        self.full_width = int(self.screen_width * 0.5)
        self.full_height = int(self.screen_height * 0.5)
        x_gap = int(self.root.winfo_screenwidth() * 0.1)
        y_gap = int(self.screen_height * 0.1)
        x_pos = self.target_monitor.x + (self.target_monitor.width//2) - (self.full_width//2)
        y_pos = self.target_monitor.y + (self.target_monitor.height//2) - (self.full_height//2)
        self.root.geometry(f"{self.full_width}x{self.full_height}+{x_pos}+{y_pos}")

        self.main_frame = self.create_main_frame(self.full_width, self.full_height)
        
        self.create_background()
        self.create_button_frame(self.full_width, self.full_height)
    
    def create_main_frame(self, width, height):
        main_frame = tk.CTkFrame(self.root, width=width, height=height)
        main_frame.pack(fill="both", expand=True)
        return main_frame
    
    def create_button_frame(self, width, height):
        self.button_frame = tk.CTkFrame(self.main_frame, width=int(width * 0.3), height=int(height * 0.8))
        self.button_frame.pack(pady=10, padx=10, fill="y", expand=False, side="left")
        pywinstyles.set_opacity(self.button_frame, value=0)

        self.label = tk.CTkLabel(self.button_frame, anchor="w", justify="left", text="Pathology Tools", font=tk.CTkFont(size=22))
        self.label.pack(side="top", fill="both", padx=10, pady=10)

        buttons = [
            ("Signout Microscope", lambda: self.show_frame('Signout Template-M', signout_only=True, microscope_comment=True)),
            ("Signout Microscope and Digital", lambda: self.show_frame('Signout Template-MD', signout_only=True, microscope_comment=True, digital_comment=True)),
            ("Signout Digital", lambda: self.show_frame('Signout Template-D', signout_only=True, digital_comment=True)),
            ("Signout No Micro Comment", lambda: self.show_frame('Signout Template-None', signout_only=True)),
        ]

        for text, command in buttons:
            button = tk.CTkButton(self.button_frame, text=text, command=command)
            button.pack(pady=10, padx=10, anchor="w")
            #if text == "Save Case":
                #self.root.bind("<F1>", self.save_case_event)

        #self.label = tk.CTkLabel(self.button_frame, anchor="w", justify="left", text="", font=tk.CTkFont(size=22))
        #self.label.pack(side="top", fill="both", padx=10, pady=10)
        #self.label = tk.CTkLabel(self.button_frame, anchor="w", justify="left", text="Pathology Tools", font=tk.CTkFont(size=22))
        #self.label.pack(side="top", fill="both", padx=10, pady=10)
        
        buttons = [
            #("**Test** - Open Case", lambda: self.show_frame('Open Case', open_case=True))
        ]

        for text, command in buttons:
            #button = tk.CTkButton(self.button_frame, text=text, command=command)
            #button.pack(pady=10, padx=10, anchor="w")
            pass
    
    def show_frame(self, frame_name, signout_only=False, microscope_comment=False, digital_comment=False):
        self.micro_comment = None
        if microscope_comment and not digital_comment:
            self.micro_comment = 0
        if microscope_comment and digital_comment:
            self.micro_comment = 1
        if digital_comment and not microscope_comment:
            self.micro_comment = 2
        if self.active_frame_name == frame_name:
            if self.active_frame:
                self.active_frame.destroy()
                self.active_frame = None
                self.active_frame_name = None
        else:
            try:
                if self.active_frame:
                    self.active_frame.destroy()
                    self.active_frame = None
                    self.active_frame_name = None
            except:
                pass
            
            self.active_frame = tk.CTkFrame(self.main_frame, width=int(self.screen_width * 0.5), height=int(self.screen_height * 0.8))
            self.active_frame.pack(pady=10, padx=10, fill="both", expand=True, side="right")
            pywinstyles.set_opacity(self.active_frame, value=0.95)
            self.active_frame_name = frame_name
            
            if signout_only:
                self.signout_only()
            else:
                self.active_frame_label = tk.CTkLabel(self.active_frame, text="", font=tk.CTkFont(size=20))
                self.active_frame_label.pack(pady=20)
    
    def signout_only(self):
        self.description_label = tk.CTkLabel(self.active_frame, text="Signout Template Builder", font=tk.CTkFont(size=20))
        self.description_label.pack(pady=10)
        
        self.label_name = "Run Signout Template Auto Dictation?"
        if self.micro_comment == 0:
            self.label_name = self.label_name + "\n\nMicroscope review only comment"
        if self.micro_comment == 1:
            self.label_name = self.label_name + "\n\nUse of microscope and digital comment"
        if self.micro_comment == 2:
            self.label_name = self.label_name + "\n\nDigital review only comment"
        if self.micro_comment == None:
            self.label_name = self.label_name + "\n\nNo microscopic description comment"
        
        self.barcode_label = tk.CTkLabel(self.active_frame, text=self.label_name, font=tk.CTkFont(size=14))
        self.barcode_label.pack(pady=10)
        
        self.barcode_button = tk.CTkButton(self.active_frame, text="OK", command=self.ok_clicked)
        self.barcode_button.pack(pady=10)
        self.barcode_button.bind('<Return>', lambda event: self.ok_clicked())
        
    def ok_clicked(self):
        ec = epic_control.EpicControlNative()
        try:
            specimen_dict = ec.run_safe_automation()
            print(f"INFO: Specimen information extracted:\n  {specimen_dict}")
        except:
            print(f"ERROR: Unable to obtain specimen information. Please ensure Epic is opened and try again.")
            return False
        try:
            sc = template_handler.SignoutCleanup(template_dict=specimen_dict)
            dictation_template = sc.build_signout_template()
        except:
            dictation_template = None
            print(f"ERROR: Unable to build the signout dictation. Please try again. \n  specimen_dict: {specimen_dict}\n  dictation_template: {dictation_template}")
            return False
        dictation_string = sc.signout_dict_to_string()
        start_pos = pyautogui.position()
        if not self.micro_comment == None:
            ec.select_drop_down_template(box_hotkey="alt+6", down_press=(self.micro_comment + 1))
        time.sleep(0.01)
        keyboard.press_and_release('alt+1')
        time.sleep(0.05)
        
        clipboard = None
        computer_control.empty_clipboard()
        keyboard.press_and_release('ctrl+a')
        time.sleep(0.05)
        keyboard.press_and_release('ctrl+c')
        time.sleep(0.05)
        clipboard = computer_control.grab_clipboard().strip()
        time.sleep(0.1)
        if clipboard:
            print(f"INFO: Dictation not entered. Detected text already in the diagnosis field:\n  {clipboard}")
            return False
        
        ec.input_dictation(box_hotkey="alt+1", dictation=dictation_string)
        time.sleep(0.01)
        keyboard.press_and_release('ctrl+a')
        time.sleep(0.01)
        keyboard.press_and_release('ctrl+b')
        time.sleep(0.01)
        keyboard.press_and_release('f2')
        pyautogui.moveTo(start_pos)
        
    def cancel_clicked(self):
        self.return_dict.clear()
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
    
    def extract_frames_from_video(self, video_path, x, y):
        cap = cv2.VideoCapture(video_path)
        frames = []

        if not cap.isOpened():
            print("Error: Couldn't open the video file.")
            return frames

        success, frame = cap.read()
        while success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_frame = PIL.Image.fromarray(frame)
            pil_frame = pil_frame.resize((x, y), PIL.Image.Resampling.LANCZOS)
            frames.append(PIL.ImageTk.PhotoImage(pil_frame))
            success, frame = cap.read()

        cap.release()
        return frames

    def animate_icon(self):
        self.root.iconbitmap()
        self.root.iconphoto(True, self.icon_frames[self.icon_frame])

        if self.icon_forward:
            self.icon_frame +=1
            if self.icon_frame >= 71:
                self.icon_frame = 71
                self.icon_forward = False
        if not self.icon_forward:
            self.icon_frame -=1
            if self.icon_frame <= 24:
                self.icon_forward = True
                self.icon_frame +=1
        self.root.after(50, self.animate_icon)  

    def animate_background(self):
        if self.animate_on:
            if self.background_forward:
                if self.logo_opacity > 0.8:
                    self.logo_opacity += 0.01
                elif self.logo_opacity > 0.7:
                    self.logo_opacity += 0.01
                elif self.logo_opacity > 0.6:
                    self.logo_opacity += 0.02
                elif self.logo_opacity > 0.5:
                    self.logo_opacity += 0.02
                else:
                    self.logo_opacity += 0.03
                if self.logo_opacity > 0.95:
                    self.background_forward = False
                    self.copyright_forward = False
            if not self.background_forward:
                if self.logo_opacity > 0.8:
                    self.logo_opacity -= 0.01
                elif self.logo_opacity > 0.7:
                    self.logo_opacity -= 0.01
                elif self.logo_opacity > 0.6:
                    self.logo_opacity -= 0.02
                elif self.logo_opacity > 0.5:
                    self.logo_opacity -= 0.02
                else:
                    self.logo_opacity -= 0.03
                if self.logo_opacity < 0.4:
                    self.background_forward = True
            pywinstyles.set_opacity(self.logo_label, value=self.logo_opacity) 
        if self.copyright_forward and self.logo_opacity < 0.2:
            pywinstyles.set_opacity(self.copyright_label, value=self.logo_opacity)  
            pywinstyles.set_opacity(self.button_frame, value=self.logo_opacity*5)    
        self.root.after(75, self.animate_background) 

    def shrink_logo(self):
        pywinstyles.set_opacity(self.logo_label, value=self.logo_opacity)
        if self.logo_opacity > 0:            
            self.logo_opacity -= .008
            self.root.after(15, self.shrink_logo)
        else:
            pywinstyles.set_opacity(self.logo_label, value=0)
            self.logo_image.configure(size=(self.screen_width/18, self.screen_height/18))
            self.root.after(100, self.animate_background)

    def background_intro(self):
        if self.background_forward:
            self.background_frame += 0.01
            if self.background_frame >= 0.7:
                self.background_forward = False
        if not self.background_forward:
            self.background_frame -= 0.01

        pywinstyles.set_opacity(self.logo_label, value=1-self.background_frame)        
        if self.background_frame < 0.2 and not self.background_forward:
            self.root.after(2000, self.shrink_logo)
            self.logo_opacity=0.9
            pywinstyles.set_opacity(self.logo_label, value=self.logo_opacity)
            self.background_forward = True
            self.background_frame = 0.9
            self.animate_on=True
            self.background_animate=True
        else:
            self.root.after(25, self.background_intro)  

    def create_background(self):
        logo_path = resource_path(f'gui/assets/logo.png')
        logo_image = PIL.Image.open(resource_path(logo_path))
        self.logo_image = tk.CTkImage(dark_image=logo_image, size=(self.screen_width/5, self.screen_height/5))
        self.logo_label = tk.CTkLabel(self.main_frame, image=self.logo_image, text="")
        self.logo_label.place(relwidth=1, relheight=1)
        pywinstyles.set_opacity(self.logo_label, value=0.9)
        
        copyright_path = resource_path(f'gui/assets/copyright.png')
        copyright_image = PIL.Image.open(resource_path(copyright_path))
        self.copyright_image = tk.CTkImage(dark_image=copyright_image, size=(self.screen_width/6, self.screen_height/60))
        self.copyright_label = tk.CTkLabel(self.main_frame, image=self.copyright_image, text="")
        self.copyright_label.place(relwidth=1, relheight=0.1, rely=0.85)
        pywinstyles.set_opacity(self.copyright_label, value=0)
        self.copyright_forward = True

        background_path = resource_path(f'gui/assets/background_only.png')
        backround_image = PIL.Image.open(resource_path(background_path))
        self.background_image = tk.CTkImage(dark_image=backround_image, size=(self.screen_width*1.1, self.screen_height*1.1))
        self.background_label = tk.CTkLabel(self.main_frame, image=self.background_image, text="")
        self.background_label.place(relwidth=1.1, relheight=1.1, x=0, y=self.animation_pad)
        pywinstyles.set_opacity(self.background_label, value=0.2)

def main():
    gui = TopLevelGUI()

if __name__ == "__main__":
    main()