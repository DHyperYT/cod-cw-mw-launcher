import tkinter as tk
from tkinter import filedialog, messagebox
import os
import tempfile
import cv2
from PIL import Image, ImageTk
import pygame
import subprocess
import time
import psutil
import webbrowser
import urllib.request
import sys
import pypresence

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Call of Duty Launcher")
        self.root.geometry("850x600")
        self.root.resizable(False, False)

        icon_path = resource_path('icon.ico')
        self.root.iconbitmap(icon_path)

        pygame.mixer.init()
        self.muted = False
        self.play_music(resource_path("mw.mp3"))

        self.overlay_frame = tk.Frame(root, bg="#000000", bd=5)
        self.overlay_frame.place(relwidth=1, relheight=1)

        self.sidebar = tk.Frame(self.overlay_frame, width=300, bg="#333", height=600, relief="raised", borderwidth=2)
        self.sidebar.pack(side="left", fill="y")

        self.button_frame = tk.Frame(self.sidebar, bg="#333")
        self.button_frame.pack(pady=10)

        self.mute_img = Image.open(resource_path("mute.png"))
        self.mute_img = self.mute_img.resize((50, 50), Image.Resampling.LANCZOS)
        self.mute_photo = ImageTk.PhotoImage(self.mute_img)
        self.mute_button = tk.Button(self.button_frame, image=self.mute_photo, command=self.toggle_mute, bg="#333", bd=0)
        self.mute_button.pack(side="left", padx=5)

        self.git_img = Image.open(resource_path("git.png"))
        self.git_img = self.git_img.resize((50, 50), Image.Resampling.LANCZOS)
        self.git_photo = ImageTk.PhotoImage(self.git_img)
        self.git_button = tk.Button(self.button_frame, image=self.git_photo, command=self.open_github, bg="#333", bd=0)
        self.git_button.pack(side="left", padx=5)

        self.discord_img = Image.open(resource_path("discord.png"))
        self.discord_img = self.discord_img.resize((50, 50), Image.Resampling.LANCZOS)
        self.discord_photo = ImageTk.PhotoImage(self.discord_img)
        self.discord_button = tk.Button(self.button_frame, image=self.discord_photo, command=self.open_discord, bg="#333", bd=0)
        self.discord_button.pack(side="left", padx=5)

        self.settings_button = tk.Button(self.sidebar, text="Settings", command=self.open_settings, bg="#000", fg="white", font=("Impact", 16), height=2)
        self.settings_button.pack(side="bottom", fill="x", pady=10)

        self.mw_button = tk.Button(self.sidebar, text="   Modern Warfare   ", command=self.show_mw_launcher, bg="#000", fg="white", font=("Impact", 16), height=2)
        self.mw_button.pack(pady=10)

        self.cw_button = tk.Button(self.sidebar, text="Black Ops Cold War", command=self.show_cw_launcher, bg="#000", fg="white", font=("Impact", 16), height=2)
        self.cw_button.pack(pady=10)

        self.main_frame = tk.Frame(self.overlay_frame, width=700, height=600, bg="#000000")
        self.main_frame.pack(side="right", fill="both", expand=True)

        self.video_label = tk.Label(self.main_frame)
        self.video_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.mw_video_path = resource_path("mw.mp4")
        self.cw_video_path = resource_path("cw.mp4")

        self.mw_cap = None
        self.cw_cap = None
        self.current_launcher = None
        self.launch_button = None
        self.dll_button = None

        self.current_mission_label = tk.Label(self.main_frame, text="Current Campaign Missions", bg="#000", fg="white", font=("Arial", 12))
        self.save1_label = tk.Label(self.main_frame, text="", bg="#000", fg="white", font=("Arial", 12))
        self.save2_label = tk.Label(self.main_frame, text="", bg="#000", fg="white", font=("Arial", 12))
        self.save3_label = tk.Label(self.main_frame, text="", bg="#000", fg="white", font=("Arial", 12))

        self.hide_mission_labels()

        self.initialize_rpc()
        self.show_mw_launcher()

        self.check_game_thread = threading.Thread(target=self.check_game_status, daemon=True)
        self.check_game_thread.start()
        
    def is_game_running(self, process_name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                return True
        return False

    def initialize_rpc(self):
        if any(proc.name() == "Discord.exe" for proc in psutil.process_iter()):
            try:
                self.rpc = pypresence.Presence(client_id='779362523388313612')
                self.rpc.connect()
                self.update_rpc("Idle", "In the Modern Warfare Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
            except Exception as e:
                print(f"Failed to initialize RPC: {e}")

    def update_rpc(self, state, details, button_label, button_url):
        if self.rpc:
            try:
                self.rpc.update(
                    state=state,
                    details=details,
                    large_image="icon",
                    buttons=[{"label": button_label, "url": button_url}]
                )
            except Exception as e:
                print(f"Failed to update RPC: {e}")

    def play_music(self, music_file):
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)

    def show_mw_launcher(self):
        if self.current_launcher == 'mw':
            return

        self.current_launcher = 'mw'
        if self.cw_cap:
            self.cw_cap.release()

        self.play_video(self.mw_video_path, 'mw')
        self.play_music(resource_path("mw.mp3"))

        if self.launch_button:
            self.launch_button.destroy()

        self.launch_button = tk.Button(self.main_frame, text="Launch", command=self.launch_mw_game, bg="#4b5320", fg="white", font=("Verdana", 20))
        self.launch_button.pack(pady=250)

        if self.dll_button:
            self.dll_button.destroy()

        self.dll_button = tk.Button(self.main_frame, text="Download DLL", command=self.download_mw_dll, bg="#FF4500", fg="white", font=("Arial", 12))
        self.dll_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

        self.hide_mission_labels()

        self.update_rpc("Idle", "In the Modern Warfare Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")

    def show_cw_launcher(self):
        if self.current_launcher == 'cw':
            return

        self.current_launcher = 'cw'
        if self.mw_cap:
            self.mw_cap.release()

        self.play_video(self.cw_video_path, 'cw')
        self.play_music(resource_path("cw.mp3"))

        if self.launch_button:
            self.launch_button.destroy()

        self.launch_button = tk.Button(self.main_frame, text="Launch", command=self.launch_cw_game, bg="#4b5320", fg="white", font=("Verdana", 20))
        self.launch_button.pack(pady=250)

        if self.dll_button:
            self.dll_button.destroy()

        self.dll_button = tk.Button(self.main_frame, text="Download DLL", command=self.download_cw_dll, bg="#FF4500", fg="white", font=("Arial", 12))
        self.dll_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

        self.update_mission_display()
        self.show_mission_labels()

        self.update_rpc("Idle", "In the Black Ops Cold War Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")

    def hide_mission_labels(self):
        self.current_mission_label.place_forget()
        self.save1_label.place_forget()
        self.save2_label.place_forget()
        self.save3_label.place_forget()

    def show_mission_labels(self):
        self.current_mission_label.place(x=10, y=460)
        self.save1_label.place(x=10, y=485)
        self.save2_label.place(x=10, y=510)
        self.save3_label.place(x=10, y=535)

    def update_mission_display(self):
        self.mission_map = {
            'cp_rus_amerika': 'Redlight, Greenlight',
            'cp_rus_yamantau': 'Echoes of a Cold War',
            'cp_ger_hub_post_yamantau': 'Safehouse: Lubyanka Briefing',
            'cp_rus_kgb': 'Desperate Measures',
            'cp_takedown': 'Nowhere Left to Run',
            'cp_ger_hub': 'CIA Safehouse E9',
            'cp_nam_armada': 'Fracture Jaw',
            'cp_ger_hub_post_armada': 'Safehouse: East Berlin Briefing',
            'cp_ger_stakeout': 'Brick in the Wall',
            'cp_sidemission_takedown': 'Operation Chaos',
            'cp_sidemission_tundra': 'Operation Red Circus',
            'cp_ger_hub_post_kgb': 'Safehouse: Cuba Briefing',
            'cp_nic_revolucion': 'End of the Line',
            'cp_ger_hub_post_cuba': 'Interrogation',
            'cp_nam_prisoner': 'Break on Through',
            'cp_ger_hub8': 'Identity Crisis',
            'cp_rus_siege': 'The Final Countdown',
            'cp_rus_duga': 'Ashes to Ashes',
        }

        save1_mission = self.get_mission_from_save_file('cp_savegame.cgp')
        save2_mission = self.get_mission_from_save_file('cp_savegame_1.cgp')
        save3_mission = self.get_mission_from_save_file('cp_savegame_2.cgp')

        self.save1_label.config(text=f"Save 1: {save1_mission}")
        self.save2_label.config(text=f"Save 2: {save2_mission}")
        self.save3_label.config(text=f"Save 3: {save3_mission}")

    def get_mission_from_save_file(self, save_file):
        save_directory = os.path.join(os.getenv('USERPROFILE'), 'Documents', 'Call Of Duty Black Ops Cold War', 'player')
        save_file_path = os.path.join(save_directory, save_file)

        try:
            with open(save_file_path, 'rb') as file:
                first_line = file.readline().decode('utf-8', errors='ignore')

                for mission_id in self.mission_map:
                    if mission_id in first_line:
                        return self.mission_map[mission_id]

            return "No active mission"
        except Exception as e:
            return "Error"

    def play_video(self, video_path, launcher_type):
        if launcher_type == 'mw':
            self.mw_cap = cv2.VideoCapture(video_path)
            self.update_video(self.mw_cap)
        elif launcher_type == 'cw':
            self.cw_cap = cv2.VideoCapture(video_path)
            self.update_video(self.cw_cap)

    def update_video(self, cap):
        if cap is not None:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (700, 600))
                img = ImageTk.PhotoImage(Image.fromarray(frame))
                self.video_label.config(image=img)
                self.video_label.image = img
                self.root.after(10, lambda: self.update_video(cap))
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.update_video(cap)

    def load_game_path(self):
        temp_dir = tempfile.gettempdir()
        path_file = os.path.join(temp_dir, f"cod_{self.current_launcher}_path.txt")
        if os.path.exists(path_file):
            with open(path_file, 'r') as file:
                return file.read().strip()
        return ""

    def save_game_path(self, path):
        temp_dir = tempfile.gettempdir()
        path_file = os.path.join(temp_dir, f"cod_{self.current_launcher}_path.txt")
        with open(path_file, 'w') as file:
            file.write(path)

    def open_settings(self):
        new_path = filedialog.askdirectory(title="Select Game Folder")
        if new_path:
            if self.current_launcher == 'mw':
                exe_path = os.path.join(new_path, "game_dx12_ship_replay.exe")
                if os.path.exists(exe_path):
                    self.save_game_path(new_path)
                    messagebox.showinfo("Path Saved", "Modern Warfare path has been saved.")
                else:
                    download = messagebox.askyesno("Executable Not Found", "Game not found in the selected path. Do you want to download it?")
                    if download:
                        webbrowser.open("https://gofile.io/d/r4XRqA")
            elif self.current_launcher == 'cw':
                exe_path = os.path.join(new_path, "BlackOpsColdWar.exe")
                if os.path.exists(exe_path):
                    self.save_game_path(new_path)
                    messagebox.showinfo("Path Saved", "Black Ops Cold War path has been saved.")
                else:
                    download = messagebox.askyesno("Executable Not Found", "Game not found in the selected path. Do you want to download it?")
                    if download:
                        webbrowser.open("https://gofile.io/d/s9r66f")

    def launch_mw_game(self):
        game_path = self.load_game_path()
        if game_path:
            exe_path = os.path.join(game_path, "game_dx12_ship_replay.exe")
            if os.path.exists(exe_path):
                self.toggle_mute()
                subprocess.Popen(exe_path, cwd=game_path)
                self.update_rpc("Playing", "Modern Warfare", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
                self.wait_for_process_termination("game_dx12_ship_replay.exe")
                self.toggle_mute()
                self.update_rpc("Idle", "In the Modern Warfare menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
            else:
                download = messagebox.askyesno("Executable Not Found", "Game not found in the selected path. Do you want to download it?")
                if download:
                    webbrowser.open("https://gofile.io/d/r4XRqA")
        else:
            messagebox.showerror("Error", "Game path not set. Please set the game path in Settings.")

    def launch_cw_game(self):
        game_path = self.load_game_path()
        if game_path:
            exe_path = os.path.join(game_path, "BlackOpsColdWar.exe")
            if os.path.exists(exe_path):
                self.toggle_mute()
                subprocess.Popen(exe_path, cwd=game_path)
                self.update_rpc("Playing", "Black Ops Cold War", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
                self.wait_for_process_termination("BlackOpsColdWar.exe")
                self.toggle_mute()
                self.update_rpc("Idle", "In the Black Ops Cold War menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
                self.update_mission_display()
            else:
                download = messagebox.askyesno("Executable Not Found", "Game not found in the selected path. Do you want to download it?")
                if download:
                    webbrowser.open("https://gofile.io/d/s9r66f")
        else:
            messagebox.showerror("Error", "Game path not set. Please set the game path in Settings.")

    def toggle_mute(self):
        if self.muted:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.muted = not self.muted

    def wait_for_process_termination(self, process_name):
        while any(proc.name() == process_name for proc in psutil.process_iter()):
            time.sleep(1)

    def download_mw_dll(self):
        game_path = self.load_game_path()
        if game_path:
            dll_url = "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/discord_game_sdk%20(1).dll"
            dll_path = os.path.join(game_path, "discord_game_sdk.dll")
            urllib.request.urlretrieve(dll_url, dll_path)
            messagebox.showinfo("DLL Downloaded", "DLL installed successfully.")
        else:
            messagebox.showerror("Error", "Game path not set. Please set the game path in Settings.")

    def download_cw_dll(self):
        game_path = self.load_game_path()
        if game_path:
            dll_url = "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/discord_game_sdk.dll"
            dll_path = os.path.join(game_path, "discord_game_sdk.dll")
            urllib.request.urlretrieve(dll_url, dll_path)
            messagebox.showinfo("DLL Downloaded", "DLL installed successfully.")
        else:
            messagebox.showerror("Error", "Game path not set. Please set the game path in Settings.")

    def open_github(self):
        webbrowser.open("https://github.com/DHyperYT/cod-cw-mw-launcher/")

    def open_discord(self):
        webbrowser.open("https://discord.gg/CCZhqg6RfX")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()
