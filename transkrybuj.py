# -*- coding: utf-8 -*-
"""Transkrypcja audio -> tekst. Wersja konsolowa: minimum ruchomych części.

Użycie:
  1. Wrzuć pliki audio do folderu 'do_transkrypcji' i kliknij Transkrybuj.bat
     (albo przeciągnij pliki wprost na Transkrybuj.bat)
  2. Wyniki (.txt ze znacznikami czasu) lądują w folderze 'transkrypcje'

Ustawienia poniżej można zmieniać w razie potrzeby.
"""
import os
import sys
import time
import ctypes
import datetime

# model można nadpisać z pliku .bat (set WHISPER_MODEL=medium); domyślnie small
MODEL = os.environ.get("WHISPER_MODEL", "small")   # tiny / base / small / medium / large
LANGUAGE = "pl"        # "pl", "en" albo None = wykryj automatycznie
BLOCK_SECONDS = 60     # grupowanie w bloki czasowe; 0 = bez grupowania

# Wszystkie ścieżki względem położenia TEGO pliku — cały folder programu
# można przenosić w dowolne miejsce i nadal będzie działał.
BASE = os.path.dirname(os.path.abspath(__file__))
IN_DIR = os.path.join(BASE, "do_transkrypcji")
OUT_DIR = os.path.join(BASE, "transkrypcje")
FFMPEG_DIR = os.path.join(BASE, "runtime", "ffmpeg")
MODELS_DIR = os.path.join(BASE, "runtime", "models")
AUDIO_EXT = (".mp3", ".wav", ".m4a", ".ogg", ".flac")

# ffmpeg wbudowany w folder programu ma pierwszeństwo przed systemowym
if os.path.isfile(os.path.join(FFMPEG_DIR, "ffmpeg.exe")):
    os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")


def windows_keep_awake_and_full_speed():
    """Nie pozwól systemowi zasnąć ani zdławić tego procesu, gdy użytkownik odejdzie."""
    kernel32 = ctypes.windll.kernel32
    # blokada usypiania (ekran może się wygaszać, obliczenia lecą dalej)
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
    kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)

    # wyłączenie EcoQoS/power throttling — Windows 11 potrafi zwolnić procesy
    # "w tle" do ułamka mocy CPU, gdy ekran zgaśnie
    class POWER_THROTTLING(ctypes.Structure):
        _fields_ = [("Version", ctypes.c_ulong),
                    ("ControlMask", ctypes.c_ulong),
                    ("StateMask", ctypes.c_ulong)]

    PROCESS_POWER_THROTTLING_EXECUTION_SPEED = 0x1
    ProcessPowerThrottling = 4
    state = POWER_THROTTLING(1, PROCESS_POWER_THROTTLING_EXECUTION_SPEED, 0)
    kernel32.SetProcessInformation(kernel32.GetCurrentProcess(), ProcessPowerThrottling,
                                   ctypes.byref(state), ctypes.sizeof(state))


def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def group_segments(segments, block_seconds):
    if not block_seconds:
        return [(s["start"], s["end"], s["text"].strip()) for s in segments]
    groups, current = [], None
    for s in segments:
        if current is None:
            current = [s["start"], s["end"], [s["text"].strip()]]
        else:
            current[1] = s["end"]
            current[2].append(s["text"].strip())
        if current[1] - current[0] >= block_seconds:
            groups.append(current)
            current = None
    if current is not None:
        groups.append(current)
    return [(g[0], g[1], " ".join(g[2])) for g in groups]


def main():
    windows_keep_awake_and_full_speed()
    os.makedirs(IN_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    # pliki: z argumentów (przeciągnięte na .bat) albo z folderu do_transkrypcji
    files = [f for f in sys.argv[1:] if f.lower().endswith(AUDIO_EXT)]
    if not files:
        files = sorted(
            os.path.join(IN_DIR, f) for f in os.listdir(IN_DIR)
            if f.lower().endswith(AUDIO_EXT)
        )
    if not files:
        print(f"Brak plików audio. Wrzuć nagrania do folderu:\n  {IN_DIR}\n"
              f"albo przeciągnij pliki na Transkrybuj.bat")
        return

    # Kontrola ffmpeg PRZED startem — bez niego Whisper nie odczyta audio,
    # a błąd systemowy (WinError 2) nie mówi wprost, czego brakuje.
    import shutil
    if not shutil.which("ffmpeg"):
        # awaryjnie: ffmpeg wbudowany w bibliotekę imageio-ffmpeg (instaluje ją Instaluj.bat)
        try:
            import imageio_ffmpeg
            os.makedirs(FFMPEG_DIR, exist_ok=True)
            shutil.copy(imageio_ffmpeg.get_ffmpeg_exe(), os.path.join(FFMPEG_DIR, "ffmpeg.exe"))
            os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")
            print("ffmpeg przygotowany automatycznie (z pakietu imageio-ffmpeg).")
        except ImportError:
            pass
    if not shutil.which("ffmpeg"):
        print("BŁĄD: brak ffmpeg — programu do odczytu plików audio.")
        print("Napraw jednym z dwóch sposobów:")
        print("  1. Uruchom ponownie Instaluj.bat, albo")
        print("  2. Pobierz https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip,")
        print(f"     rozpakuj i skopiuj plik bin\\ffmpeg.exe do folderu:\n     {FFMPEG_DIR}")
        return

    print(f"Plików do przetworzenia: {len(files)} | model: {MODEL} | język: {LANGUAGE or 'auto'}")
    print(f"Ładowanie modelu '{MODEL}' (pierwszy raz = pobieranie z internetu)...")
    import whisper  # import tutaj, żeby komunikat wyżej pojawił się od razu
    # modele trzymamy w folderze programu (przenośne, bez problemu "ć" w ścieżce profilu)
    model = whisper.load_model(MODEL, download_root=MODELS_DIR)

    ok, failed = 0, 0
    for i, path in enumerate(files, 1):
        name = os.path.splitext(os.path.basename(path))[0]
        print(f"\n[{i}/{len(files)}] {os.path.basename(path)}")
        started = time.time()
        try:
            # verbose=False -> whisper sam rysuje pasek postępu w konsoli
            kwargs = {"verbose": False}
            if LANGUAGE:
                kwargs["language"] = LANGUAGE
            result = model.transcribe(path, **kwargs)

            stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            out_path = os.path.join(OUT_DIR, f"{name}_{stamp}.txt")
            grouped = group_segments(result["segments"], BLOCK_SECONDS)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(f"[{format_time(a)} - {format_time(b)}] {t}" for a, b, t in grouped))

            print(f"  OK ({format_time(time.time() - started)}) -> {out_path}")
            ok += 1
        except Exception as e:
            print(f"  BŁĄD: {e}")
            failed += 1

    print(f"\nGotowe: {ok} OK, {failed} błędów. Wyniki w: {OUT_DIR}")


if __name__ == "__main__":
    main()
