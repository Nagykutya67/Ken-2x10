@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo Keno 2x10 Analytics v2.1.0 - Windows build
echo ==========================================

where py >nul 2>nul
if errorlevel 1 (
    echo HIBA: A Python launcher nem talalhato.
    echo Telepits Python 3.11 vagy ujabb verziot.
    pause
    exit /b 1
)

echo [1/4] PyInstaller telepitese...
py -3 -m pip install --upgrade pyinstaller
if errorlevel 1 goto build_error

echo [2/4] Korabbi build torlese...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Keno2x10-v2.1.spec del /q Keno2x10-v2.1.spec

echo [3/4] Windows EXE keszitese...
py -3 -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onedir ^
  --name "Keno2x10-v2.1" ^
  --add-data "data\draws.csv;data" ^
  --collect-all tkinter ^
  launcher.py

if errorlevel 1 goto build_error

echo [4/4] Build ellenorzese...
if not exist "dist\Keno2x10-v2.1\Keno2x10-v2.1.exe" goto build_error

echo.
echo SIKERES BUILD
echo Program:
echo %CD%\dist\Keno2x10-v2.1\Keno2x10-v2.1.exe
echo.
pause
exit /b 0

:build_error
echo.
echo A BUILD SIKERTELEN.
echo A hiba reszletei fent lathatok.
pause
exit /b 1
