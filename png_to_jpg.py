import os
import sys
import time
import queue
import threading
import subprocess
import zipfile
import io
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, unquote

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from tkinter.scrolledtext import ScrolledText
    from tkinter import font as tkfont
except ImportError:
    print("tkinter not found.")
    print("Reinstall Python and make sure the tkinter/tcl-tk component is included.")
    try:
        input("Press Enter to exit...")
    except Exception:
        pass
    sys.exit(1)

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except Exception:
    TkinterDnD = None
    DND_FILES = None
    DND_AVAILABLE = False

try:
    from PIL import Image
except ImportError:
    print("Pillow library not found.")
    print("Install it with: python -m pip install Pillow")
    try:
        input("Press Enter to exit...")
    except Exception:
        pass
    sys.exit(1)


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "OUTPUT"

PNG_EXT = ".png"
ZIP_EXT = ".zip"

LANGUAGES = ("en", "ru")
CONFLICT_CODES = ("rename", "overwrite", "skip")

TRANSLATIONS = {
    "en": {
        "app_title": "PNG → JPG Converter",
        "language": "Language",
        "frame_add": "Add",
        "dnd_hint": "Drop folders, PNG files or ZIP archives here",
        "dnd_unavailable_hint": "Drag-and-drop is unavailable. Install 'tkinterdnd2' or use the buttons below.",
        "btn_add_folder": "Add folder",
        "btn_add_files": "Add files / ZIP",
        "btn_remove_selected": "Remove selected",
        "btn_clear_list": "Clear list",
        "frame_queue": "Queue",
        "col_type": "Type",
        "col_name": "Name",
        "col_path": "Path",
        "col_remove": "X",
        "frame_quality": "JPG quality",
        "frame_options": "Options",
        "opt_recursive": "Process subfolders and nested ZIP archives",
        "opt_conflict": "On name conflict:",
        "opt_verbose": "Verbose log",
        "conflict_rename": "Rename",
        "conflict_overwrite": "Overwrite",
        "conflict_skip": "Skip",
        "btn_convert": "Convert",
        "btn_cancel": "Cancel",
        "btn_open_output": "Open OUTPUT",
        "btn_clear_log": "Clear log",
        "frame_log": "Log",
        "status_ready": "Ready",
        "log_app_started": "Application started",
        "log_output_dir": "Output folder: {path}",
        "log_dnd_available": "Drag-and-drop available",
        "log_dnd_unavailable": "Drag-and-drop unavailable. Install 'tkinterdnd2'.",
        "log_dnd_init_error": "Failed to initialize drag-and-drop: {error}",
        "msg_busy": "Please wait for the current conversion to finish.",
        "dialog_select_folder": "Select a folder with PNG files or ZIP archives",
        "dialog_select_files": "Select PNG files or ZIP archives",
        "filetype_png_zip": "PNG/ZIP",
        "filetype_png": "PNG",
        "filetype_zip": "ZIP",
        "filetype_all": "All files",
        "kind_folder": "Folder",
        "kind_png": "PNG",
        "kind_zip": "ZIP",
        "log_add_failed": "Failed to add item: {error}",
        "log_added": "Added to queue: {count}",
        "log_duplicates": "Duplicates skipped: {count}",
        "log_unsupported_added": "Unsupported files skipped. Supported: folders, PNG files and ZIP archives.",
        "log_missing_paths": "Paths not found: {count}",
        "msg_select_rows": "Select rows to remove first.",
        "log_list_cleared": "Queue cleared: {count} items removed",
        "log_removed": "Removed from queue: {count}",
        "msg_queue_empty": "The queue is empty.",
        "log_another_job": "Another conversion is running. Please wait for it to finish.",
        "status_starting": "Starting...",
        "log_cancel_requested": "Cancellation requested",
        "msg_open_output_error": "Failed to open the OUTPUT folder:\n{error}",
        "status_processing": "Processing: {index}/{total}",
        "log_zip_read_error": "Failed to read ZIP: {name} — {error}",
        "log_zip_unsafe": "ZIP: skipped unsafe path {member} in {name}",
        "log_zip_member_error": "ZIP: failed to read member {member} in {name}: {error}",
        "log_zip_found": "ZIP: {name}, PNG files found: {count}, destination: {dest}",
        "log_zip_no_png": "No PNG files in ZIP: {name}",
        "log_folder_read_error": "Failed to read folder {path}: {error}",
        "log_file_process_error": "Failed to process file {path}: {error}",
        "log_conversion_start": "=== Conversion started ===",
        "log_quality": "JPG quality: {quality}",
        "log_sources_count": "Items in queue: {count}",
        "log_output_create_error": "Failed to create the OUTPUT folder: {error}",
        "status_output_create_error": "Failed to create the OUTPUT folder",
        "log_source_missing": "Source not found: {path}",
        "log_dest_create_error": "Failed to create destination folder {path}: {error}",
        "log_folder": "Folder: {src} -> {dest}",
        "log_folder_found": "Found in folder: PNG={png}, ZIP={zip}, PNG inside ZIP={zip_png}",
        "log_folder_no_png": "No PNG files or ZIP archives found in folder: {path}",
        "log_unsupported_skip": "Skipped unsupported file: {name}",
        "log_source_skip": "Skipped source: {path}",
        "log_source_error": "Failed to process source {path}: {error}",
        "log_direct_png": "PNG files in queue: {count}",
        "log_skipped_sources": "Sources skipped: {count}",
        "log_no_tasks": "No files to convert.",
        "status_no_tasks": "No tasks",
        "log_cancelled_by_user": "Conversion stopped by user.",
        "log_skipped_exists": "Skipped, already exists: {name}",
        "log_zip_open_error": "Failed to open ZIP: {name} — {error}",
        "log_warning": "Warning: {source} — {message}",
        "log_ok": "OK: {source} -> {target}",
        "log_error": "Error: {source} — {message}",
        "unknown_item": "unknown item",
        "summary_cancelled": "Cancelled: succeeded {success}, errors {errors}, skipped {skipped}, time {time:.1f} s",
        "summary_done": "Done: succeeded {success}, errors {errors}, skipped {skipped}, warnings {warnings}, time {time:.1f} s",
        "log_critical": "Critical error: {error}",
        "status_critical": "Critical error",
        "warn_animated": "animated PNG, only the first frame was saved",
    },
    "ru": {
        "app_title": "PNG → JPG конвертер",
        "language": "Язык",
        "frame_add": "Добавление",
        "dnd_hint": "Перетащите сюда папки, файлы PNG или ZIP",
        "dnd_unavailable_hint": "Drag-and-drop недоступен. Установите 'tkinterdnd2' или используйте кнопки ниже.",
        "btn_add_folder": "Добавить папку",
        "btn_add_files": "Добавить файлы / ZIP",
        "btn_remove_selected": "Удалить выбранные",
        "btn_clear_list": "Очистить список",
        "frame_queue": "Список загрузки",
        "col_type": "Тип",
        "col_name": "Имя",
        "col_path": "Путь",
        "col_remove": "X",
        "frame_quality": "Качество JPG",
        "frame_options": "Параметры",
        "opt_recursive": "Обрабатывать вложенные папки и ZIP внутри",
        "opt_conflict": "При совпадении имён:",
        "opt_verbose": "Подробный лог",
        "conflict_rename": "Переименовывать",
        "conflict_overwrite": "Перезаписывать",
        "conflict_skip": "Пропускать",
        "btn_convert": "Конвертация",
        "btn_cancel": "Отмена",
        "btn_open_output": "Открыть OUTPUT",
        "btn_clear_log": "Очистить лог",
        "frame_log": "Лог",
        "status_ready": "Готово",
        "log_app_started": "Приложение запущено",
        "log_output_dir": "Папка результатов: {path}",
        "log_dnd_available": "Drag-and-drop доступен",
        "log_dnd_unavailable": "Drag-and-drop недоступен. Установите 'tkinterdnd2'.",
        "log_dnd_init_error": "Не удалось инициализировать drag-and-drop: {error}",
        "msg_busy": "Дождитесь завершения текущей конвертации.",
        "dialog_select_folder": "Выберите папку с PNG или ZIP",
        "dialog_select_files": "Выберите PNG или ZIP",
        "filetype_png_zip": "PNG/ZIP",
        "filetype_png": "PNG",
        "filetype_zip": "ZIP",
        "filetype_all": "Все файлы",
        "kind_folder": "Папка",
        "kind_png": "PNG",
        "kind_zip": "ZIP",
        "log_add_failed": "Не удалось добавить элемент: {error}",
        "log_added": "Добавлено в список: {count}",
        "log_duplicates": "Дубликаты пропущены: {count}",
        "log_unsupported_added": "Неподдерживаемые файлы пропущены. Поддерживаются папки, PNG и ZIP.",
        "log_missing_paths": "Не найдены пути: {count}",
        "msg_select_rows": "Сначала выберите строки для удаления.",
        "log_list_cleared": "Список очищен: удалено элементов: {count}",
        "log_removed": "Удалено из списка: {count}",
        "msg_queue_empty": "Список загрузки пуст.",
        "log_another_job": "Идёт другая конвертация. Дождитесь завершения.",
        "status_starting": "Запуск...",
        "log_cancel_requested": "Запрошена отмена",
        "msg_open_output_error": "Не удалось открыть папку OUTPUT:\n{error}",
        "status_processing": "Обработка: {index}/{total}",
        "log_zip_read_error": "Ошибка чтения ZIP: {name} — {error}",
        "log_zip_unsafe": "ZIP: пропущен небезопасный путь {member} в {name}",
        "log_zip_member_error": "ZIP: ошибка при чтении элемента {member} в {name}: {error}",
        "log_zip_found": "ZIP: {name}, найдено PNG: {count}, назначение: {dest}",
        "log_zip_no_png": "В ZIP нет PNG: {name}",
        "log_folder_read_error": "Ошибка чтения папки {path}: {error}",
        "log_file_process_error": "Ошибка при обработке файла {path}: {error}",
        "log_conversion_start": "=== Старт конвертации ===",
        "log_quality": "Качество JPG: {quality}",
        "log_sources_count": "Объектов в списке: {count}",
        "log_output_create_error": "Не удалось создать папку OUTPUT: {error}",
        "status_output_create_error": "Ошибка создания папки OUTPUT",
        "log_source_missing": "Источник не найден: {path}",
        "log_dest_create_error": "Не удалось создать папку назначения {path}: {error}",
        "log_folder": "Папка: {src} -> {dest}",
        "log_folder_found": "В папке найдено: PNG={png}, ZIP={zip}, PNG внутри ZIP={zip_png}",
        "log_folder_no_png": "В папке не найдено PNG или ZIP: {path}",
        "log_unsupported_skip": "Пропущен неподдерживаемый файл: {name}",
        "log_source_skip": "Пропущен источник: {path}",
        "log_source_error": "Ошибка при обработке источника {path}: {error}",
        "log_direct_png": "PNG файлов в списке: {count}",
        "log_skipped_sources": "Пропущено источников: {count}",
        "log_no_tasks": "Нет задач для конвертации.",
        "status_no_tasks": "Нет задач",
        "log_cancelled_by_user": "Конвертация остановлена пользователем.",
        "log_skipped_exists": "Пропущено, уже существует: {name}",
        "log_zip_open_error": "Ошибка открытия ZIP: {name} — {error}",
        "log_warning": "Предупреждение: {source} — {message}",
        "log_ok": "OK: {source} -> {target}",
        "log_error": "Ошибка: {source} — {message}",
        "unknown_item": "неизвестный элемент",
        "summary_cancelled": "Отменено: успешно {success}, ошибок {errors}, пропущено {skipped}, время {time:.1f} с",
        "summary_done": "Готово: успешно {success}, ошибок {errors}, пропущено {skipped}, предупреждений {warnings}, время {time:.1f} с",
        "log_critical": "Критическая ошибка: {error}",
        "status_critical": "Критическая ошибка",
        "warn_animated": "анимированный PNG, сохранён только первый кадр",
    },
}

