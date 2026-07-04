@echo off
chcp 65001 >nul
rem Transkrypcja modelem SMALL (szybszy, dobra jakosc). Dwuklik = folder 'do_transkrypcji'.
rem Mozna tez przeciagnac pliki audio wprost na ten plik .bat.
rem Sciezki wzgledne - caly folder programu mozna przenosic w dowolne miejsce.
set "WHISPER_MODEL=small"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"

rem Python: najpierw lokalny (runtime\venv), potem instalacja na tym komputerze
set "PY=%~dp0runtime\venv\Scripts\python.exe"
if not exist "%PY%" set "PY=C:\ClaudeEnvs\whisper_env\Scripts\python.exe"
if not exist "%PY%" (
    echo Nie znaleziono Pythona. Na nowym komputerze uruchom najpierw Instaluj.bat
    pause
    exit /b 1
)

"%PY%" transkrybuj.py %*
echo.
pause
