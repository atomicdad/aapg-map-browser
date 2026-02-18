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

__version__ = "1.2.1b"
VERSION_STRING = f"v{__version__}"

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, Menu, filedialog
from pathlib import Path
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

# built in maps hardcoded
DEFAULT_MAPS = [
    "bdx_breach_ex", "bdx_bridge_ex", "bdx_checkout_ex", "bdx_crossfire_c4", "bdx_crossfire_ex", "bdx_furious_th"
    , "bdx_hydra_ex", "bdx_innerhospital_ex", "bdx_innerhospital_vip", "bdx_intercept_c4", "bdx_intercept_ex"
    , "bdx_lockdown_ex", "bdx_outerhospital_c4", "bdx_raptus_ex", "bdx_reaction_ex", "bdx_redline_c4", "bdx_redline_ex"
    , "bdx_rusneyev_ex", "bdx_shadowstep_ex", "bdx_siege_c4", "bdx_siege_ex", "bdx_springstreet_ex", "bdx_springstreet_vip"
    , "bdx_urbanrush_ex", "bdx_watchdog_c4", "flo_aa2hospital_vip", "flo_abandoned_c4", "flo_alley_th"
    , "flo_blackwidow_vip", "flo_border_ex", "flo_bridgenight_ex", "flo_bridge_ex", "flo_bystreet_th"
    , "flo_copkeating_ac", "flo_csar2_ac", "flo_cabinfever_th", "flo_camel_ex", "flo_ceasefirexl_c4"
    , "flo_ceasefire_c4", "flo_chaos_vip", "flo_checkout_ex", "flo_coldfront_c4", "flo_coldfront_ex", "flo_dforce_vip"
    , "flo_danam_c4", "flo_descent_ex", "flo_desert_vip", "flo_dockside_th", "flo_doubleimpact_th", "flo_downtown_ex"
    , "flo_dusk_vip", "flo_enigma_ac", "flo_furiousmuseum_vip", "flo_furious_th", "flo_harborassaultnight_th"
    , "flo_harborassault_th", "flo_hardescape_vip", "flo_highway_ex", "flo_homestead_c4", "flo_homestead_vip"
    , "flo_honortown_ac", "flo_hospital_ex", "flo_impact_th", "flo_innerhospital_ex", "flo_innerhospital_vip"
    , "flo_insurgentcamp_ac", "flo_intercept_c4", "flo_intercept_ex", "flo_intercept_vip", "flo_invaders_c4"
    , "flo_killorbekilled_de", "flo_kortyarzeh_c4", "flo_lazareth_ac", "flo_longstone_ac", "flo_moutmckenna_th"
    , "flo_obelisk_c4", "flo_overload_c4", "flo_parkinggarage_ex", "flo_pipeline_ac", "flo_rdp_c4", "flo_ranch_ac"
    , "flo_raptus_ex", "flo_reaction_ex", "flo_redline_c4", "flo_redline_ex", "flo_redline_vip", "flo_rockyroad_ex"
    , "flo_rusneyev_ex", "flo_sonaf_de", "flo_sandstorm_th", "flo_simplex_th", "flo_slums_c4", "flo_slums_th"
    , "flo_slums_vip", "flo_smugglersharbour_vip", "flo_snakeplain2_c4", "flo_steamroller_th", "flo_streets_vip"
    , "flo_threekings_th", "flo_touchdown_ex", "flo_toujane_ex", "flo_trouble_vip", "flo_twincreekminingco_vip"
    , "flo_uptown_ex", "flo_uptown_vip", "flo_vypls_ac", "flo_waste_c4", "flo_watchdog_ac", "flo_watchdog_c4"
    , "flo_worksite_ex", "leavenworthprison", "flo_stoneruins_c4"
]


def get_appdata_path(filename: str) -> Path:
    """
    Returns a Path to filename next to the .exe (even in --onefile mode).
    Works in dev (python) and frozen exe.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as bundled exe
        exe_dir = Path(sys.executable).resolve().parent
    else:
        # Running as python script
        exe_dir = Path(__file__).resolve().parent

    return exe_dir / filename

def resource_path(relative_path):
    """Get absolute path to resource"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# def load_maps():
#     maps = []
#     if os.path.exists("maps.ini"):
#         config = configparser.ConfigParser()
#         config.read(str(get_appdata_path("maps.ini")), encoding='utf-8-sig')
#         if "Maps" in config:
#             maps = list(config["Maps"].keys())
#     else:
#         maps = DEFAULT_MAPS[:]
#         print("maps.ini not found → using default map list")
#     return maps