BaseWindow = TkinterDnD.Tk if DND_AVAILABLE else tk.Tk


def now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def sanitize_filename(name: str) -> str:
    name = name.replace("\0", "")
    name = "".join(ch for ch in name if ord(ch) >= 32)

    invalid_chars = '<>:"/\\|?*'
    for ch in invalid_chars:
        name = name.replace(ch, "_")

    name = name.strip(". ")
    if not name:
        return "folder"

    return name


def decode_zip_filename(info):
    """
    Пытается корректно прочитать имя файла внутри ZIP,
    в том числе кириллицу из старых архивов.
    """
    name = info.filename

    try:
        if info.flag_bits & 0x800:
            return name

        raw = name.encode("cp437")
    except Exception:
        return name

    for enc in ("cp866", "cp1251", "utf-8"):
        try:
            return raw.decode(enc)
        except Exception:
            pass

    return name


def safe_zip_rel(name: str):
    """
    Безопасно превращает внутренний путь ZIP в относительный путь для сохранения.
    """
    name = name.replace("\\", "/")
    p = Path(name)

    if p.is_absolute():
        return None

    parts = []
    for part in p.parts:
        if part == "..":
            return None

        if part in ("", ".", "/"):
            continue

        clean = sanitize_filename(part)
        if clean:
            parts.append(clean)

    if not parts:
        return None

    return Path(*parts)


