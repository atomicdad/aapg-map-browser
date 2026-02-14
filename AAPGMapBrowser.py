#!/usr/bin/env python3
"""
AAPG Map Browser - Cross-platform (Windows/Linux)
Requirements:
pyautogui - keyboard automation
sv_ttk - tkinter theme for modernizing UI

Linux:
    xdotool - find and focus game window
Windows:
    pywin32 - find and focus game window

Optional:
    pyinstaller - to compile as self-contained executables
        Windows: pyinstaller --onefile --clean --noconsole --icon=assets/aapgmb.ico --add-data "assets/aapgmb.ico:assets" --add-data "assets/aapgmb.png:assets" AAPGMapBrowser.py
        Linux:   pyinstaller --onefile --clean --noconsole --add-data "assets/aapgmb.png:assets" AAPGMapBrowser.py
"""

__version__ = "1.1"
VERSION_STRING = f"v{__version__}"

import tkinter as tk
from tkinter import ttk, messagebox, Menu
import configparser
import os
import sys
import random
import time
import re
import platform
import subprocess
import sv_ttk

# Try Windows-specific imports
try:
    import win32gui
    import win32process
    import win32api
    import win32con
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

# pyautogui for typing
try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    pyautogui = None

# load default map list if maps.ini load fails
DEFAULT_MAPS = [
    "BDX_Breach_EX", "BDX_Bridge_EX", "BDX_Checkout_EX", "BDX_Crossfire_C4", "BDX_Crossfire_EX",
    "BDX_Furious_TH", "BDX_Hydra_EX", "BDX_InnerHospital_EX", "BDX_InnerHospital_VIP",
    "BDX_Intercept_C4", "BDX_Intercept_EX", "BDX_Lockdown_EX", "BDX_OuterHospital_C4",
    "BDX_Raptus_EX", "BDX_Reaction_EX", "BDX_RedLine_C4", "BDX_RedLine_EX", "BDX_Rusneyev_EX",
    "BDX_ShadowStep_EX", "BDX_Siege_C4", "BDX_Siege_EX", "BDX_SpringStreet_EX", "BDX_SpringStreet_VIP",
    "BDX_UrbanRush_EX", "BDX_Watchdog_C4", "FLO_AA2Hospital_VIP", "FLO_Abandoned_C4", "FLO_Alley_TH", "FLO_Blackwidow_VIP",
    "FLO_Border_EX", "FLO_Bystreet_TH", "FLO_Camel_EX", "FLO_CeaseFire_C4", "FLO_CeaseFireXL_C4",
    "FLO_Chaos_VIP", "FLO_Checkout_EX", "FLO_ColdFront_C4", "FLO_ColdFront_EX", "FLO_COPKeating_AC",
    "FLO_CSAR2_AC", "FLO_Danam_C4", "FLO_Descent_EX", "FLO_Desert_VIP", "FLO_DForce_VIP",
    "FLO_Dockside_TH", "FLO_DoubleImpact_TH", "FLO_Downtown_EX", "FLO_Dusk_VIP", "FLO_Enigma_AC",
    "FLO_FuriousMuseum_VIP", "FLO_HarborAssault_TH"
]

