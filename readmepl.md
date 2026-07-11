> **WAŻNE:** To jest wersja polska. Wersję angielską znajdziesz w [README.md](./README.md).

# Nahida4479 Recorder

Prosty skrypt w Pythonie z GUI do nagrywania i odtwarzania ruchów myszki i klawiatury, z obsługą globalnych skrótów klawiszowych, zapisem/wczytywaniem do JSON oraz opcjonalnym trybem pętli.

## Wspierane systemy

| Windows | Linux (X11) | Linux (Wayland) |
|:-------:|:-----------:|:----------------:|
| ✔️ | ✔️ | ✔️/❌ |

## Instalacja

```bash
git clone https://github.com/Nahida4479/Nahida4479-recorder.git
cd Nahida4479-recorder
pip install -r requirements.txt
```

## Użycie

```bash
python Nahida4479_recorder.py
```

- **⏺ Record** – start/stop nagrywania ruchów myszki i klawiatury
- **▶ Play** – odtwarzanie nagrania (włącz **Loop**, aby odtwarzać w pętli)
- **File → Save/Load** – eksport/import nagrania jako `.json`
- **Edit → Keybinds…** – ustawianie globalnych skrótów klawiszowych (start/stop nagrywania, start/stop odtwarzania, awaryjne zatrzymanie)