def load_favorites():
    favorites = {}
    if os.path.exists("favorites.ini"):
        config = configparser.ConfigParser()
        # Use utf-8-sig to handle BOM (common from Windows Notepad)
        config.read(str(get_appdata_path("favorites.ini")), encoding='utf-8-sig')
        if "Favorites" in config:
            for m, v in config["Favorites"].items():
                if v == "1":
                    favorites[m] = True
    return favorites

def save_favorites(favorites):
    config = configparser.ConfigParser()
    config["Favorites"] = {k: "1" for k, v in favorites.items() if v}
    # Write plain UTF-8 (no BOM)
    with get_appdata_path("favorites.ini").open("w", encoding="utf-8") as f:
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
        self.aaclient_log_found = False
        self.workshop_content_found = False
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
        self.maps_dirty = False
        self.last_shown_map_list_name = ""
        self.current_map_list_name = ""
        self.root = tk.Tk()
        self.root.title(f"AAPG: Map Browser {VERSION_STRING}")
        self.root.geometry("585x655")
        self.root.resizable(False, False)

        # ── Config ────────────────────────────────────────────────────────
        #self.config_path = Path(__file__).parent / "config.ini"
        self.config_path = str(get_appdata_path("config.ini"))
        self.aaclient_log_path = ""
        self.workshop_path = ""
        self.last_map_file = ""
        self.dark_mode = False
        self.load_config()
        self.validate_paths()

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

        self.favorites = load_favorites()
        self.selected_map = ""
        self.map_action = 3  # default: set next map

        self.build_gui()
        self.refresh_map_file_selection_combobox()
        self.current_map_list_name = self.combo_file_var.get().strip()

        self.update_listview()
        theme = "dark" if self.dark_mode else "light"
        sv_ttk.set_theme(theme)

        theme = "dark" if self.dark_mode else "light"
        sv_ttk.set_theme(theme)

        # Fix persistent blue highlight on readonly Combobox
        style = ttk.Style()

        if theme == "dark":
            style.map("TCombobox",
                      selectbackground=[("readonly", "#333333")],  # dark gray
                      selectforeground=[("readonly", "#e0e0e0")],
                      )
        else:
            style.map("TCombobox",
                      selectbackground=[("readonly", "white")],
                      selectforeground=[("readonly", "black")],
                      )
        # Intercept the window close button (X)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.mainloop()

    def build_gui(self):
        os_name = platform.system().lower()

        # Menu
        self.menubar = tk.Menu(self.root)
        self.root["menu"] = self.menubar
        self.menu_file = tk.Menu(self.menubar, tearoff=0)
        self.menu_settings = tk.Menu(self.menubar, tearoff=0)
        self.menu_map_list = tk.Menu(self.menubar, tearoff=0)
        self.menu_help = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.menu_file)
        self.menubar.add_cascade(label="Map List", menu=self.menu_map_list)
        self.menubar.add_cascade(label="Settings", menu=self.menu_settings)
        #self.menubar.add_cascade(label="Help", menu=self.menu_help)

        self.menu_file.add_command(
            label="New",
            command=self.create_new_map_list
        )

        self.menu_file.add_command(
            label="Save",
            command=self.save_map_list
        )

        self.menu_file.add_command(
            label="Save As...",
            command=self.save_map_list_as
        )

        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.on_closing)

        self.menu_map_list.add_command(
            label="Rename Current",
            command=self.rename_current_map_list
        )
        self.menu_map_list.add_command(
            label="Delete Current",
            command=self.delete_current_map_list
        )
        self.menu_map_list.add_command(
            label="Get Local Maps",
            command=self.get_local_maps
        )
        self.menu_map_list.add_command(
            label="Get Server Maps",
            command=self.get_server_maps
        )


        self.dark_var = tk.BooleanVar(value=self.dark_mode)
        self.menu_settings.add_command(
            label="Folder Paths",
            command=self.show_folder_paths
        )
        self.menu_settings.add_checkbutton(label="Dark Mode",
                                           variable=self.dark_var,
                                           command=self.toggle_dark_mode)

        #TODO: Implement guidance for support
        #self.menu_help.add_command(label="Report Issue/Bug")

        #Map List Frame
        self.map_list_frame = ttk.LabelFrame(self.root, text="", width=388, height=618)
        self.map_list_frame.place(x=7, y=10)

        # Map List File ComboBox
        self.combo_file_var = tk.StringVar(value="")
        self.file_selection_combo_box = ttk.Combobox(self.root, textvariable=self.combo_file_var, values=["Temp"], state="readonly")
        self.file_selection_combo_box.place(x=15, y=5)
        # Bind the change detector
        self.combo_file_var.trace_add("write", self.on_file_combo_about_to_change)

        # Search
        search_width = 0
        if os_name == "linux":
            ttk.Label(self.root, text="Search:").place(x=15, y=49)
            search_width = 23
        else:
            ttk.Label(self.root, text="Search:").place(x=15, y=48)
            search_width = 29

        self.search_var = tk.StringVar()
        self.search_edit = ttk.Entry(self.root, textvariable=self.search_var, width=search_width)

        if os_name == "linux":
            self.search_edit.place(x=69, y=43)
        else:
            self.search_edit.place(x=67, y=42)

        self.search_edit.bind("<KeyRelease>", lambda e: self.update_listview())

        # Map count
        self.map_count_label_frame = (ttk.LabelFrame(self.root, text="Map Count", width=85, height=38))
        self.map_count_label_frame.place(x=296, y=34)
        self.map_count_label = ttk.Label(self.map_count_label_frame, text="0")
        self.map_count_label.place(x=10, y=0)

        # ListView (Treeview)
        columns = ("hidden", "Map Name", "Type", "Mode", "Favorite")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=26)
        self.tree.place(x=15, y=80, width=372, height=540)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.place(x=15 + 350 + 4, y=115, height=500)

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
        filter_frame.place(x=415, y=10)

        self.fav_var = tk.BooleanVar()
        ttk.Checkbutton(self.root, text="Favorites", variable=self.fav_var, command=self.update_listview).place(x=428, y=25)

        ttk.LabelFrame(self.root, text="Map Type:", width=125, height=50).place(x=426, y=51)
        self.bdx_var = tk.BooleanVar(value=False)
        self.flo_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.root, text="BDX", variable=self.bdx_var, command=self.on_maptype_click).place(x=428, y=68)
        ttk.Checkbutton(self.root, text="FLO", variable=self.flo_var, command=self.on_maptype_click).place(x=488, y=68)

        ttk.LabelFrame(self.root, text="Game Mode:", width=125, height=128).place(x=426, y=105)
        self.ex_var  = tk.BooleanVar()
        self.c4_var  = tk.BooleanVar()
        self.de_var  = tk.BooleanVar()
        self.ac_var  = tk.BooleanVar()
        self.th_var  = tk.BooleanVar()
        self.vip_var = tk.BooleanVar()
        self.cu_var  = tk.BooleanVar()

        ttk.Checkbutton(self.root, text="EX",  variable=self.ex_var,  command=lambda: self.on_gamemode_click(self.ex_var)).place(x=428, y=123)
        ttk.Checkbutton(self.root, text="C4",  variable=self.c4_var,  command=lambda: self.on_gamemode_click(self.c4_var)).place(x=428, y=149)
        ttk.Checkbutton(self.root, text="DE",  variable=self.de_var,  command=lambda: self.on_gamemode_click(self.de_var)).place(x=428, y=175)
        ttk.Checkbutton(self.root, text="AC",  variable=self.ac_var,  command=lambda: self.on_gamemode_click(self.ac_var)).place(x=428, y=201)
        ttk.Checkbutton(self.root, text="TH",  variable=self.th_var,  command=lambda: self.on_gamemode_click(self.th_var)).place(x=488, y=123)
        ttk.Checkbutton(self.root, text="VIP", variable=self.vip_var, command=lambda: self.on_gamemode_click(self.vip_var)).place(x=488, y=149)
        ttk.Checkbutton(self.root, text="CU",  variable=self.cu_var,  command=lambda: self.on_gamemode_click(self.cu_var)).place(x=488, y=175)

        self.clean_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.root, text="Clean names", variable=self.clean_var, command=self.update_listview).place(x=427, y=256)

        # Random button
        ttk.Button(self.root, text="Pick Random Map", width=16, command=self.pick_random).place(x=411, y=295, height=30)

        # Action radios
        game_commands_frame = ttk.LabelFrame(self.root, text="Game Commands:", width=175, height=270)
        game_commands_frame.place(x=402, y=358)

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

        ttk.Button(self.root, text="Submit", width=12, command=self.submit_map).place(x=429, y=588)

        self.root.bind("<Escape>", self.clear_search_and_filters)

        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Toggle Favorite", command=self.toggle_favorite)

    def show_folder_paths(self):
        FolderPathsDialog(self)
        # wait_window is already handled inside the dialog

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

    def refresh_map_file_selection_combobox(self):
        app_root = get_appdata_path("")
        map_names = [
            p.stem.removeprefix("ml_")
            for p in app_root.glob("ml_*.ini")
            if p.is_file()
        ]
        map_names.sort()

        self.file_selection_combo_box['values'] = map_names

        if map_names:
            if self.last_map_file and self.last_map_file in map_names:
                idx = map_names.index(self.last_map_file)
                self.file_selection_combo_box.current(idx)
            else:
                self.file_selection_combo_box.current(0)
        else:
            self.file_selection_combo_box.set("No map lists found")

        self.last_shown_map_list_name = self.combo_file_var.get().strip()

    def on_file_combo_about_to_change(self, *args):
        if not self.maps_dirty:
            self.perform_map_list_switch()
            return

        # Current = what's actually loaded and possibly dirty
        current_name = self.current_map_list_name or "Untitled"

        # Target = what the user just clicked
        target_name = self.combo_file_var.get().strip()

        if current_name == target_name:
            return

        response = messagebox.askyesnocancel(
            title="Unsaved Changes",
            message=f"You have unsaved changes in '{current_name}'.\n\n"
                    f"Do you want to save before switching to '{target_name}'?",
            detail="Yes = Save and switch\nNo = Discard changes and switch\nCancel = Stay on current list",
            icon="warning",
            parent=self.root
        )

        if response is None:  # Cancel
            self.combo_file_var.set(current_name)  # Revert combobox
            return

        if response is True:  # Save first
            # Temporarily switch var to current name to save correctly
            old_value = self.combo_file_var.get()
            self.combo_file_var.set(current_name)
            saved_ok = self.save_map_list()
            self.combo_file_var.set(target_name)  # Restore target
            if not saved_ok:
                self.combo_file_var.set(current_name)
                return

        # Proceed with switch (either saved or discarded)
        self.perform_map_list_switch()

    def perform_map_list_switch(self):
        target_name = self.combo_file_var.get().strip()
        self.current_map_list_name = target_name

        filename = f"ml_{target_name}.ini"
        if os.path.exists(filename):
            config = configparser.ConfigParser()
            config.read(str(get_appdata_path(filename)), encoding='utf-8-sig')
            if "Maps" in config:
                self.maps = list(config["Maps"].keys())
        else:
            self.maps = DEFAULT_MAPS[:]

        self.maps_dirty = False
        self.update_listview()
        self.update_window_title()

    def on_file_combo_changed(self, var_name=None, index=None, mode=None):
        self.maps = []
        filename = f"ml_{self.combo_file_var.get()}.ini"
        if os.path.exists(filename):
            config = configparser.ConfigParser()
            config.read(str(get_appdata_path(filename)), encoding='utf-8-sig')
            if "Maps" in config:
                self.maps = list(config["Maps"].keys())
        else:
            self.maps = DEFAULT_MAPS[:]
            print("maps.ini not found → using default map list")

        self.update_listview()

        # save last opened map file
        selected = self.combo_file_var.get()
        if selected and selected != "No map lists found":
            self.last_map_file = selected
            self.save_config()

    def load_config(self):
        """Load user settings from config.ini (creates nothing if missing)"""
        config = configparser.ConfigParser()
        if get_appdata_path("config.ini").exists():
            config.read(str(get_appdata_path("config.ini")), encoding='utf-8')
            if "Settings" in config:
                self.aaclient_log_path = config["Settings"].get("AAClientLog", "")
                self.workshop_path = config["Settings"].get("WorkshopPath", "")
                self.last_map_file = config["Settings"].get("LastMapFile", "")
                self.dark_mode = config["Settings"].getboolean("DarkMode", False)

    def save_config(self):
        """Save all settings to config.ini"""
        config = configparser.ConfigParser()
        config["Settings"] = {
            "AAClientLog": self.aaclient_log_path,
            "WorkshopPath": self.workshop_path,
            "LastMapFile": self.last_map_file,
            "DarkMode": str(self.dark_mode)
        }

        with get_appdata_path("config.ini").open("w", encoding="utf-8") as f:
            config.write(f)

    def update_window_title(self):
        base = f"AAPG: Map Browser {VERSION_STRING}"
        current_name = self.combo_file_var.get().strip()

        if current_name and current_name != "No map lists found":
            title = f"{base} - {current_name}"
        else:
            title = base

        if self.maps_dirty:
            title += " * (unsaved)"

        self.root.title(title)

    def validate_aaclient_log(self, path: str) -> bool:
        """Returns True if the path points to an existing file."""
        return bool(path and os.path.isfile(path.strip()))

    def validate_workshop_path(self, path: str) -> bool:
        """Checks up to the first 3 subfolders for any *.umap file."""
        if not path or not os.path.isdir(path.strip()):
            return False

        try:
            p = Path(path.strip())
            subdirs = [d for d in p.iterdir() if d.is_dir()]
            for sub in subdirs[:3]:                     # try max 3 subfolders
                if any(sub.glob("*.umap")):
                    return True
            return False
        except:
            return False

    def validate_paths(self):
        """Update both booleans (called on startup and after dialog OK)."""
        self.aaclient_log_found = self.validate_aaclient_log(self.aaclient_log_path)
        self.workshop_content_found = self.validate_workshop_path(self.workshop_path)

    def toggle_dark_mode(self):
        self.dark_mode = self.dark_var.get()
        theme = "dark" if self.dark_mode else "light"
        sv_ttk.set_theme(theme)

        # Fix persistent blue highlight on readonly Combobox
        style = ttk.Style()

        if theme == "dark":
            style.map("TCombobox",
                      selectbackground=[("readonly", "#333333")],  # dark gray
                      selectforeground=[("readonly", "#e0e0e0")],
                      )
        else:
            style.map("TCombobox",
                      selectbackground=[("readonly", "white")],
                      selectforeground=[("readonly", "black")],
                      )

        self.save_config()

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

    def get_local_maps(self):
        """Menu: Map List → Get Local Maps"""
        if not self.workshop_content_found:
            if messagebox.askyesno(
                "Path not set or invalid",
                "Workshop content path is not valid or not set.\n\n"
                "Open Folder Paths settings now?"
            ):
                self.show_folder_paths()
            else:
                messagebox.showwarning(
                    "Cannot proceed",
                    "Please set a valid Workshop Content path in Settings → Folder Paths first."
                )
            return

        workshop_dir = Path(self.workshop_path).resolve()
        if not workshop_dir.is_dir():
            messagebox.showerror(
                "Folder not found",
                f"Workshop folder not found at:\n{workshop_dir}\n\n"
                "Please check the path in Settings → Folder Paths."
            )
            return

        # Find all .umap files recursively
        umap_files = list(workshop_dir.rglob("*.umap"))

        if not umap_files:
            messagebox.showinfo(
                "No maps found",
                "No .umap files were found in the workshop folder\n"
                f"({workshop_dir})\nor any of its subfolders."
            )
            return

        # Extract map names: stem = filename without extension
        local_maps = sorted({f.stem for f in umap_files})  # sorted + unique via set
        # Append maps that ship with AAPG
        local_maps.extend(DEFAULT_MAPS)
        local_maps = [str.lower(x) for x in local_maps]



        # Apply the new list
        self.maps = list(local_maps)
        self.maps_dirty = True
        self.update_listview()
        self.update_window_title()

        messagebox.showinfo(
            "Server maps loaded",
            f"Found and loaded {len(local_maps)} unique .umap-based map names.\n\n"
            "Use File → Save or Save As to keep this list."
        )

    def get_server_maps(self):
        """Menu: Map List → Get Server Maps"""
        if not self.aaclient_log_found:
            if messagebox.askyesno(
                "Path not set or invalid",
                "AAClient.log path is not valid or not set.\n\n"
                "Open Folder Paths settings now?"
            ):
                self.show_folder_paths()
            else:
                messagebox.showwarning(
                    "Cannot proceed",
                    "Please set a valid AAClient.log path in Settings → Folder Paths first."
                )
            return

        log_path = Path(self.aaclient_log_path)
        if not log_path.is_file():
            messagebox.showerror(
                "File not found",
                f"AAClient.log not found at:\n{log_path}\n\n"
                "Please check the path in Settings → Folder Paths."
            )
            return

        # Same parsing logic as MapsFileBuilder.py
        pattern = re.compile(r"MapNamePart:'([^']+)'")

        maps: list[str] = []
        seen = set()

        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "MapNamePart" in line:
                        match = pattern.search(line)
                        if match:
                            name = match.group(1).strip()
                            if name and name not in seen:
                                seen.add(name)
                                maps.append(name)
        except Exception as e:
            messagebox.showerror(
                "Read error",
                f"Could not read AAClient.log:\n{str(e)}"
            )
            return

        if not maps:
            messagebox.showinfo(
                "No maps found",
                "No MapNamePart entries were found in the log.\n"
                "(The file might be empty or from a session without map loading.)"
            )
            return

        # Apply the new list
        self.maps = maps
        self.maps_dirty = True
        self.update_listview()
        self.update_window_title()

        messagebox.showinfo(
            "Server maps loaded",
            f"Loaded {len(maps)} unique map names from AAClient.log.\n\n"
            "Use File → Save or Save As to keep this list."
        )

    def create_new_map_list(self):

        # ── Handle unsaved changes FIRST ─────────────────────────────────────

        current_name = self.combo_file_var.get().strip()

        if self.maps_dirty:
            response = messagebox.askyesnocancel(
                title="Unsaved Changes",
                message=f"You have unsaved changes in '{current_name}'.\n\n"
                        f"Do you want to save?",
                icon="warning",
                parent=self.root
            )

            if response is None:  # Cancel
                return

            if response is True:  # Yes → save under current (old) name
                if not self.save_map_list():  # uses current combo value → old name
                    messagebox.showwarning("Save failed", "Aborted because save failed.")
                    return

        self.maps_dirty = False

        """Menu: File → New"""
        name = tk.simpledialog.askstring(
            title="New Map List",
            prompt="Enter name for the new map list:",
            parent=self.root
        )
        if not name:
            return  # user cancelled

        name = name.strip()
        if not name:
            messagebox.showwarning("Invalid name", "Name cannot be empty.")
            return

        filename = f"ml_{name}.ini"
        safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
        if not safe_name:
            messagebox.showwarning("Invalid name", "Name contains only invalid characters.")
            return

        # Overwrite protection
        if Path(filename).exists():
            if not messagebox.askyesno(
                    "File exists",
                    f"{filename} already exists.\nOverwrite it?"
            ):
                return

        # Create empty map list
        config = configparser.ConfigParser()
        config["Maps"] = {}

        with open(str(get_appdata_path(filename)), "w", encoding="utf-8") as f:
            config.write(f)

        messagebox.showinfo("Created", f"New empty map list created:\n{filename}")

        # Refresh combobox and select the new file
        self.refresh_map_file_selection_combobox()
        self.current_map_list_name = name

        try:
            idx = self.file_selection_combo_box['values'].index(name)
            self.file_selection_combo_box.current(idx)
            self.on_file_combo_changed()
        except ValueError:
            pass  # should not happen, but safe

    def save_map_list_as(self):
        """Menu: File → Save As"""
        if not self.maps:
            messagebox.showwarning("Nothing to save", "Current map list is empty.")
            return

        name = tk.simpledialog.askstring(
            title="Save Map List As",
            prompt="Enter name for this map list:",
            initialvalue=self.combo_file_var.get(),  # suggest current name
            parent=self.root
        )
        if not name:
            return  # cancelled

        name = name.strip()
        if not name:
            messagebox.showwarning("Invalid name", "Name cannot be empty.")
            return

        filename = f"ml_{name}.ini"

        # Overwrite confirmation
        if Path(str(get_appdata_path(filename))).exists() and filename != f"ml_{self.combo_file_var.get()}.ini":
            if not messagebox.askyesno(
                    "Overwrite?",
                    f"{filename} already exists.\nOverwrite it?"
            ):
                return

        # Build config from current self.maps
        config = configparser.ConfigParser()
        config["Maps"] = {m: "" for m in self.maps}  # empty values = typical format

        try:
            with open(str(get_appdata_path(filename)), "w", encoding="utf-8") as f:
                config.write(f)
            messagebox.showinfo("Saved", f"Map list saved as:\n{filename}")
        except Exception as e:
            messagebox.showerror("Save failed", f"Could not save file:\n{str(e)}")
            return

        # Refresh combobox and switch to the new/updated file
        self.refresh_map_file_selection_combobox()
        self.current_map_list_name = name

        try:
            idx = self.file_selection_combo_box['values'].index(name)
            self.file_selection_combo_box.current(idx)
            self.on_file_combo_changed()
            self.last_map_file = name
            self.save_config()
            self.maps_dirty = False
            self.update_window_title()
        except ValueError:
            pass

    def save_map_list(self):
        """Menu: File → Save"""
        current_name = self.combo_file_var.get().strip()
        if not current_name or current_name == "No map lists found":
            # No current file → force Save As
            self.save_map_list_as()
            return not self.maps_dirty  # True if save succeeded

        filename = f"ml_{current_name}.ini"

        config = configparser.ConfigParser()
        config["Maps"] = {m: "" for m in self.maps}

        try:
            with open(str(get_appdata_path(filename)), "w", encoding="utf-8") as f:
                config.write(f)
            self.maps_dirty = False
            self.update_window_title()
            print(f"Saved: {filename}")
            return True
        except Exception as e:
            messagebox.showerror("Save failed", f"Could not save:\n{str(e)}")
            return False

    def rename_current_map_list(self):
        """Menu: Map List → Rename Current"""
        current_name = self.combo_file_var.get().strip()

        if not current_name or current_name == "No map lists found":
            messagebox.showwarning("No selection", "Please select an existing map list first.")
            return

        old_filename = f"ml_{current_name}.ini"
        old_path = get_appdata_path(old_filename)

        if not old_path.is_file():
            messagebox.showerror("File missing", f"Cannot find:\n{old_filename}\n\nNothing to rename.")
            return

        # ── Handle unsaved changes FIRST ─────────────────────────────────────
        if self.maps_dirty:
            response = messagebox.askyesnocancel(
                title="Unsaved Changes",
                message=f"You have unsaved changes in '{current_name}'.\n\n"
                        f"Do you want to save before renaming?",
                detail="Yes = Save → then rename\nNo = Discard changes → then rename\nCancel = Abort",
                icon="warning",
                parent=self.root
            )

            if response is None:  # Cancel
                return

            if response is True:  # Yes → save under current (old) name
                if not self.save_map_list():  # uses current combo value → old name
                    messagebox.showwarning("Save failed", "Rename aborted because save failed.")
                    return

        self.maps_dirty = False

        # ── Now ask for new name ─────────────────────────────────────────────
        new_name = tk.simpledialog.askstring(
            title="Rename Map List",
            prompt="Enter the new name for this map list:",
            initialvalue=current_name,
            parent=self.root
        )

        if new_name is None:
            return  # cancelled

        new_name = new_name.strip()
        if not new_name:
            messagebox.showwarning("Invalid name", "Name cannot be empty.")
            return

        if new_name == current_name:
            messagebox.showinfo("No change", "The name is the same — nothing to do.")
            return

        new_filename = f"ml_{new_name}.ini"
        new_path = get_appdata_path(new_filename)

        # Overwrite protection
        if new_path.exists():
            if not messagebox.askyesno(
                    "File exists",
                    f"{new_filename} already exists.\nOverwrite it?\n\n(The old file will be replaced.)"
            ):
                return

        try:

            if new_path.exists():
                new_path.unlink()

            # Perform the rename on disk
            os.rename(old_path, new_path)

            # ── Update UI to new name ────────────────────────────────────────
            self.refresh_map_file_selection_combobox()

            # Try to select the newly renamed item
            values = self.file_selection_combo_box['values']
            if new_name in values:
                idx = values.index(new_name)
                self.file_selection_combo_box.current(idx)
                self.perform_map_list_switch()  # reloads from new file
            else:
                # fallback
                self.combo_file_var.set(new_name)

            # Update last opened if necessary
            if self.last_map_file == current_name:
                self.last_map_file = new_name
                self.save_config()

            self.current_map_list_name = new_name
            self.update_window_title()

            messagebox.showinfo("Renamed", f"Renamed successfully:\n{old_filename} → {new_filename}")

        except FileExistsError:
            messagebox.showerror("Error", f"Cannot rename — {new_filename} still exists after check.")
        except PermissionError:
            messagebox.showerror("Permission denied", "Cannot rename file — check permissions.")
        except Exception as e:
            messagebox.showerror("Rename failed", f"Unexpected error:\n{str(e)}")

    def delete_current_map_list(self):
        """Menu: Map List → Delete Current"""
        current_name = self.combo_file_var.get().strip()

        if not current_name or current_name == "No map lists found":
            messagebox.showwarning(
                "Nothing selected",
                "No map list is currently selected."
            )
            return

        filename = f"ml_{current_name}.ini"
        path = Path(str(get_appdata_path(filename)))

        if not path.is_file():
            messagebox.showerror(
                "File missing",
                f"The file {filename} was not found on disk.\n"
                "It may have already been deleted or moved."
            )
            return

        # Confirmation – make it scary/explicit
        confirm = messagebox.askyesno(
            title="Delete Map List",
            message=f"Are you sure you want to **permanently delete** this map list?\n\n"
                    f"File: {filename}\n"
                    f"Contains: {len(self.maps)} maps\n\n"
                    "This action cannot be undone.",
            icon="warning"
        )

        if not confirm:
            return

        try:
            path.unlink()  # delete the file

            # Clear dirty state since file is gone
            self.maps_dirty = False

            # Refresh combobox → will remove the deleted item
            self.refresh_map_file_selection_combobox()

            # Try to select something sensible
            values = self.file_selection_combo_box['values']
            if values:
                self.file_selection_combo_box.current(0)
                self.on_file_combo_changed()
            else:
                # No lists left → fall back to default
                self.combo_file_var.set("")
                self.maps = DEFAULT_MAPS[:]
                self.update_listview()

            self.update_window_title()

            messagebox.showinfo(
                "Deleted",
                f"Map list deleted successfully:\n{filename}"
            )

        except PermissionError:
            messagebox.showerror(
                "Permission denied",
                f"Cannot delete {filename}.\n"
                "The file may be open in another program or you lack permission."
            )
        except Exception as e:
            messagebox.showerror(
                "Delete failed",
                f"Could not delete the file:\n{str(e)}"
            )

    def on_closing(self):
        """Called when user clicks the window close button (X)"""
        if self.maps_dirty:
            response = messagebox.askyesnocancel(
                title="Unsaved Changes",
                message="You have unsaved changes in the current map list.\n\n"
                        "Do you want to save before closing?",
                detail="Yes = Save and exit\nNo = Discard changes and exit\nCancel = Stay in the app",
                icon="warning"
            )

            if response is None:       # Cancel
                return                 # do nothing, keep window open

            if response is True:       # Yes → save first
                self.save_map_list()   # or self.save_map_list_as() if you prefer always asking
                if self.maps_dirty:    # still dirty? → save failed or was cancelled
                    return

        # Either no changes, or user chose No, or save succeeded
        self.root.destroy()