def folder_output_name(src_dir: Path) -> str:
    name = src_dir.name or src_dir.resolve().name

    if not name and src_dir.drive:
        name = src_dir.drive.replace(":", "_")

    return sanitize_filename(name or "folder")


def resolve_conflict(path: Path, mode: str):
    if not path.exists():
        return path

    if mode == "overwrite":
        return path

    if mode == "skip":
        return None

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    index = 1

    while True:
        candidate = parent / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def iter_files(folder: Path, recursive: bool):
    if recursive:
        for root, dirs, files in os.walk(folder):
            try:
                root_path = Path(root).resolve()
                dirs[:] = [
                    d for d in dirs
                    if (root_path / d).resolve() != OUTPUT_DIR.resolve()
                ]
            except Exception:
                pass

            for name in files:
                yield Path(root) / name
    else:
        try:
            for item in folder.iterdir():
                if item.is_file():
                    yield item
        except OSError:
            return


def process_and_save_image(img: Image.Image, dst: Path, quality: int):
    warning = None

    if getattr(img, "is_animated", False) and getattr(img, "n_frames", 1) > 1:
        warning = "warn_animated"

    img.load()

    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        rgb = Image.new("RGB", rgba.size, (255, 255, 255))
        rgb.paste(rgba, mask=rgba.split()[3])
    else:
        rgb = img.convert("RGB")

    rgb.save(
        dst,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
    )

    return warning


def convert_image_file(src: Path, dst: Path, quality: int):
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(src) as img:
            warning = process_and_save_image(img, dst, quality)
            return True, warning

    except Exception as exc:
        return False, str(exc)


def convert_zip_member(zf: zipfile.ZipFile, member_name: str, dst: Path, quality: int):
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)

        data = zf.read(member_name)

        with Image.open(io.BytesIO(data)) as img:
            warning = process_and_save_image(img, dst, quality)
            return True, warning

    except Exception as exc:
        return False, str(exc)