def resource_path(relative_path):
    """Get absolute path to resource"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_maps():
    maps = []
    if os.path.exists("maps.ini"):
        config = configparser.ConfigParser()
        config.read("maps.ini", encoding='utf-8-sig')
        if "Maps" in config:
            maps = list(config["Maps"].keys())
    else:
        maps = DEFAULT_MAPS[:]
        print("maps.ini not found → using default map list")
    return maps

def load_favorites(maps_list):
    favorites = {}
    if os.path.exists("favorites.ini"):
        config = configparser.ConfigParser()
        # Use utf-8-sig to handle BOM (common from Windows Notepad)
        config.read("favorites.ini", encoding='utf-8-sig')
        if "Favorites" in config:
            for m in maps_list:
                if config["Favorites"].get(m, "0") == "1":
                    favorites[m] = True
    return favorites

def save_favorites(favorites):
    config = configparser.ConfigParser()
    config["Favorites"] = {k: "1" for k, v in favorites.items() if v}
    # Write plain UTF-8 (no BOM)
    with open("favorites.ini", "w", encoding="utf-8") as f:
        config.write(f)

def clean_map_name(map_name: str) -> str:
    cleaned = re.sub(r"^(?:BDX_|FLO_)+", "", map_name, flags=re.IGNORECASE)
    if "$" in cleaned:
        cleaned = cleaned.split("$", 1)[0]
    cleaned = re.sub(r"(?:_AC|_C4|_EX|_VIP|_TH|_DE|_CU)$", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()

# ====================== CROSS-PLATFORM WINDOW FOCUS ======================

def find_game_window():
    os_name = platform.system().lower()
    if os_name == "windows" and HAS_PYWIN32:
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
                    exe = win32process.GetModuleFileNameEx(handle, 0).lower()
                    if "aagame.exe" in exe:
                        hwnds.append(hwnd)
                except:
                    pass
            return True
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None

    elif os_name == "linux":
        try:
            result = subprocess.run(
                ["xdotool", "search", "--name", "AA Game"],
                capture_output=True, text=True, timeout=4
            )
            ids = result.stdout.strip().split("\n")
            if ids and ids[0]:
                return ids[0]
        except:
            pass
    return None

def activate_game_window():
    if not HAS_PYAUTOGUI:
        print("pyautogui not available → cannot auto-focus or send keys")
        return False

    hwnd_or_id = find_game_window()
    if not hwnd_or_id:
        print("Game window not found")
        return False

    os_name = platform.system().lower()
    try:
        if os_name == "windows" and HAS_PYWIN32:
            win32gui.ShowWindow(hwnd_or_id, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd_or_id)
            time.sleep(0.25)
            return True
        elif os_name == "linux":
            subprocess.run(["xdotool", "windowactivate", str(hwnd_or_id)], check=False)
            time.sleep(0.35)
            return True
    except Exception as e:
        print(f"Window activation failed: {e}")
    return False

def send_command_to_game(command: str):
    if not HAS_PYAUTOGUI:
        print(f"Cannot send keys automatically. Manual command: ~ {command} ~")
        messagebox.showwarning("Warning", f"pyautogui missing.\nManual command:\n~ {command} ~")
        return

    success = activate_game_window()
    if not success:
        print(f"Could not focus game. Manual command: ~ {command} ~")
        messagebox.showwarning("Warning", f"Game not focused.\nManual command:\n~ {command} ~")
        return

    time.sleep(0.15)
    pyautogui.press('~')
    time.sleep(0.08)
    pyautogui.write(command)
    time.sleep(0.08)
    pyautogui.press('enter')
    time.sleep(0.08)
    pyautogui.press('~')

# ====================== GUI ======================

class AAPGMapBrowser:
    def __init__(self):
        self.context_menu = None
        self.action_var = None
        self.clean_var = None
        self.tree = None
        self.map_count_label = None
        self.search_edit = None
        self.search_var = None
        self.map_count_label_frame = None
        self.last_bdx = False
        self.last_flo = False
        self.flo_var = None
        self.fav_var = None
        self.bdx_var = None
        self.cu_var = None
        self.vip_var = None
        self.th_var = None
        self.ac_var = None
        self.de_var = None
        self.c4_var = None
        self.ex_var = None
        self.root = tk.Tk()
        self.root.title(f"AAPG: Map Browser {VERSION_STRING}")
        self.root.geometry("575x600")
        self.root.resizable(False, False)

        # ── Cross-platform icon setup ────────────────────────────────────────
        ico_path = resource_path("assets/aapgmb.ico")
        png_path = resource_path("assets/aapgmb.png")

        if sys.platform.startswith("win"):
            # Windows — prefers .ico
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                # fallback if something goes wrong with .ico
                photo = tk.PhotoImage(file=png_path)
                self.root.iconphoto(True, photo)

        else:
            # macOS + Linux — use PhotoImage (.png works best)
            try:
                photo = tk.PhotoImage(file=png_path)
                self.root.iconphoto(True, photo)
                self.root._icon_photo = photo
            except Exception as e:
                print("Could not load PNG icon:", e)
                # Optional fallback: try .ico on non-Windows
                try:
                    self.root.iconbitmap(ico_path)
                except:
                    pass

        try:
            self.root.option_add("*Font", ("Segoe UI", 10))
        except:
            pass

        self.maps = load_maps()
        self.favorites = load_favorites(self.maps)
        self.selected_map = ""
        self.map_action = 3  # default: set next map

        self.build_gui()
        self.update_listview()
        sv_ttk.set_theme("light")
        self.root.mainloop()

    def build_gui(self):
        os_name = platform.system().lower()

        # Search
        search_width = 0
        if os_name == "linux":
            ttk.Label(self.root, text="Search:").place(x=10, y=19)
            search_width = 23
        else:
            ttk.Label(self.root, text="Search:").place(x=10, y=18)
            search_width = 29

        self.search_var = tk.StringVar()
        self.search_edit = ttk.Entry(self.root, textvariable=self.search_var, width=search_width)

        if os_name == "linux":
            self.search_edit.place(x=64, y=13)
        else:
            self.search_edit.place(x=62, y=12)

        self.search_edit.bind("<KeyRelease>", lambda e: self.update_listview())

        # Map count
        self.map_count_label_frame = (ttk.LabelFrame(self.root, text="Map Count", width=85, height=38))
        self.map_count_label_frame.place(x=296, y=4)
        self.map_count_label = ttk.Label(self.map_count_label_frame, text="0")
        self.map_count_label.place(x=10, y=0)

        # ListView (Treeview)
        columns = ("hidden", "Map Name", "Type", "Mode", "Favorite")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=26)
        self.tree.place(x=10, y=50, width=372, height=540)

        self.tree.heading("hidden", text="")
        self.tree.heading("Map Name", text="Map Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Mode", text="Mode")
        self.tree.heading("Favorite", text="Favorite")

        self.tree.column("hidden", width=0, stretch=False)
        self.tree.column("Map Name", width=190, anchor="w")
        self.tree.column("Type", width=44, anchor="center")
        self.tree.column("Mode", width=47, anchor="center")
        self.tree.column("Favorite", width=70, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self.on_map_select)
        self.tree.bind("<Double-1>", lambda e: self.on_map_select(e))
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Filters
        filter_frame = ttk.LabelFrame(self.root, text="Map Filters:", width=148, height=234)
        filter_frame.place(x=404, y=4)

        self.fav_var = tk.BooleanVar()
        ttk.Checkbutton(self.root, text="Favorites", variable=self.fav_var, command=self.update_listview).place(x=417, y=20)

        ttk.LabelFrame(self.root, text="Map Type:", width=125, height=50).place(x=415, y=46)
        self.bdx_var = tk.BooleanVar(value=False)
        self.flo_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.root, text="BDX", variable=self.bdx_var, command=self.on_maptype_click).place(x=417, y=63)
        ttk.Checkbutton(self.root, text="FLO", variable=self.flo_var, command=self.on_maptype_click).place(x=477, y=63)

        ttk.LabelFrame(self.root, text="Game Mode:", width=125, height=128).place(x=415, y=100)
        self.ex_var  = tk.BooleanVar()
        self.c4_var  = tk.BooleanVar()
        self.de_var  = tk.BooleanVar()
        self.ac_var  = tk.BooleanVar()
        self.th_var  = tk.BooleanVar()
        self.vip_var = tk.BooleanVar()
        self.cu_var  = tk.BooleanVar()

        ttk.Checkbutton(self.root, text="EX",  variable=self.ex_var,  command=lambda: self.on_gamemode_click(self.ex_var)).place(x=417, y=118)
        ttk.Checkbutton(self.root, text="C4",  variable=self.c4_var,  command=lambda: self.on_gamemode_click(self.c4_var)).place(x=417, y=144)
        ttk.Checkbutton(self.root, text="DE",  variable=self.de_var,  command=lambda: self.on_gamemode_click(self.de_var)).place(x=417, y=170)
        ttk.Checkbutton(self.root, text="AC",  variable=self.ac_var,  command=lambda: self.on_gamemode_click(self.ac_var)).place(x=417, y=196)
        ttk.Checkbutton(self.root, text="TH",  variable=self.th_var,  command=lambda: self.on_gamemode_click(self.th_var)).place(x=477, y=118)
        ttk.Checkbutton(self.root, text="VIP", variable=self.vip_var, command=lambda: self.on_gamemode_click(self.vip_var)).place(x=477, y=144)
        ttk.Checkbutton(self.root, text="CU",  variable=self.cu_var,  command=lambda: self.on_gamemode_click(self.cu_var)).place(x=477, y=170)

        self.clean_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.root, text="Clean names", variable=self.clean_var, command=self.update_listview).place(x=418, y=246)

        # Random button
        ttk.Button(self.root, text="Pick Random Map", width=16, command=self.pick_random).place(x=402, y=280, height=30)

        # Action radios
        game_commands_frame = ttk.LabelFrame(self.root, text="Game Commands:", width=175, height=270)
        game_commands_frame.place(x=392, y=320)

        vote_frame = ttk.LabelFrame(game_commands_frame, text="Vote:", width=159, height=80)
        vote_frame.place(x=8, y=0)
        vote_switch_now = ttk.Radiobutton(vote_frame, text="Change Map Now", value=1, command=self.update_action)
        vote_switch_now.place(x=2, y=2)
        vote_scramble_teams = (ttk.Radiobutton(vote_frame, text="Scramble Teams", value=2, command=self.update_action))
        vote_scramble_teams.place(x=2, y=30)

        admin_frame = ttk.LabelFrame(game_commands_frame, text="Admin:", width=159, height=80)
        admin_frame.place(x=8, y=80)
        admin_set_next = ttk.Radiobutton(admin_frame, text="Set next map", value=3, command=self.update_action)
        admin_set_next.place(x=2, y=0)
        admin_switch_now = ttk.Radiobutton(admin_frame, text="Switch map now", value=4, command=self.update_action)
        admin_switch_now.place(x=2, y=30)

        local_frame = ttk.LabelFrame(game_commands_frame, text="Local:", width=159, height=46)
        local_frame.place(x=8, y=160)
        open_map_local = ttk.Radiobutton(local_frame, text="Open Map", value=5, command=self.update_action)
        open_map_local.place(x=2, y=0)

        self.action_var = tk.IntVar(value=3)
        for rb in (vote_switch_now, vote_scramble_teams, admin_set_next, admin_switch_now, open_map_local):
            rb.config(variable=self.action_var)

        ttk.Button(self.root, text="Submit", width=12, command=self.submit_map).place(x=420, y=550)

        self.root.bind("<Escape>", self.clear_search_and_filters)

        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Toggle Favorite", command=self.toggle_favorite)

    def update_action(self):
        self.map_action = self.action_var.get()

    def on_maptype_click(self):
        now_bdx = self.bdx_var.get()
        now_flo = self.flo_var.get()

        if now_bdx and now_flo:
            if self.last_bdx:
                self.bdx_var.set(False)
            else:
                self.flo_var.set(False)

        self.last_bdx = self.bdx_var.get()
        self.last_flo = self.flo_var.get()
        self.update_listview()

    def on_gamemode_click(self, clicked_var):
        if clicked_var.get():
            for v in [self.ex_var, self.c4_var, self.de_var, self.ac_var,
                      self.th_var, self.vip_var, self.cu_var]:
                if v is not clicked_var:
                    v.set(False)

        self.update_listview()

    def clear_search_and_filters(self, event=None):
        if not self.search_var.get().strip():
            self.fav_var.set(False)
            self.bdx_var.set(False)
            self.flo_var.set(False)
            self.ex_var.set(False)
            self.c4_var.set(False)
            self.de_var.set(False)
            self.ac_var.set(False)
            self.th_var.set(False)
            self.vip_var.set(False)
            self.cu_var.set(False)
        else:
            self.search_var.set("")
        self.update_listview()

    def on_map_select(self, event=None):
        sel = self.tree.selection()
        if sel:
            self.selected_map = self.tree.item(sel[0])["values"][0]

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.selected_map = self.tree.item(item)["values"][0]
            self.context_menu.post(event.x_root, event.y_root)

    def toggle_favorite(self):
        if not self.selected_map:
            return
        self.favorites[self.selected_map] = not self.favorites.get(self.selected_map, False)
        save_favorites(self.favorites)
        self.update_listview()

    def pick_random(self):
        items = self.tree.get_children()
        if not items:
            messagebox.showerror("Error", "No maps available in the current list.")
            return
        random_item = random.choice(items)
        self.tree.selection_set(random_item)
        self.tree.see(random_item)
        self.tree.focus(random_item)
        self.selected_map = self.tree.item(random_item)["values"][0]

    def update_listview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_text = self.search_var.get().strip().lower()
        clean_names = self.clean_var.get()

        any_filter = any([
            self.fav_var.get(), self.bdx_var.get(), self.flo_var.get(),
            self.ex_var.get(), self.c4_var.get(), self.de_var.get(),
            self.ac_var.get(), self.th_var.get(), self.vip_var.get(), self.cu_var.get()
        ])

        displayed = []
        for map_name in self.maps:
            map_type = map_name.split("_")[0].upper()
            mode = ""
            upper_name = map_name.upper()
            if "_C4" in upper_name: mode = "C4"
            elif "_EX" in upper_name: mode = "EX"
            elif "_VIP" in upper_name: mode = "VIP"
            elif "_TH" in upper_name: mode = "TH"
            elif "_AC" in upper_name: mode = "AC"
            elif "_DE" in upper_name: mode = "DE"
            elif "_CU" in upper_name: mode = "CU"

            is_fav = self.favorites.get(map_name, False)
            fav_str = "X" if is_fav else ""

            display_name = clean_map_name(map_name) if clean_names else map_name
            if search_text and search_text not in display_name.lower():
                continue

            meets = True
            if any_filter:
                if self.fav_var.get() and not is_fav: meets = False
                if self.bdx_var.get() and map_type != "BDX": meets = False
                if self.flo_var.get() and map_type != "FLO": meets = False
                if self.ex_var.get()  and mode != "EX":  meets = False
                if self.c4_var.get()  and mode != "C4":  meets = False
                if self.de_var.get()  and mode != "DE":  meets = False
                if self.ac_var.get()  and mode != "AC":  meets = False
                if self.th_var.get()  and mode != "TH":  meets = False
                if self.vip_var.get() and mode != "VIP": meets = False
                if self.cu_var.get()  and mode != "CU":  meets = False

            if meets:
                displayed.append((map_name, display_name, map_type, mode, fav_str))

        displayed.sort(key=lambda x: x[1])

        for item in displayed:
            self.tree.insert("", "end", values=item)

        self.map_count_label.config(text=f"{len(displayed)}")

    def submit_map(self):
        if self.map_action not in (1, 2, 3, 4, 5):
            return

        if self.map_action != 2 and not self.selected_map:
            messagebox.showerror("Error", "Please select a map.")
            return

        cmd = ""
        if self.map_action == 1:
            cmd = f"votechangemap {self.selected_map}"
        elif self.map_action == 2:
            cmd = "votescrambleteams"
        elif self.map_action == 3:
            cmd = f"adminsetnextmap {self.selected_map}"
        elif self.map_action == 4:
            cmd = f"adminswitchmap {self.selected_map}"
        elif self.map_action == 5:
            cmd = f"open {self.selected_map}"

        if cmd:
            send_command_to_game(cmd)
        else:
            messagebox.showerror("Error", "No valid command selected.")

if __name__ == "__main__":
    AAPGMapBrowser()