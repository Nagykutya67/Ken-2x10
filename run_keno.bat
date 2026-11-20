@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto python
py -3 -m keno
goto end
:python
python -m keno
:end