class App(BaseWindow):
    def __init__(self):
        super().__init__()

        self.lang = "en"

        self.title(self._t("app_title"))
        self.geometry("1080x740")
        self.minsize(940, 640)

        self.log_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker = None

        self.quality_var = tk.IntVar(value=85)
        self.conflict_code = tk.StringVar(value=CONFLICT_CODES[0])
        self.conflict_display = tk.StringVar()
        self.verbose_var = tk.BooleanVar(value=False)
        self.recursive_var = tk.BooleanVar(value=True)

        self.status_text = tk.StringVar(value=self._t("status_ready"))

        # Load queue
        self.sources = {}       # iid -> Path
        self.item_keys = {}     # iid -> unique key
        self.item_kinds = {}    # iid -> translation key
        self.key_to_iid = {}    # unique key -> iid

        self._ui_font = None
        self._drop_font = None
        self._text_widgets = []

        self._setup_fonts()
        self._build_ui()
        self._register_dnd()
        self._apply_language()

        self.after(100, self._poll_queue)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._update_convert_btn()

        self._log(self._t("log_app_started"))
        self._log(self._t("log_output_dir", path=OUTPUT_DIR))

        if DND_AVAILABLE:
            self._log(self._t("log_dnd_available"))
        else:
            self._log(self._t("log_dnd_unavailable"), "WARN")

    def _setup_fonts(self):
        try:
            try:
                families = set(tkfont.families(self))
            except Exception:
                families = set()

            preferred = [
                "Segoe UI",
                "Calibri",
                "Verdana",
                "Arial",
                "DejaVu Sans",
                "Helvetica",
            ]

            chosen = next((f for f in preferred if f in families), None)

            if not chosen:
                return

            self._ui_font = (chosen, 10)
            self._drop_font = (chosen, 12, "bold")

            for font_name in (
                "TkDefaultFont",
                "TkTextFont",
                "TkMenuFont",
                "TkHeadingFont",
                "TkTooltipFont",
                "TkFixedFont",
            ):
                try:
                    tkfont.nametofont(font_name).configure(family=chosen, size=10)
                except Exception:
                    pass

            style = ttk.Style(self)
            style.configure(".", font=(chosen, 10))
            style.configure("TLabel", font=(chosen, 10))
            style.configure("TButton", font=(chosen, 10))
            style.configure("TCheckbutton", font=(chosen, 10))
            style.configure("TRadiobutton", font=(chosen, 10))
            style.configure("Treeview", font=(chosen, 10), rowheight=24)
            style.configure("Treeview.Heading", font=(chosen, 9, "bold"))

        except Exception:
            pass

    def _t(self, key, **kwargs):
        lang = self.lang if self.lang in TRANSLATIONS else "en"
        template = TRANSLATIONS[lang].get(key, TRANSLATIONS["en"].get(key, key))
        if kwargs:
            try:
                return template.format(**kwargs)
            except Exception:
                return template
        return template

    def _bind_text(self, widget, key):
        self._text_widgets.append((widget, key))
        try:
            widget.configure(text=self._t(key))
        except Exception:
            pass

    def _conflict_values(self):
        return [self._t("conflict_" + code) for code in CONFLICT_CODES]

    def _refresh_conflict_combo(self):
        self.conflict_combo.configure(values=self._conflict_values())
        self.conflict_display.set(self._t("conflict_" + self.conflict_code.get()))

    def _on_conflict_change(self, event=None):
        display = self.conflict_display.get()
        for code in CONFLICT_CODES:
            if self._t("conflict_" + code) == display:
                self.conflict_code.set(code)
                break

    def toggle_language(self):
        self.lang = "ru" if self.lang == "en" else "en"
        self._apply_language()

    def _apply_language(self):
        for widget, key in self._text_widgets:
            try:
                widget.configure(text=self._t(key))
            except Exception:
                pass

        self.title(self._t("app_title"))

        self.drop_label.configure(
            text=self._t("dnd_hint")
            if DND_AVAILABLE
            else self._t("dnd_unavailable_hint")
        )

        self.lang_btn.configure(text="Русский" if self.lang == "en" else "English")

        self.tree.heading("type", text=self._t("col_type"))
        self.tree.heading("name", text=self._t("col_name"))
        self.tree.heading("path", text=self._t("col_path"))
        self.tree.heading("remove", text=self._t("col_remove"))

        for iid, kind_key in self.item_kinds.items():
            try:
                self.tree.set(iid, "type", self._t(kind_key))
            except Exception:
                pass

        self._refresh_conflict_combo()

        if not self.is_busy():
            ready_values = {TRANSLATIONS[code]["status_ready"] for code in LANGUAGES}
            if self.status_text.get() in ready_values:
                self.status_text.set(self._t("status_ready"))

    def _translate_warning(self, message):
        if message == "warn_animated":
            return self._t("warn_animated")
        return message

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=2)
        main.rowconfigure(7, weight=3)

        # Top bar: title and language switch
        header = ttk.Frame(main)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        header.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(header, text="")
        self.title_label.grid(row=0, column=0, sticky="w")
        if self._drop_font:
            self.title_label.configure(font=self._drop_font)

        self.lang_label = ttk.Label(header, text="")
        self.lang_label.grid(row=0, column=1, padx=(8, 4))

        self.lang_btn = ttk.Button(
            header,
            text="",
            command=self.toggle_language,
            width=10,
        )
        self.lang_btn.grid(row=0, column=2)

        self._bind_text(self.title_label, "app_title")
        self._bind_text(self.lang_label, "language")

        # Add block
        self.add_frame = ttk.LabelFrame(main, text="", padding=8)
        self.add_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.add_frame.columnconfigure(0, weight=1)
        self._bind_text(self.add_frame, "frame_add")

        self.drop_label = ttk.Label(self.add_frame, text="", anchor="center")
        self.drop_label.grid(row=0, column=0, sticky="ew", ipady=6)

        if self._drop_font:
            self.drop_label.configure(font=self._drop_font)

        add_buttons = ttk.Frame(self.add_frame)
        add_buttons.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        self.add_folder_btn = ttk.Button(
            add_buttons,
            text="",
            command=self.select_folder,
        )
        self.add_folder_btn.pack(side="left", padx=(0, 8))
        self._bind_text(self.add_folder_btn, "btn_add_folder")

        self.add_files_btn = ttk.Button(
            add_buttons,
            text="",
            command=self.select_files,
        )
        self.add_files_btn.pack(side="left", padx=(0, 8))
        self._bind_text(self.add_files_btn, "btn_add_files")

        self.remove_btn = ttk.Button(
            add_buttons,
            text="",
            command=self.remove_selected,
        )
        self.remove_btn.pack(side="left", padx=(0, 8))
        self._bind_text(self.remove_btn, "btn_remove_selected")

        self.clear_list_btn = ttk.Button(
            add_buttons,
            text="",
            command=self.clear_list,
        )
        self.clear_list_btn.pack(side="left")
        self._bind_text(self.clear_list_btn, "btn_clear_list")

        # Queue list
        self.list_frame = ttk.LabelFrame(main, text="", padding=4)
        self.list_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        self.list_frame.columnconfigure(0, weight=1)
        self.list_frame.rowconfigure(0, weight=1)
        self._bind_text(self.list_frame, "frame_queue")

        self.tree = ttk.Treeview(
            self.list_frame,
            columns=("type", "name", "path", "remove"),
            show="headings",
            selectmode="extended",
        )

        self.tree.heading("type", text="")
        self.tree.heading("name", text="")
        self.tree.heading("path", text="")
        self.tree.heading("remove", text="")

        self.tree.column("type", width=80, anchor="center", stretch=False)
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("path", width=560, anchor="w")
        self.tree.column("remove", width=44, anchor="center", stretch=False)

        tree_scroll = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)
        self.tree.bind("<Delete>", lambda event: self.remove_selected())

        # Quality
        self.quality_frame = ttk.LabelFrame(main, text="", padding=8)
        self.quality_frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        self.quality_frame.columnconfigure(1, weight=1)
        self._bind_text(self.quality_frame, "frame_quality")

        ttk.Label(self.quality_frame, text="1").grid(row=0, column=0, sticky="w")

        self.quality_scale = ttk.Scale(
            self.quality_frame,
            from_=1,
            to=100,
            orient="horizontal",
            variable=self.quality_var,
            command=self._quality_changed,
        )
        self.quality_scale.grid(row=0, column=1, sticky="ew", padx=8)

        ttk.Label(self.quality_frame, text="100").grid(row=0, column=2, sticky="e")

        self.quality_label = ttk.Label(self.quality_frame, text="85", width=4)
        self.quality_label.grid(row=0, column=3, padx=(8, 0))

        # Options
        self.options_frame = ttk.LabelFrame(main, text="", padding=8)
        self.options_frame.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        self.options_frame.columnconfigure(1, weight=1)
        self._bind_text(self.options_frame, "frame_options")

        self.recursive_check = ttk.Checkbutton(
            self.options_frame,
            text="",
            variable=self.recursive_var,
        )
        self.recursive_check.grid(row=0, column=0, columnspan=3, sticky="w")
        self._bind_text(self.recursive_check, "opt_recursive")

        self.conflict_label = ttk.Label(self.options_frame, text="")
        self.conflict_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(6, 0),
        )
        self._bind_text(self.conflict_label, "opt_conflict")

        self.conflict_combo = ttk.Combobox(
            self.options_frame,
            textvariable=self.conflict_display,
            values=[],
            state="readonly",
            width=18,
        )
        self.conflict_combo.grid(
            row=1,
            column=1,
            sticky="w",
            padx=(8, 0),
            pady=(6, 0),
        )
        self.conflict_combo.bind("<<ComboboxSelected>>", self._on_conflict_change)

        self.verbose_check = ttk.Checkbutton(
            self.options_frame,
            text="",
            variable=self.verbose_var,
        )
        self.verbose_check.grid(
            row=1,
            column=2,
            sticky="w",
            padx=(16, 0),
            pady=(6, 0),
        )
        self._bind_text(self.verbose_check, "opt_verbose")

        # Action buttons
        action_frame = ttk.Frame(main)
        action_frame.grid(row=5, column=0, sticky="ew", pady=(0, 8))

        self.convert_btn = ttk.Button(
            action_frame,
            text="",
            command=self.start_conversion,
            state="disabled",
        )
        self.convert_btn.pack(side="left", padx=(0, 8))
        self._bind_text(self.convert_btn, "btn_convert")

        self.cancel_btn = ttk.Button(
            action_frame,
            text="",
            command=self.cancel_conversion,
            state="disabled",
        )
        self.cancel_btn.pack(side="left", padx=(0, 8))
        self._bind_text(self.cancel_btn, "btn_cancel")

        self.open_btn = ttk.Button(
            action_frame,
            text="",
            command=self.open_output,
        )
        self.open_btn.pack(side="left", padx=(0, 8))
        self._bind_text(self.open_btn, "btn_open_output")

        self.clear_log_btn = ttk.Button(
            action_frame,
            text="",
            command=self.clear_log,
        )
        self.clear_log_btn.pack(side="left")
        self._bind_text(self.clear_log_btn, "btn_clear_log")

        # Progress
        progress_frame = ttk.Frame(main)
        progress_frame.grid(row=6, column=0, sticky="ew", pady=(0, 8))
        progress_frame.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.grid(row=0, column=0, sticky="ew")

        ttk.Label(progress_frame, textvariable=self.status_text).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(4, 0),
        )

        # Log
        self.log_frame = ttk.LabelFrame(main, text="", padding=4)
        self.log_frame.grid(row=7, column=0, sticky="nsew")
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        self._bind_text(self.log_frame, "frame_log")

        self.log_text = ScrolledText(
            self.log_frame,
            height=10,
            wrap="word",
            state="disabled",
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")

        if self._ui_font:
            self.log_text.configure(font=self._ui_font)

    def _register_dnd(self):
        if not DND_AVAILABLE:
            return

        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_drop)
        except Exception as exc:
            self._log(self._t("log_dnd_init_error", error=exc), "WARN")

    def _quality_changed(self, value):
        try:
            self.quality_label.config(text=str(int(float(value))))
        except Exception:
            pass

    def _path_key(self, path: Path) -> str:
        try:
            resolved = path.resolve()
        except Exception:
            resolved = path

        return os.path.normcase(str(resolved))

    def select_folder(self):
        if self.is_busy():
            self._log(self._t("msg_busy"), "WARN")
            return

        path = filedialog.askdirectory(title=self._t("dialog_select_folder"))
        if not path:
            return

        self.add_sources([Path(path)])

    def select_files(self):
        if self.is_busy():
            self._log(self._t("msg_busy"), "WARN")
            return

        files = filedialog.askopenfilenames(
            title=self._t("dialog_select_files"),
            filetypes=[
                (self._t("filetype_png_zip"), "*.png *.zip *.PNG *.ZIP"),
                (self._t("filetype_png"), "*.png *.PNG"),
                (self._t("filetype_zip"), "*.zip *.ZIP"),
                (self._t("filetype_all"), "*.*"),
            ],
        )

        if not files:
            return

        self.add_sources([Path(f) for f in files])

    def _on_drop(self, event):
        if self.is_busy():
            self._log(self._t("msg_busy"), "WARN")
            return

        try:
            raw_items = self.tk.splitlist(event.data)
        except Exception:
            raw_items = tuple(event.data.split())

        sources = []

        for item in raw_items:
            item = str(item).strip()
            if not item:
                continue

            if item.startswith("file://"):
                parsed = urlparse(item)
                item = unquote(parsed.path)

                if os.name == "nt" and item.startswith("/"):
                    item = item[1:]

            sources.append(Path(item))

        if sources:
            self.add_sources(sources)

    def add_sources(self, paths):
        if self.is_busy():
            self._log(self._t("msg_busy"), "WARN")
            return

        added = 0
        duplicates = 0
        unsupported = 0
        missing = 0

        for path in paths:
            try:
                if not path.exists():
                    missing += 1
                    continue

                key = self._path_key(path)

                if key in self.key_to_iid:
                    duplicates += 1
                    continue

                if path.is_dir():
                    kind_key = "kind_folder"
                elif path.is_file():
                    suffix = path.suffix.lower()

                    if suffix == PNG_EXT:
                        kind_key = "kind_png"
                    elif suffix == ZIP_EXT:
                        kind_key = "kind_zip"
                    else:
                        unsupported += 1
                        continue
                else:
                    unsupported += 1
                    continue

                iid = self.tree.insert(
                    "",
                    "end",
                    values=(self._t(kind_key), path.name, str(path), "X"),
                )

                self.sources[iid] = path
                self.item_keys[iid] = key
                self.item_kinds[iid] = kind_key
                self.key_to_iid[key] = iid

                added += 1

            except Exception as exc:
                self._log(self._t("log_add_failed", error=exc), "ERROR")

        if added:
            self._log(self._t("log_added", count=added))

        if duplicates:
            self._log(self._t("log_duplicates", count=duplicates), "WARN")

        if unsupported:
            self._log(self._t("log_unsupported_added"), "WARN")

        if missing:
            self._log(self._t("log_missing_paths", count=missing), "WARN")

        self._update_convert_btn()

    def remove_selected(self):
        if self.is_busy():
            self._log(self._t("msg_busy"), "WARN")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(self._t("app_title"), self._t("msg_select_rows"))
            return

        self._remove_items(selected)

    def clear_list(self):
        if self.is_busy():
            self._log(self._t("msg_busy"), "WARN")
            return

        if not self.sources:
            return

        count = len(self.sources)

        self.tree.delete(*self.tree.get_children())
        self.sources.clear()
        self.item_keys.clear()
        self.item_kinds.clear()
        self.key_to_iid.clear()

        self._log(self._t("log_list_cleared", count=count))
        self._update_convert_btn()

    def _on_tree_click(self, event):
        if self.is_busy():
            return

        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        # remove column is the 4th data column: #4
        if row and column == "#4":
            self._remove_items([row])

    def _remove_items(self, iids):
        if not iids:
            return

        count = 0

        for iid in iids:
            if iid not in self.sources:
                continue

            key = self.item_keys.pop(iid, None)
            self.sources.pop(iid, None)
            self.item_kinds.pop(iid, None)

            if key and self.key_to_iid.get(key) == iid:
                self.key_to_iid.pop(key, None)

            try:
                self.tree.delete(iid)
            except Exception:
                pass

            count += 1

        if count:
            self._log(self._t("log_removed", count=count))

        self._update_convert_btn()

    def start_conversion(self):
        if self.is_busy():
            return

        if not self.sources:
            messagebox.showwarning(self._t("app_title"), self._t("msg_queue_empty"))
            return

        sources = list(self.sources.values())
        self._start_job(sources)

    def _start_job(self, sources):
        if self.is_busy():
            self._log(self._t("log_another_job"), "WARN")
            return

        if not sources:
            return

        unique_sources = []
        seen = set()

        for src in sources:
            key = self._path_key(src)

            if key not in seen:
                seen.add(key)
                unique_sources.append(src)

        try:
            quality = int(self.quality_var.get())
        except Exception:
            quality = 85

        quality = max(1, min(100, quality))

        self.cancel_event.clear()
        self._set_ui_busy(True)

        self.progress.config(maximum=0, value=0)
        self.status_text.set(self._t("status_starting"))

        self.worker = threading.Thread(
            target=self._run_job,
            args=(
                unique_sources,
                quality,
                self.conflict_code.get(),
                self.verbose_var.get(),
                self.recursive_var.get(),
            ),
            daemon=True,
        )

        self.worker.start()

    def cancel_conversion(self):
        if self.is_busy():
            self.cancel_event.set()
            self._log(self._t("log_cancel_requested"), "WARN")

    def is_busy(self):
        return self.worker is not None and self.worker.is_alive()

    def _set_ui_busy(self, busy: bool):
        if busy:
            self.add_folder_btn.config(state="disabled")
            self.add_files_btn.config(state="disabled")
            self.remove_btn.config(state="disabled")
            self.clear_list_btn.config(state="disabled")
            self.convert_btn.config(state="disabled")
            self.cancel_btn.config(state="normal")
            self.recursive_check.config(state="disabled")
            self.conflict_combo.config(state="disabled")
            self.verbose_check.config(state="disabled")
        else:
            self.add_folder_btn.config(state="normal")
            self.add_files_btn.config(state="normal")
            self.remove_btn.config(state="normal")
            self.clear_list_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")
            self.recursive_check.config(state="normal")
            self.conflict_combo.config(state="readonly")
            self.verbose_check.config(state="normal")
            self._update_convert_btn()

    def _update_convert_btn(self):
        if self.is_busy():
            self.convert_btn.config(state="disabled")
            return

        if self.sources:
            self.convert_btn.config(state="normal")
        else:
            self.convert_btn.config(state="disabled")

    def open_output(self):
        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            if sys.platform == "win32":
                os.startfile(OUTPUT_DIR)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(OUTPUT_DIR)])
            else:
                subprocess.Popen(["xdg-open", str(OUTPUT_DIR)])

        except Exception as exc:
            messagebox.showerror(
                self._t("app_title"),
                self._t("msg_open_output_error", error=exc),
            )

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")

    def _log(self, message: str, level: str = "INFO"):
        self.log_queue.put(("log", f"[{now()}] {level}: {message}"))

    def _append_log(self, text: str):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def _poll_queue(self):
        try:
            while True:
                item = self.log_queue.get_nowait()
                kind = item[0]

                if kind == "log":
                    self._append_log(item[1])
                elif kind == "progress":
                    self.progress["value"] = item[1]
                elif kind == "progress_max":
                    self.progress["maximum"] = item[1]
                    self.progress["value"] = 0
                elif kind == "status":
                    self.status_text.set(item[1])
                elif kind == "finished":
                    self._finish()

        except queue.Empty:
            pass

        self.after(100, self._poll_queue)

    def _finish(self):
        if self.is_busy():
            self.after(100, self._finish)
            return

        self._set_ui_busy(False)

    def _on_close(self):
        if self.is_busy():
            self.cancel_event.set()

        self.destroy()

    def _update_progress(self, index: int, total: int):
        self.log_queue.put(("progress", index))
        self.log_queue.put(("status", self._t("status_processing", index=index, total=total)))

    def _reserve_output_base(self, candidate: Path, used_set: set) -> Path:
        key = str(candidate).lower()

        if key not in used_set:
            used_set.add(key)
            return candidate

        index = 1

        while True:
            new_candidate = candidate.parent / f"{candidate.name}_{index}"
            key = str(new_candidate).lower()

            if key not in used_set:
                used_set.add(key)
                return new_candidate

            index += 1

    def _collect_zip_tasks(self, zip_path: Path, out_base: Path):
        tasks = []
        count = 0

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                members = zf.infolist()
        except Exception as exc:
            self._log(
                self._t("log_zip_read_error", name=zip_path.name, error=exc),
                "ERROR",
            )
            return tasks, count

        for info in members:
            if self.cancel_event.is_set():
                break

            try:
                if info.is_dir():
                    continue

                decoded_name = decode_zip_filename(info)

                if not decoded_name.lower().endswith(PNG_EXT):
                    continue

                rel = safe_zip_rel(decoded_name)

                if rel is None:
                    self._log(
                        self._t(
                            "log_zip_unsafe",
                            member=info.filename,
                            name=zip_path.name,
                        ),
                        "WARN",
                    )
                    continue

                dst = out_base / rel.with_suffix(".jpg")
                tasks.append(("zip", zip_path, info.filename, dst))
                count += 1

            except Exception as exc:
                self._log(
                    self._t(
                        "log_zip_member_error",
                        member=info.filename,
                        name=zip_path.name,
                        error=exc,
                    ),
                    "ERROR",
                )

        if count:
            self._log(
                self._t(
                    "log_zip_found",
                    name=zip_path.name,
                    count=count,
                    dest=out_base,
                )
            )
        else:
            self._log(self._t("log_zip_no_png", name=zip_path.name), "WARN")

        return tasks, count

    def _collect_folder_tasks(self, src_dir: Path, recursive: bool, out_base: Path):
        tasks = []
        png_count = 0
        zip_count = 0
        zip_member_count = 0

        try:
            files = sorted(iter_files(src_dir, recursive), key=lambda p: str(p).lower())
        except Exception as exc:
            self._log(
                self._t("log_folder_read_error", path=src_dir, error=exc),
                "ERROR",
            )
            return tasks, png_count, zip_count, zip_member_count

        for file_path in files:
            if self.cancel_event.is_set():
                break

            try:
                suffix = file_path.suffix.lower()

                if recursive:
                    rel = file_path.relative_to(src_dir)
                    rel_dir = rel.parent
                else:
                    rel = Path(file_path.name)
                    rel_dir = Path(".")

                if suffix == PNG_EXT:
                    if recursive:
                        dst_rel = rel.with_suffix(".jpg")
                    else:
                        dst_rel = Path(file_path.stem + ".jpg")

                    tasks.append(("file", file_path, out_base / dst_rel))
                    png_count += 1

                elif suffix == ZIP_EXT:
                    zip_dir_name = sanitize_filename(file_path.stem or file_path.name)

                    if rel_dir == Path("."):
                        zip_out_base = out_base / zip_dir_name
                    else:
                        zip_out_base = out_base / rel_dir / zip_dir_name

                    zip_tasks, zip_pngs = self._collect_zip_tasks(file_path, zip_out_base)

                    if zip_tasks:
                        tasks.extend(zip_tasks)
                        zip_count += 1
                        zip_member_count += zip_pngs

            except Exception as exc:
                self._log(
                    self._t("log_file_process_error", path=file_path, error=exc),
                    "ERROR",
                )

        return tasks, png_count, zip_count, zip_member_count

    def _run_job(
        self,
        sources,
        quality: int,
        conflict_mode: str,
        verbose: bool,
        recursive: bool,
    ):
        start_time = time.time()
        current_zip = None
        current_zip_path = None

        try:
            self._log(self._t("log_conversion_start"))
            self._log(self._t("log_quality", quality=quality))
            self._log(self._t("log_sources_count", count=len(sources)))

            try:
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                self._log(self._t("log_output_create_error", error=exc), "ERROR")
                self.log_queue.put(("status", self._t("status_output_create_error")))
                return

            tasks = []
            direct_png_count = 0
            skipped_sources = 0
            used_output_bases = set()

            for src in sources:
                if self.cancel_event.is_set():
                    break

                try:
                    if not src.exists():
                        self._log(self._t("log_source_missing", path=src), "WARN")
                        skipped_sources += 1
                        continue

                    if src.is_dir():
                        out_base_candidate = OUTPUT_DIR / folder_output_name(src)
                        out_base = self._reserve_output_base(out_base_candidate, used_output_bases)

                        folder_tasks, png_count, zip_count, zip_member_count = (
                            self._collect_folder_tasks(src, recursive, out_base)
                        )

                        if folder_tasks:
                            try:
                                out_base.mkdir(parents=True, exist_ok=True)
                            except Exception as exc:
                                self._log(
                                    self._t(
                                        "log_dest_create_error",
                                        path=out_base,
                                        error=exc,
                                    ),
                                    "ERROR",
                                )
                                skipped_sources += 1
                                continue

                            tasks.extend(folder_tasks)
                            self._log(self._t("log_folder", src=src, dest=out_base))
                            self._log(
                                self._t(
                                    "log_folder_found",
                                    png=png_count,
                                    zip=zip_count,
                                    zip_png=zip_member_count,
                                )
                            )
                        else:
                            self._log(self._t("log_folder_no_png", path=src), "WARN")

                    elif src.is_file():
                        suffix = src.suffix.lower()

                        if suffix == PNG_EXT:
                            direct_png_count += 1
                            tasks.append(("file", src, OUTPUT_DIR / (src.stem + ".jpg")))

                        elif suffix == ZIP_EXT:
                            out_base_candidate = OUTPUT_DIR / sanitize_filename(src.stem or src.name)
                            out_base = self._reserve_output_base(out_base_candidate, used_output_bases)

                            zip_tasks, _ = self._collect_zip_tasks(src, out_base)

                            if zip_tasks:
                                tasks.extend(zip_tasks)

                        else:
                            self._log(
                                self._t("log_unsupported_skip", name=src.name),
                                "WARN",
                            )
                            skipped_sources += 1

                    else:
                        self._log(self._t("log_source_skip", path=src), "WARN")
                        skipped_sources += 1

                except Exception as exc:
                    self._log(
                        self._t("log_source_error", path=src, error=exc),
                        "ERROR",
                    )
                    skipped_sources += 1

            if direct_png_count:
                self._log(self._t("log_direct_png", count=direct_png_count))

            if skipped_sources:
                self._log(self._t("log_skipped_sources", count=skipped_sources), "WARN")

            if not tasks:
                self._log(self._t("log_no_tasks"), "WARN")
                self.log_queue.put(("status", self._t("status_no_tasks")))
                return

            self.log_queue.put(("progress_max", len(tasks)))
            self.log_queue.put(("status", self._t("status_processing", index=0, total=len(tasks))))

            success = 0
            errors = 0
            skipped = 0
            warnings = 0
            failed_zips = set()

            for index, task in enumerate(tasks, start=1):
                if self.cancel_event.is_set():
                    self._log(self._t("log_cancelled_by_user"), "WARN")
                    break

                source_name = ""
                target = None

                try:
                    kind = task[0]

                    if kind == "file":
                        _, src, dst = task
                        source_name = src.name

                        if current_zip is not None:
                            try:
                                current_zip.close()
                            except Exception:
                                pass
                            current_zip = None
                            current_zip_path = None

                        target = resolve_conflict(dst, conflict_mode)

                        if target is None:
                            skipped += 1
                            if verbose:
                                self._log(
                                    self._t("log_skipped_exists", name=dst.name),
                                    "WARN",
                                )
                            self._update_progress(index, len(tasks))
                            continue

                        ok, message = convert_image_file(src, target, quality)

                    elif kind == "zip":
                        _, zip_path, member_name, dst = task
                        source_name = f"{zip_path.name}::{member_name}"

                        if zip_path in failed_zips:
                            errors += 1
                            self._update_progress(index, len(tasks))
                            continue

                        if current_zip_path != zip_path:
                            if current_zip is not None:
                                try:
                                    current_zip.close()
                                except Exception:
                                    pass
                                current_zip = None
                                current_zip_path = None

                            try:
                                current_zip = zipfile.ZipFile(zip_path, "r")
                                current_zip_path = zip_path
                            except Exception as exc:
                                failed_zips.add(zip_path)
                                self._log(
                                    self._t(
                                        "log_zip_open_error",
                                        name=zip_path.name,
                                        error=exc,
                                    ),
                                    "ERROR",
                                )
                                errors += 1
                                self._update_progress(index, len(tasks))
                                continue

                        target = resolve_conflict(dst, conflict_mode)

                        if target is None:
                            skipped += 1
                            if verbose:
                                self._log(
                                    self._t("log_skipped_exists", name=dst.name),
                                    "WARN",
                                )
                            self._update_progress(index, len(tasks))
                            continue

                        ok, message = convert_zip_member(current_zip, member_name, target, quality)

                    else:
                        skipped += 1
                        self._update_progress(index, len(tasks))
                        continue

                    if ok:
                        success += 1

                        if message:
                            warnings += 1
                            self._log(
                                self._t(
                                    "log_warning",
                                    source=source_name,
                                    message=self._translate_warning(message),
                                ),
                                "WARN",
                            )

                        if verbose:
                            self._log(
                                self._t("log_ok", source=source_name, target=target.name)
                            )

                    else:
                        errors += 1
                        self._log(
                            self._t("log_error", source=source_name, message=message),
                            "ERROR",
                        )

                except Exception as exc:
                    errors += 1
                    self._log(
                        self._t(
                            "log_error",
                            source=source_name or self._t("unknown_item"),
                            message=exc,
                        ),
                        "ERROR",
                    )

                self._update_progress(index, len(tasks))

            duration = time.time() - start_time

            if self.cancel_event.is_set():
                summary = self._t(
                    "summary_cancelled",
                    success=success,
                    errors=errors,
                    skipped=skipped,
                    time=duration,
                )
            else:
                summary = self._t(
                    "summary_done",
                    success=success,
                    errors=errors,
                    skipped=skipped,
                    warnings=warnings,
                    time=duration,
                )

            self._log(summary)
            self.log_queue.put(("status", summary))

        except Exception as exc:
            self._log(self._t("log_critical", error=exc), "ERROR")
            self.log_queue.put(("status", self._t("status_critical")))

        finally:
            if current_zip is not None:
                try:
                    current_zip.close()
                except Exception:
                    pass

            self.log_queue.put(("finished",))


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()