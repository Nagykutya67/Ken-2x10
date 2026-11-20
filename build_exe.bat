@echo off
cd /d "%~dp0"
py -3 -m pip install pyinstaller
py -3 -m PyInstaller --noconfirm --clean --windowed --name Keno2x10-v2.1 --add-data "data\draws.csv;data" keno\__main__.py
pause
