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
"runtime\venv\Scripts\python.exe" -m pip install openai-whisper

if exist "runtime\ffmpeg\ffmpeg.exe" (
    echo ffmpeg juz jest - pomijam pobieranie.
) else (
    echo Pobieranie ffmpeg (ok. 90 MB)...
    if not exist "runtime\ffmpeg" mkdir "runtime\ffmpeg"
    powershell -NoProfile -Command "Invoke-WebRequest 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'runtime\ffmpeg\ffmpeg.zip'; Expand-Archive 'runtime\ffmpeg\ffmpeg.zip' 'runtime\ffmpeg\tmp' -Force; Copy-Item 'runtime\ffmpeg\tmp\*\bin\ffmpeg.exe' 'runtime\ffmpeg\'; Remove-Item 'runtime\ffmpeg\ffmpeg.zip','runtime\ffmpeg\tmp' -Recurse -Force"
    if not exist "runtime\ffmpeg\ffmpeg.exe" (
        echo UWAGA: automatyczne pobranie ffmpeg nie powiodlo sie.
        echo Pobierz recznie z https://www.gyan.dev/ffmpeg/builds/ i umiesc
        echo plik ffmpeg.exe w folderze runtime\ffmpeg\
    )
)

echo.
echo GOTOWE. Od teraz uzywaj Transkrybuj.bat lub Transkrybuj_MEDIUM.bat
pause