class FolderPathsDialog(tk.Toplevel):
    def __init__(self, parent: AAPGMapBrowser):
        super().__init__(parent.root)
        self.title("Folder Paths")
        self.resizable(False, False)
        self.parent = parent
        self.grab_set()                     # modal

        self.log_var = tk.StringVar(value=parent.aaclient_log_path)
        self.ws_var  = tk.StringVar(value=parent.workshop_path)

        self.create_widgets()
        self.validate_all()                 # initial validation

        # Auto-validate when user types
        self.log_var.trace_add("write", lambda *a: self.validate_log())
        self.ws_var.trace_add("write",  lambda *a: self.validate_workshop())

    def create_widgets(self):
        # AA Log
        ttk.Label(self, text="AA Log File:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.log_icon = ttk.Label(self, text=" ", width=3)
        self.log_icon.grid(row=0, column=1)
        ttk.Entry(self, textvariable=self.log_var, width=55).grid(row=0, column=2, padx=5, pady=8)
        ttk.Button(self, text="Browse...", command=self.browse_log).grid(row=0, column=3, padx=5, pady=8)

        # Workshop
        ttk.Label(self, text="AA Workshop Content:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.ws_icon = ttk.Label(self, text=" ", width=3)
        self.ws_icon.grid(row=1, column=1)
        ttk.Entry(self, textvariable=self.ws_var, width=55).grid(row=1, column=2, padx=5, pady=8)
        ttk.Button(self, text="Browse...", command=self.browse_workshop).grid(row=1, column=3, padx=5, pady=8)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=15)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=8)
        ttk.Button(btn_frame, text="OK",     command=self.on_ok).pack(side="right")


    def validate_log(self):
        valid = self.parent.validate_aaclient_log(self.log_var.get())
        self.log_icon.config(text="✅" if valid else "❌",
                             foreground="green" if valid else "red")
        return valid

    def validate_workshop(self):
        valid = self.parent.validate_workshop_path(self.ws_var.get())
        self.ws_icon.config(text="✅" if valid else "❌",
                            foreground="green" if valid else "red")
        return valid

    def validate_all(self):
        self.validate_log()
        self.validate_workshop()

    def browse_log(self):
        path = filedialog.askopenfilename(
            title="Select AAClient.log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")],
            initialdir=Path(self.log_var.get()).parent if self.log_var.get() else None
        )
        if path:
            self.log_var.set(path)

    def browse_workshop(self):
        path = filedialog.askdirectory(
            title="Select Workshop Content Folder",
            initialdir=self.ws_var.get() or None
        )
        if path:
            self.ws_var.set(path)

    def on_ok(self):
        # Final validation
        log_ok = self.validate_log()
        ws_ok  = self.validate_workshop()

        if not (log_ok and ws_ok):
            if not messagebox.askyesno("Warning",
                "One or both paths look invalid.\n\nSave anyway?"):
                return

        # Save to main window
        self.parent.aaclient_log_path = self.log_var.get().strip()
        self.parent.workshop_path     = self.ws_var.get().strip()
        self.parent.validate_paths()          # update booleans
        self.parent.save_config()

        self.destroy()

if __name__ == "__main__":
    AAPGMapBrowser()