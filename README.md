# Transkryptor

Prosta, całkowicie **lokalna** transkrypcja nagrań audio na tekst (po polsku i nie tylko), oparta o [OpenAI Whisper](https://github.com/openai/whisper). Bez chmury, bez abonamentu, bez wysyłania nagrań w internet — wszystko liczy się na Twoim komputerze.

## Możliwości

- 🎙️ Transkrypcja audio (mp3, wav, m4a, ogg, flac, aac, wma, opus) i **wideo** (mp4, mpg, mkv, mov, avi, webm — z filmu wyciągana jest ścieżka dźwiękowa) → pliki `.txt` ze znacznikami czasu
- 📚 Kolejka wielu plików naraz (przetwarzane jeden po drugim, model ładowany raz)
- 🕐 Wynik grupowany w bloki czasowe (domyślnie ~60 s) zamiast porwanych urywków
- 💤 Blokuje usypianie komputera na czas pracy (Windows Modern Standby zamraża obliczenia)
- 🚀 Wyłącza dławienie procesu przez Windows (EcoQoS), gdy odejdziesz od komputera
- 📦 Przenośny — cały folder można skopiować na inny dysk lub komputer

## Użycie

1. Wrzuć nagrania do folderu `do_transkrypcji`
2. Kliknij dwa razy `Transkrybuj.bat` (model *small* — szybszy) albo `Transkrybuj_MEDIUM.bat` (dokładniejszy, wolniejszy, ~5 GB wolnego RAM)
3. Wyniki pojawią się w folderze `transkrypcje`

Można też przeciągnąć pliki audio myszką wprost na plik `.bat`.

## Instalacja na nowym komputerze (Windows)

1. Zainstaluj [Pythona](https://www.python.org/downloads/) — zaznacz **"Add Python to PATH"**
2. Uruchom `Instaluj.bat` — utworzy środowisko, pobierze bibliotekę Whisper i ffmpeg
3. Gotowe — używaj `Transkrybuj.bat`

Przy pierwszej transkrypcji model Whisper (~0,5–1,5 GB) pobierze się automatycznie do `runtime\models`.

## Ustawienia

Na górze pliku `transkrybuj.py`:

| Ustawienie | Domyślnie | Opis |
|---|---|---|
| `MODEL` | `small` | tiny / base / small / medium / large (większy = dokładniejszy i wolniejszy) |
| `LANGUAGE` | `pl` | język nagrania; `None` = wykryj automatycznie |
| `BLOCK_SECONDS` | `60` | długość bloku czasowego w wyniku; `0` = bez grupowania |

## Wskazówki

- Do polskich nagrań używaj co najmniej modelu `small` — `tiny`/`base` robią dużo błędów
- Na zwykłym laptopie (bez karty graficznej NVIDIA) model `medium` liczy się kilka razy dłużej, niż trwa nagranie
- Nie zamykaj klapy laptopa podczas pracy — to wymusza uśpienie i zatrzymuje obliczenia

## Licencja

MIT — patrz [LICENSE](LICENSE). Wykorzystuje: [Whisper](https://github.com/openai/whisper) (MIT), [FFmpeg](https://ffmpeg.org/) (GPL/LGPL), Python (PSF).
