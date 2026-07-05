@echo off
chcp 65001 >nul
rem Jednorazowa instalacja na NOWYM komputerze.
rem Wymaga zainstalowanego Pythona (www.python.org, wersja 3.10-3.12 zalecana).
rem Tworzy srodowisko w runtime\venv, instaluje Whisper i pobiera ffmpeg.
cd /d "%~dp0"

echo Szukanie Pythona...
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo BLAD: Python nie jest zainstalowany.
    echo Pobierz go z https://www.python.org/downloads/ i podczas instalacji
    echo zaznacz opcje "Add Python to PATH". Potem uruchom ten plik ponownie.
    pause
    exit /b 1
)

if exist "runtime\venv\Scripts\python.exe" (
    echo Srodowisko juz istnieje - pomijam tworzenie.
) else (
    echo Tworzenie srodowiska w runtime\venv ...
    python -m venv "runtime\venv"
)

echo Instalowanie bibliotek (moze potrwac kilka minut)...
"runtime\venv\Scripts\python.exe" -m pip install --upgrade pip
rem imageio-ffmpeg zawiera w sobie gotowy ffmpeg - zadnych osobnych pobieran
"runtime\venv\Scripts\python.exe" -m pip install openai-whisper imageio-ffmpeg

echo.
echo GOTOWE. Od teraz uzywaj Transkrybuj.bat lub Transkrybuj_MEDIUM.bat
pause
