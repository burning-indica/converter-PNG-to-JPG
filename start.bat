@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title PNG to JPG Converter

if not exist "%~dp0png_to_jpg.py" (
    echo [ERROR] File png_to_jpg.py not found next to this BAT file.
    pause
    exit /b 1
)

set "PYTHON_CMD="

where py >nul 2>nul
if !errorlevel! equ 0 (
    py -3 -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if !errorlevel! equ 0 (
        python -c "import sys" >nul 2>nul
        if !errorlevel! equ 0 set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo [ERROR] Python not found. Install Python 3 and add it to PATH.
    pause
    exit /b 1
)

!PYTHON_CMD! -c "import tkinter" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] tkinter not found. Reinstall Python with tcl/tk option.
    pause
    exit /b 1
)

!PYTHON_CMD! -c "import PIL, tkinterdnd2" >nul 2>nul
if errorlevel 1 (
    echo Some dependencies are missing.
    choice /c 12 /n /m "Install dependencies? 1 - install, 2 - exit: "

    if errorlevel 2 (
        echo Exit without installation.
        exit /b 0
    )

    echo Installing Pillow and tkinterdnd2...
    !PYTHON_CMD! -m pip install --upgrade pillow tkinterdnd2

    if errorlevel 1 (
        echo Retry with --user...
        !PYTHON_CMD! -m pip install --upgrade --user pillow tkinterdnd2
    )
)

!PYTHON_CMD! -c "import PIL" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Cannot import Pillow after installation.
    pause
    exit /b 1
)

!PYTHON_CMD! -c "import tkinterdnd2" >nul 2>nul
if errorlevel 1 (
    echo Warning: tkinterdnd2 is not available. Drag-and-drop will be disabled.
)

start "" !PYTHON_CMD! "%~dp0png_to_jpg.py"
exit /b 0