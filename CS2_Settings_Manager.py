"""
CS2 Settings Manager
Single Python GUI app replacing the two old BAT files:
1. Creates the required CS2 settings folders.
2. Applies a selected settings folder to every Steam userdata profile.
3. Opens the app folder, Steam userdata folder, and each settings folder.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk

APP_NAME = "CS2 Settings Manager"
APP_VERSION = "V3"

SETTING_FOLDERS = [
    ("Main", "SET MAIN"),
    ("Tryhard", "SET TRYHARD"),
    ("Farming", "SET FARMING"),
    ("Armsrace", "SET ARMSRACE"),
    ("Skin Inspect", "SET SKIN INSPECT"),
    ("Playhour", "SET PLAYHOUR"),
]

# CS2/HUD inspired palette
BG = "#070b12"
BG_2 = "#0b111c"
PANEL = "#101a2b"
PANEL_2 = "#17233a"
PANEL_3 = "#1d2d48"
INK = "#05080d"
TEXT = "#edf5ff"
MUTED = "#9fb0c9"
MUTED_2 = "#6f809a"
BORDER = "#2b3f5f"
BORDER_LIGHT = "#526987"
BUTTON = "#203452"
BUTTON_HOVER = "#2b466d"
ORANGE = "#f59e0b"
ORANGE_2 = "#ffb22e"
ORANGE_DARK = "#9a5a05"
CYAN = "#22d3ee"
CYAN_DARK = "#0891b2"
GREEN = "#22c55e"
GREEN_DARK = "#15803d"
RED = "#ef4444"
SHADOW = "#02040a"

FONT_TITLE = ("Segoe UI Black", 25)
FONT_SUBTITLE = ("Segoe UI", 10)
FONT_SECTION = ("Segoe UI Semibold", 13)
FONT_BODY = ("Segoe UI", 10)
FONT_BODY_BOLD = ("Segoe UI Semibold", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 9)


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


def shift_color(color: str, amount: int) -> str:
    r, g, b = hex_to_rgb(color)
    return rgb_to_hex((max(0, min(255, r + amount)), max(0, min(255, g + amount)), max(0, min(255, b + amount))))


def get_app_folder() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_asset_path(relative: str) -> Path:
    # Works from source, and also when PyInstaller unpacks bundled assets.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundled = Path(getattr(sys, "_MEIPASS")) / relative
        if bundled.exists():
            return bundled
    return get_app_folder() / relative


def open_folder(path: Path) -> None:
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(str(path))

    system_name = platform.system().lower()
    if system_name == "windows":
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif system_name == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def detect_steam_userdata() -> Path:
    default_path = Path(r"C:\Program Files (x86)\Steam\userdata")
    if default_path.exists():
        return default_path

    if platform.system().lower() == "windows":
        try:
            import winreg  # type: ignore

            registry_locations = [
                (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Valve\Steam"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Valve\Steam"),
            ]
            for hive, key_path in registry_locations:
                try:
                    with winreg.OpenKey(hive, key_path) as key:
                        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
                        userdata = Path(str(steam_path).replace("/", os.sep)) / "userdata"
                        if userdata.exists():
                            return userdata
                except OSError:
                    continue
        except Exception:
            pass

    return default_path


def ensure_setting_folders(base_folder: Path) -> tuple[list[Path], list[Path]]:
    created: list[Path] = []
    existing: list[Path] = []
    for _, folder_name in SETTING_FOLDERS:
        folder = base_folder / folder_name
        if folder.exists():
            existing.append(folder)
        else:
            folder.mkdir(parents=True, exist_ok=True)
            created.append(folder)
    return created, existing


def copy_folder_contents(source: Path, destination: Path) -> tuple[int, int]:
    file_count = 0
    folder_count = 0

    for item in source.rglob("*"):
        relative = item.relative_to(source)
        target = destination / relative

        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            folder_count += 1
        elif item.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            file_count += 1

    return file_count, folder_count


class GameButton(tk.Canvas):
    """A small 3D HUD style button that still behaves like a normal Tk widget."""

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command,
        *,
        fill: str = BUTTON,
        accent: str = CYAN,
        fg: str = TEXT,
        width: int = 154,
        height: int = 42,
        parent_bg: str = PANEL,
    ) -> None:
        super().__init__(parent, width=width, height=height, bg=parent_bg, highlightthickness=0, bd=0, cursor="hand2")
        self.text = text
        self.command = command
        self.fill = fill
        self.accent = accent
        self.fg = fg
        self.button_width = width
        self.button_height = height
        self.parent_bg = parent_bg
        self.hover = False
        self.pressed = False
        self.enabled = True
        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", lambda _event: self._draw())

    def configure(self, cnf=None, **kw):  # type: ignore[override]
        state = kw.pop("state", None)
        if state is not None:
            self.set_enabled(str(state) != "disabled")
        if kw:
            return super().configure(cnf, **kw)
        return None

    config = configure

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        self.configure(cursor="hand2" if enabled else "arrow")
        self._draw()

    def _on_enter(self, _event=None) -> None:
        if self.enabled:
            self.hover = True
            self._draw()

    def _on_leave(self, _event=None) -> None:
        self.hover = False
        self.pressed = False
        self._draw()

    def _on_press(self, _event=None) -> None:
        if self.enabled:
            self.pressed = True
            self._draw()

    def _on_release(self, event=None) -> None:
        if self.enabled and self.pressed:
            self.pressed = False
            self._draw()
            x = getattr(event, "x", 0)
            y = getattr(event, "y", 0)
            if 0 <= x <= self.winfo_width() and 0 <= y <= self.winfo_height():
                self.command()

    def _draw(self) -> None:
        self.delete("all")
        w = max(self.winfo_width(), 40)
        h = max(self.winfo_height(), self.button_height)
        offset = 2 if self.pressed else 0
        fill = self.fill
        if not self.enabled:
            fill = "#344154"
            text_color = MUTED_2
            accent = "#526071"
        else:
            text_color = self.fg
            accent = self.accent
            if self.hover:
                fill = shift_color(fill, 18)

        x0, y0 = 3 + offset, 3 + offset
        x1, y1 = w - 6 + offset, h - 8 + offset
        cut = 10

        # Shadow and body.
        self.create_polygon(
            8,
            8,
            w - 1,
            8,
            w - 1,
            h - 1,
            8,
            h - 1,
            fill=SHADOW,
            outline="",
        )
        self.create_polygon(
            x0 + cut,
            y0,
            x1,
            y0,
            x1,
            y1 - cut,
            x1 - cut,
            y1,
            x0,
            y1,
            x0,
            y0 + cut,
            fill=fill,
            outline=BORDER_LIGHT,
            width=1,
        )
        # 3D bevel.
        self.create_line(x0 + cut, y0 + 1, x1 - 1, y0 + 1, fill=shift_color(fill, 55), width=2)
        self.create_line(x0 + 1, y0 + cut, x0 + 1, y1 - 1, fill=shift_color(fill, 40), width=2)
        self.create_line(x0 + 2, y1 - 1, x1 - cut, y1 - 1, fill=shift_color(fill, -55), width=2)
        self.create_line(x1 - 1, y0 + 2, x1 - 1, y1 - cut, fill=shift_color(fill, -65), width=2)
        # CS2 orange/cyan accent strip.
        self.create_polygon(x0, y0 + cut, x0 + cut, y0, x0 + cut + 6, y0, x0, y0 + cut + 16, fill=accent, outline="")
        self.create_line(x0 + 14, y1 - 4, x1 - 18, y1 - 4, fill=accent, width=1)
        self.create_text(
            w // 2 + offset,
            h // 2 - 2 + offset,
            text=self.text,
            fill=text_color,
            font=FONT_BODY_BOLD,
        )


class CS2SettingsManager(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.app_folder = get_app_folder()
        self.steam_userdata = tk.StringVar(value=str(detect_steam_userdata()))
        self.selected_setting = tk.StringVar(value=SETTING_FOLDERS[0][1])
        self.is_busy = False
        self.preset_buttons: list[tk.Radiobutton] = []

        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1180x790")
        self.minsize(1160, 760)
        self.configure(bg=BG)

        try:
            icon_path = get_asset_path("assets/app_icon.ico")
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass

        self._configure_style()
        self._build_ui()
        self._refresh_status(log=False)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=FONT_BODY)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=FONT_SMALL)
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT, font=FONT_BODY)
        style.configure("PanelMuted.TLabel", background=PANEL, foreground=MUTED, font=FONT_SMALL)
        style.configure("CardTitle.TLabel", background=PANEL, foreground=TEXT, font=FONT_SECTION)
        style.configure("Status.TLabel", background=PANEL_2, foreground=TEXT, font=FONT_SMALL)
        style.configure(
            "TEntry",
            fieldbackground=INK,
            foreground=TEXT,
            insertcolor=TEXT,
            bordercolor=BORDER_LIGHT,
            lightcolor=BORDER_LIGHT,
            darkcolor=SHADOW,
            padding=5,
        )
        style.configure("Horizontal.TProgressbar", troughcolor=INK, background=ORANGE, bordercolor=PANEL)
        style.configure("Vertical.TScrollbar", background=PANEL_3, troughcolor=INK, arrowcolor=TEXT)

    def _make_button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        accent: str | None = None,
        width: int | None = None,
        height: int = 42,
        fill: str | None = None,
        parent_bg: str | None = None,
    ) -> GameButton:
        button_fill = fill or (ORANGE_DARK if accent == ORANGE else BUTTON)
        return GameButton(
            parent,
            text.upper(),
            command,
            fill=button_fill,
            accent=accent or CYAN,
            width=width or 158,
            height=height,
            parent_bg=parent_bg or PANEL,
        )

    def _panel(self, parent: tk.Widget) -> tk.Frame:
        frame = tk.Frame(parent, bg=PANEL, bd=2, relief="ridge", highlightbackground=BORDER, highlightthickness=1)
        return frame

    def _section_title(self, parent: tk.Widget, title: str, subtitle: str, row: int) -> None:
        wrap = tk.Frame(parent, bg=PANEL)
        wrap.grid(row=row, column=0, sticky="ew", padx=18, pady=(16, 8))
        wrap.grid_columnconfigure(1, weight=1)
        tk.Frame(wrap, bg=ORANGE, width=5).grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 10))
        ttk.Label(wrap, text=title.upper(), style="CardTitle.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(wrap, text=subtitle, style="PanelMuted.TLabel").grid(row=1, column=1, sticky="w", pady=(3, 0))

    def _build_ui(self) -> None:
        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True, padx=22, pady=18)

        self._build_header(root)

        content = tk.Frame(root, bg=BG)
        content.pack(fill="both", expand=True, pady=(18, 0))
        content.grid_columnconfigure(0, weight=6)
        content.grid_columnconfigure(1, weight=4)
        content.grid_rowconfigure(0, weight=4, minsize=360)
        content.grid_rowconfigure(1, weight=1, minsize=220)

        self._build_apply_panel(content)
        self._build_folder_panel(content)
        self._build_log_panel(content)

    def _build_header(self, parent: tk.Widget) -> None:
        header = tk.Frame(parent, bg=BG)
        header.pack(fill="x")
        header.grid_columnconfigure(1, weight=1)

        logo = tk.Canvas(header, width=108, height=76, bg=BG, highlightthickness=0)
        logo.grid(row=0, column=0, sticky="w", padx=(0, 14))
        logo.create_polygon(4, 12, 84, 12, 104, 32, 104, 68, 24, 68, 4, 48, fill=PANEL_2, outline=BORDER_LIGHT, width=2)
        logo.create_polygon(10, 18, 62, 18, 78, 34, 26, 34, fill=ORANGE, outline="")
        logo.create_line(13, 61, 97, 61, fill=CYAN, width=3)
        logo.create_text(54, 44, text="CS2", fill=TEXT, font=("Segoe UI Black", 25))

        title_area = tk.Frame(header, bg=BG)
        title_area.grid(row=0, column=1, sticky="ew")
        tk.Label(title_area, text="CS2 SETTINGS MANAGER", bg=BG, fg=TEXT, font=FONT_TITLE).pack(anchor="w")
        tk.Frame(title_area, bg=ORANGE, height=3).pack(anchor="w", fill="x", pady=(10, 0))

        badge = tk.Frame(header, bg=PANEL_2, bd=2, relief="raised", highlightbackground=BORDER_LIGHT, highlightthickness=1)
        badge.grid(row=0, column=2, sticky="e", padx=(14, 0))
        tk.Label(badge, text=APP_VERSION, bg=PANEL_2, fg=ORANGE_2, font=FONT_BODY_BOLD, padx=18, pady=8).pack()

    def _build_apply_panel(self, parent: tk.Widget) -> None:
        panel = self._panel(parent)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(5, weight=1)

        self._section_title(panel, "Apply Settings", "Pick a preset, then deploy it to every Steam userdata profile.", 0)

        preset_frame = tk.Frame(panel, bg=PANEL)
        preset_frame.grid(row=1, column=0, sticky="ew", padx=18, pady=(8, 10))
        for c in range(3):
            preset_frame.grid_columnconfigure(c, weight=1, uniform="preset")

        for idx, (label, folder_name) in enumerate(SETTING_FOLDERS):
            rb = tk.Radiobutton(
                preset_frame,
                text=label.upper(),
                value=folder_name,
                variable=self.selected_setting,
                command=self._sync_preset_buttons,
                indicatoron=0,
                bg=BUTTON,
                fg=TEXT,
                selectcolor=ORANGE,
                activebackground=BUTTON_HOVER,
                activeforeground=TEXT,
                relief="raised",
                bd=4,
                highlightthickness=1,
                highlightbackground=BORDER_LIGHT,
                font=FONT_BODY_BOLD,
                cursor="hand2",
                padx=10,
                pady=11,
            )
            rb.grid(row=idx // 3, column=idx % 3, sticky="ew", padx=5, pady=5)
            self.preset_buttons.append(rb)
        self._sync_preset_buttons()

        path_frame = tk.Frame(panel, bg=PANEL)
        path_frame.grid(row=2, column=0, sticky="ew", padx=18, pady=(8, 4))
        path_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(path_frame, text="STEAM USERDATA FOLDER", style="PanelMuted.TLabel").grid(row=0, column=0, sticky="w", columnspan=3)
        self.userdata_entry = ttk.Entry(path_frame, textvariable=self.steam_userdata)
        self.userdata_entry.grid(row=1, column=0, sticky="ew", pady=(7, 0), ipady=5)
        self._make_button(path_frame, "Browse", self._browse_userdata, width=112, height=40).grid(row=1, column=1, padx=(9, 0), pady=(7, 0))
        self._make_button(path_frame, "Open", self._open_userdata, width=92, height=40).grid(row=1, column=2, padx=(9, 0), pady=(7, 0))

        action_frame = tk.Frame(panel, bg=PANEL)
        action_frame.grid(row=3, column=0, sticky="ew", padx=18, pady=(16, 12))
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        self.apply_button = self._make_button(
            action_frame,
            "Apply Selected Settings",
            self._apply_selected_async,
            accent=GREEN,
            fill=GREEN_DARK,
            height=48,
        )
        self.apply_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._make_button(action_frame, "Refresh Status", self._refresh_status, accent=CYAN, height=48).grid(row=0, column=1, sticky="ew", padx=(8, 0))

        progress_wrap = tk.Frame(panel, bg=INK, bd=1, relief="sunken", highlightbackground=BORDER, highlightthickness=1)
        progress_wrap.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 18))
        progress_wrap.grid_columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(progress_wrap, mode="indeterminate", style="Horizontal.TProgressbar")
        self.progress.grid(row=0, column=0, sticky="ew", padx=3, pady=3)

    def _build_folder_panel(self, parent: tk.Widget) -> None:
        panel = self._panel(parent)
        panel.grid(row=0, column=1, rowspan=2, sticky="nsew", pady=(0, 12))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(3, weight=1)

        self._section_title(panel, "Folders", "Create and open the exact SET folders you need.", 0)

        top_actions = tk.Frame(panel, bg=PANEL)
        top_actions.grid(row=1, column=0, sticky="ew", padx=18, pady=(8, 10))
        top_actions.grid_columnconfigure(0, weight=1, uniform="folder_actions")
        top_actions.grid_columnconfigure(1, weight=1, uniform="folder_actions")
        self._make_button(top_actions, "Create SET Folders", self._create_folders, accent=ORANGE, fill=ORANGE_DARK, height=46).grid(
            row=0, column=0, sticky="ew", padx=(0, 7)
        )
        self._make_button(top_actions, "Open App Folder", self._open_app_folder, accent=CYAN, height=46).grid(
            row=0, column=1, sticky="ew", padx=(7, 0)
        )

        self.folder_list = tk.Frame(panel, bg=PANEL)
        self.folder_list.grid(row=3, column=0, sticky="nsew", padx=18, pady=(4, 10))
        self.folder_list.grid_columnconfigure(0, weight=1)
        self._draw_folder_rows()

        status_box = tk.Frame(panel, bg=PANEL_2, bd=2, relief="sunken", highlightbackground=BORDER, highlightthickness=1)
        status_box.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 16))
        status_box.grid_columnconfigure(0, weight=1)
        self.status_label = ttk.Label(status_box, text="Status loading...", style="Status.TLabel", wraplength=390, justify="left")
        self.status_label.grid(row=0, column=0, sticky="ew", padx=12, pady=8)

    def _build_log_panel(self, parent: tk.Widget) -> None:
        panel = self._panel(parent)
        panel.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        log_header = tk.Frame(panel, bg=PANEL)
        log_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
        log_header.grid_columnconfigure(0, weight=1)
        title_wrap = tk.Frame(log_header, bg=PANEL)
        title_wrap.grid(row=0, column=0, sticky="w")
        tk.Frame(title_wrap, bg=CYAN, width=5, height=28).pack(side="left", padx=(0, 10))
        ttk.Label(title_wrap, text="ACTIVITY LOG", style="CardTitle.TLabel").pack(side="left")
        self._make_button(log_header, "Clear", self._clear_log, width=104, height=38).grid(row=0, column=1, sticky="e")

        text_wrap = tk.Frame(panel, bg=INK, bd=2, relief="sunken", highlightbackground=BORDER, highlightthickness=1)
        text_wrap.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        text_wrap.grid_rowconfigure(0, weight=1)
        text_wrap.grid_columnconfigure(0, weight=1)

        self.log_text = tk.Text(
            text_wrap,
            bg=INK,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=FONT_MONO,
            wrap="word",
            height=8,
            padx=10,
            pady=10,
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(text_wrap, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self._log("Ready. Create folders first, then put your configs inside the correct SET folder.")

    def _sync_preset_buttons(self) -> None:
        selected = self.selected_setting.get()
        for rb in self.preset_buttons:
            if rb.cget("value") == selected:
                rb.configure(bg=ORANGE, fg=INK, activebackground=ORANGE_2, activeforeground=INK, relief="sunken")
            else:
                rb.configure(bg=BUTTON, fg=TEXT, activebackground=BUTTON_HOVER, activeforeground=TEXT, relief="raised")

    def _draw_folder_rows(self) -> None:
        for child in self.folder_list.winfo_children():
            child.destroy()

        self.folder_list.grid_columnconfigure(0, weight=1)
        for index, (_label, folder_name) in enumerate(SETTING_FOLDERS):
            folder = self.app_folder / folder_name
            exists = folder.exists()
            row_bg = PANEL_2 if index % 2 == 0 else PANEL_3
            row = tk.Frame(self.folder_list, bg=row_bg, bd=1, relief="ridge", highlightbackground=BORDER, highlightthickness=1)
            row.grid(row=index, column=0, sticky="ew", pady=3)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, minsize=124)

            left = tk.Frame(row, bg=row_bg)
            left.grid(row=0, column=0, sticky="ew", padx=11, pady=5)
            tk.Label(left, text=folder_name, bg=row_bg, fg=TEXT, font=FONT_BODY_BOLD).pack(anchor="w")
            status_text = "READY" if exists else "MISSING"
            status_color = GREEN if exists else RED
            tk.Label(left, text=status_text, bg=row_bg, fg=status_color, font=("Segoe UI Semibold", 8)).pack(anchor="w", pady=(2, 0))
            self._make_button(row, "Open", lambda p=folder: self._safe_open(p), width=100, height=32, parent_bg=row_bg).grid(
                row=0, column=1, sticky="e", padx=(4, 10), pady=5
            )

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")

    def _clear_log(self) -> None:
        self.log_text.delete("1.0", "end")

    def _set_busy(self, busy: bool) -> None:
        self.is_busy = busy
        if busy:
            self.apply_button.configure(state="disabled")
            self.progress.start(12)
        else:
            self.apply_button.configure(state="normal")
            self.progress.stop()

    def _short_path(self, path: Path, max_chars: int = 52) -> str:
        text = str(path)
        if len(text) <= max_chars:
            return text
        return "..." + text[-(max_chars - 3):]

    def _refresh_status(self, log: bool = True) -> None:
        missing = [name for _, name in SETTING_FOLDERS if not (self.app_folder / name).exists()]
        userdata_path = Path(self.steam_userdata.get().strip())
        profiles = []
        if userdata_path.exists():
            profiles = [p for p in userdata_path.iterdir() if p.is_dir()]

        folder_status = "All SET folders are ready." if not missing else f"Missing: {', '.join(missing)}"
        steam_status = f"Steam profiles found: {len(profiles)}" if userdata_path.exists() else "Steam userdata folder not found."
        self.status_label.configure(text=f"APP: {self._short_path(self.app_folder, 42)}\n{folder_status} | {steam_status}")
        self._draw_folder_rows()
        if log:
            self._log("Status refreshed.")

    def _browse_userdata(self) -> None:
        selected = filedialog.askdirectory(title="Select Steam userdata folder")
        if selected:
            self.steam_userdata.set(selected)
            self._refresh_status()

    def _safe_open(self, path: Path) -> None:
        try:
            if not path.exists() and path.name in [folder for _, folder in SETTING_FOLDERS]:
                create = messagebox.askyesno("Folder missing", f"{path.name} does not exist. Create it now?")
                if create:
                    path.mkdir(parents=True, exist_ok=True)
                    self._log(f"Created folder: {path}")
                    self._draw_folder_rows()
                else:
                    return
            open_folder(path)
        except Exception as exc:
            messagebox.showerror("Open folder failed", str(exc))
            self._log(f"Open folder failed: {exc}")

    def _open_app_folder(self) -> None:
        self._safe_open(self.app_folder)

    def _open_userdata(self) -> None:
        self._safe_open(Path(self.steam_userdata.get().strip()))

    def _create_folders(self) -> None:
        try:
            created, existing = ensure_setting_folders(self.app_folder)
            for folder in created:
                self._log(f"Created: {folder.name}")
            for folder in existing:
                self._log(f"Already exists: {folder.name}")
            self._refresh_status()
            messagebox.showinfo("Folder setup completed", f"Created {len(created)} folder(s). {len(existing)} already existed.")
        except Exception as exc:
            messagebox.showerror("Folder setup failed", str(exc))
            self._log(f"Folder setup failed: {exc}")

    def _apply_selected_async(self) -> None:
        if self.is_busy:
            return

        selected_folder_name = self.selected_setting.get()
        source = self.app_folder / selected_folder_name
        userdata_path = Path(self.steam_userdata.get().strip())

        if source.exists() and not list(source.rglob("*")):
            proceed = messagebox.askyesno(
                "Selected folder is empty",
                f"{selected_folder_name} is empty. Apply anyway?",
            )
            if not proceed:
                self._log("Apply cancelled because selected folder is empty.")
                return

        thread = threading.Thread(target=self._apply_selected, args=(selected_folder_name, source, userdata_path), daemon=True)
        thread.start()

    def _apply_selected(self, selected_folder_name: str, source: Path, userdata_path: Path) -> None:
        self.after(0, lambda: self._set_busy(True))
        try:
            if not source.exists():
                raise FileNotFoundError(f"Settings folder not found: {source}")
            if not userdata_path.exists():
                raise FileNotFoundError(f"Steam userdata folder not found: {userdata_path}")

            profiles = [p for p in userdata_path.iterdir() if p.is_dir()]
            if not profiles:
                raise FileNotFoundError(f"No Steam profile folders found inside: {userdata_path}")

            self.after(0, lambda: self._log(f"Applying {selected_folder_name} to {len(profiles)} Steam profile(s)..."))
            total_files = 0
            total_folders = 0
            failures: list[str] = []

            for profile in profiles:
                try:
                    files, folders = copy_folder_contents(source, profile)
                    total_files += files
                    total_folders += folders
                    self.after(0, lambda p=profile, f=files: self._log(f"Applied to {p.name}: {f} file(s) copied."))
                except Exception as exc:
                    failures.append(f"{profile.name}: {exc}")
                    self.after(0, lambda p=profile, e=exc: self._log(f"Failed for {p.name}: {e}"))

            if failures:
                message = "Some profiles failed:\n\n" + "\n".join(failures[:8])
                if len(failures) > 8:
                    message += f"\n...and {len(failures) - 8} more."
                self.after(0, lambda: messagebox.showwarning("Applied with warnings", message))
            else:
                self.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Settings applied",
                        f"{selected_folder_name} applied successfully.\n\nProfiles: {len(profiles)}\nFiles copied: {total_files}\nFolders checked: {total_folders}",
                    ),
                )

            self.after(0, lambda: self._log(f"Done. Files copied: {total_files}. Profiles touched: {len(profiles)}."))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("Apply failed", str(exc)))
            self.after(0, lambda: self._log(f"Apply failed: {exc}"))
        finally:
            self.after(0, lambda: self._set_busy(False))
            self.after(0, self._refresh_status)


def main() -> None:
    app = CS2SettingsManager()
    app.mainloop()


if __name__ == "__main__":
    main()
