# PNG → JPG Converter

**English** | [Русский](README.ru.md)

A small Windows desktop application that converts PNG images to JPG. It accepts single files, whole folders and ZIP archives, supports drag & drop, and keeps the original folder structure in the output.

The interface is available in **English** and **Russian** — switch languages with one click.

## Features

- Convert individual PNG files, entire folders, or ZIP archives
- Drag & drop files, folders and archives onto the window
- Add several sources at once and remove individual queue entries (click the `X` column)
- Optional recursive processing of subfolders and ZIP archives inside folders
- Output preserves the original directory structure and file names
- Transparent areas are composited over a white background
- Adjustable JPEG quality (1–100, default 85)
- Name conflict handling: **Rename**, **Overwrite** or **Skip**
- Live progress bar, status line and log (optional verbose mode)
- English / Russian interface with an instant language switch
- Single-file Windows build (~18 MB) produced with PyInstaller

## Download

Download `PNG2JPG.exe` from the [Releases](https://github.com/burning-indica/converter-PNG-to-JPG/releases) page and run it — no installation required.

## Requirements

- Windows 10/11 (the source also runs on other platforms supported by Tkinter)
- Python 3.9+ (developed and tested with Python 3.14)
- [Pillow](https://pypi.org/project/Pillow/)
- [tkinterdnd2](https://pypi.org/project/tkinterdnd2/) (drag & drop; the app still works without it)
- PyInstaller — only for building the `.exe`

## Quick start (from source)

```bat
python -m pip install -r requirements.txt
python png_to_jpg.py
```

Or double-click `start.bat`: it locates Python, checks `tkinter`, and offers to install the missing dependencies.

## Usage

1. Add sources in any of these ways:
   - drag & drop files, folders or ZIP archives onto the window;
   - **Add folder** — pick a folder to scan;
   - **Add files / ZIP** — pick one or more PNG files or ZIP archives.
2. Set the JPG quality with the slider.
3. Optionally enable **Process subfolders and nested ZIP archives**, choose the conflict mode, and enable the **Verbose log**.
4. Click **Convert**.
5. Results are written to the `OUTPUT` folder next to the application. Use **Open OUTPUT** to open it.

The language button in the top-right corner switches between English and Russian immediately, without restarting the app.

### Output structure

Each source keeps its own name and directory layout:

```text
Queue item                         OUTPUT
---------------------------------  ---------------------------------------------
photos\                            OUTPUT\photos\...
  a.png                            a.jpg
  sub\b.png                        sub\b.jpg
archive.zip (a.png, sub\b.png)     OUTPUT\archive\a.jpg
                                   OUTPUT\archive\sub\b.jpg
```

A folder is scanned recursively (when enabled) and recreated under `OUTPUT` with the same name. Each ZIP archive is unpacked into a subfolder named after the archive. If several sources would produce the same output folder name, a numeric suffix (`_1`, `_2`, ...) is appended.

## Notes and limitations

- Input formats: **PNG** files and **ZIP** archives containing PNG files. Other files are ignored.
- JPEG has no alpha channel: transparent pixels are blended with white.
- Animated PNG: only the first frame is converted; a warning is written to the log.
- Output files keep their original names with the extension changed to `.jpg`.
- ZIP entries with unsafe paths (absolute paths or `..`) are skipped.

## Build the Windows executable

```bat
python -m pip install pyinstaller
pyinstaller --noconfirm PNG2JPG.spec
```

The result is a single file, `dist\PNG2JPG.exe` (about 18 MB). It needs no installation and no Python on the target machine.

The spec excludes modules the app never uses (`numpy`, `ssl`, `email`, `unittest`, …). Without those exclusions PyInstaller bundles numpy and OpenSSL pulled in by Pillow, and the build grows to about 71 MB. A one-file build unpacks itself into a temporary folder on launch, so the first window appears after a second or two.

`upx=True` stays in the spec: if `upx.exe` is on `PATH`, PyInstaller will use it. Do not expect much from UPX here — a one-file build is already compressed with zlib — and compressed executables are more likely to trigger antivirus heuristics.

## Project structure

```text
png_to_jpg.py      application (Tkinter GUI, conversion and archive logic)
PNG2JPG.spec       PyInstaller build configuration
start.bat          Windows launcher for running from source
requirements.txt   runtime dependencies
README.md          this file (English)
README.ru.md       Russian translation
dist/PNG2JPG.exe   single-file Windows build (created by PyInstaller)
OUTPUT/            conversion results (created at runtime)
```

## Translations

All user-facing strings are stored in the `TRANSLATIONS` dictionary at the top of `png_to_jpg.py`. Each language uses the same set of keys. To add another language, add a dictionary with the same keys, append its code to `LANGUAGES`, and extend the language switch logic.
