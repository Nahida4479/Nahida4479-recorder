> **IMPORTANT:** This is the English version. For the Polish version, see [readmepl.md](./readmepl.md).

# Nahida4479 Recorder

A simple Python script with a GUI for recording and replaying mouse and keyboard actions, with global hotkeys, save/load to JSON, and an optional loop mode.

## Supported Systems

| Windows | Linux (X11) | Linux (Wayland) |
|:-------:|:-----------:|:----------------:|
| ✔️ | ✔️ | ✔️/❌ |

## Installation

```bash
git clone https://github.com/Nahida4479/Nahida4479-recorder.git
cd Nahida4479-recorder
pip install -r requirements.txt
```

## Usage

```bash
python Nahida4479_recorder.py
```

- **⏺ Record** – start/stop recording mouse & keyboard actions
- **▶ Play** – replay the recording (enable **Loop** for continuous playback)
- **File → Save/Load** – export/import a recording as `.json`
- **Edit → Keybinds…** – set global hotkeys (start/stop record, start/stop play, emergency stop)
