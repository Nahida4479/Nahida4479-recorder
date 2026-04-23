import platform
import os
import sys
SYSTEM = platform.system()

if SYSTEM != "Linux":
    try:
        from evdev import UInput, ecodes as e, list_devices, InputDevice
        LINUX_EVDEV = True
    except ImportError:
        LINUX_EVDEV = False
    
    mouse_lib = None
    keyboard_lib = None
elif SYSTEM == "Windows":
    LINUX_EVDEV = False
    from pynput import mouse, keyboard
    mouse_lib = mouse
    keyboard_lib = keyboard
            
import time
import threading
import json
from pynput import mouse, keyboard

class Nahida4479Recorder:
    def __init__(self):
        self.is_loop_enabled = False
        self.recorded_events = []
        self.is_recording = False
        self.start_time = 0
        self.used_keys = {}
        self.on_play_finished = None
        self.show_toast = None
        self.last_action_time = 0
        self.mouse_controller = mouse.Controller()
        self.kb_controller = keyboard.Controller()
        self.hotkey_start_play = keyboard.Key.f4
        self.hotkey_stop_play = keyboard.Key.f6
        self.hotkey_start_rec = keyboard.Key.f8
        self.hotkey_stop_rec = keyboard.Key.f9
        self.hotkey_emergency = keyboard.Key.f12
        self.binding_mode = False
        self.is_playing = False
        self.on_before_play = None
        self.on_before_play = None
        self.mouse_controller = mouse.Controller()
        self.kb_controller = keyboard.Controller()
        
    def play_recording_is_thread(self):
        if not self.recorded_events:
            print("ERROR: No events recorded! Cannot play.")
            if self.show_toast:
                self.show_toast("Error: Record something first!", "#555555")
            return False
        thread = threading.Thread(target=self.play_recording, daemon=True)
        thread.start()
        return True

    def toggle_record(self):
        if not self.is_recording:
            self.start_recording()
            return True
        else:
            self.stop_recording()
            return True

    def save_to_file(self, filepath):
        data = []
        for event_type, event_data, timestamp in self.recorded_events:
            if event_type == "click":
                x, y, button = event_data
                data.append({"type": "click", "x": x, "y": y, "button": str(button), "timestamp": timestamp})
            elif event_type == "key":
                data.append({"type": "key", "key": str(event_data), "timestamp": timestamp})
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved to {filepath}")
        
        
    def load_from_file(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        self.recorded_events = []
        for item in data:
            if item["type"] == "click":
                btn = mouse.Button.left if "left" in item["button"] else mouse.Button.right
                self.recorded_events.append(("click", (item["x"], item["y"], btn), item["timestamp"]))
            elif item["type"] == "key":
                self.recorded_events.append(("key", item["key"], item["timestamp"]))
        print(f"Loaded {len(self.recorded_events)} events from {filepath}")
    
    
    def add_event(self, event_type, data):
        if self.is_recording:
            timestamp = time.time() - self.start_time
            self.recorded_events.append((event_type, data, timestamp))

    def start_recording(self):
        self.recorded_events = []
        self.start_time = time.time()
        self.is_recording = True
        print("[ENGINE] Recording started...")
        if self.show_toast:
            self.show_toast("⏺ Recording started!", "#c0392b")
        return True

    def stop_recording(self):
        self.last_action_time = time.time()
        self.is_recording = False
        print("REC STOP")
        if self.show_toast:
            self.show_toast(f"⏹ Saved {len(self.recorded_events)} events", "#7f0000")

    def play_recording(self):
        self.last_action_time = time.time()
        
        if not self.recorded_events:
            print("Error: No events to play! Record something first.")
            return False

        self.is_playing = True
        
        if self.on_before_play:
            self.on_before_play()
        time.sleep(2)
        
        while True:
            last_time = 0
            for i, (event_type, data, timestamp) in enumerate(self.recorded_events):
                if not self.is_playing:
                    break
                wait_time = timestamp - last_time
                if wait_time > 0:
                    time.sleep(wait_time)
                last_time = timestamp
                if event_type == "move":
                    x, y = data
                    self.mouse_controller.position = (x, y)
                elif event_type == "click":
                    x, y, button = data
                    if SYSTEM == "Windows":
                        import ctypes
                        ctypes.windll.user32.SetCursorPos(int(x), int(y))
                        is_left = "left" in str(button).lower()
                        flags_down = 0x0002 if is_left else 0x0008
                        flags_up = 0x0004 if is_left else 0x0010
                        ctypes.windll.user32.mouse_event(flags_down, 0, 0, 0, 0)
                        ctypes.windll.user32.mouse_event(flags_up, 0, 0, 0, 0)
                    else:
                        self.mouse_controller.position = (x, y)
                        self.mouse_controller.click(button)
                        
                elif event_type == "key":
                    try:
                        # Rozróżniamy: string z JSON vs obiekt pynput z nagrania na żywo
                        if isinstance(data, str):
                            if data.startswith("Key."):
                                key_name = data.split(".")[1]
                                key_obj = getattr(keyboard.Key, key_name, None)
                                if key_obj:
                                    self.kb_controller.press(key_obj)
                                    self.kb_controller.release(key_obj)
                            else:
                                char = data.replace("'", "").strip()
                                if len(char) == 1:
                                    self.kb_controller.press(char)
                                    self.kb_controller.release(char)
                        else:
                            # obiekt pynput – działa tak samo na Windows i Linux
                            self.kb_controller.press(data)
                            self.kb_controller.release(data)
                    except Exception as e:
                        print(f"[KEY ERROR] {e} – data: {data}")
            if not self.is_loop_enabled or not self.is_playing:
                break

        self.is_playing = False
        print("PLAY FINISHED")
        
        if self.on_play_finished:
            self.on_play_finished()
            
        if self.show_toast:
            self.show_toast("▶ Playback finished!", "#27ae60")


recorder = Nahida4479Recorder()

def on_click(x, y, button, pressed):
    if pressed and recorder.is_recording:
        recorder.add_event("click", (x, y, button))
def on_move(x, y):
    if recorder.is_recording:
        recorder.add_event("move", (x, y))
def on_press(key):
    if recorder.binding_mode: 
        return
    try:
        
        hotkeys = [
            recorder.hotkey_emergency,
            recorder.hotkey_start_rec,
            recorder.hotkey_stop_rec,
            recorder.hotkey_start_play,
            recorder.hotkey_stop_play
        ]
        if key == recorder.hotkey_emergency:
            recorder.is_playing = False
            recorder.is_recording = False
            os._exit(0)
        elif key == recorder.hotkey_start_rec:
            if not recorder.is_recording: recorder.start_recording()
            return
        elif key == recorder.hotkey_stop_rec:
            if recorder.is_recording: 
                recorder.stop_recording()
                return
            
        elif key == recorder.hotkey_start_play:
            if not recorder.is_playing:
                threading.Thread(target=recorder.play_recording, daemon=True).start()
        elif key == recorder.hotkey_stop_play:
            recorder.is_playing = False
        elif recorder.is_recording and key not in hotkeys:
            recorder.add_event("key", key)
    except Exception as e:
        print(f"ERROR: Keybinds")

mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
key_listener = keyboard.Listener(on_press=on_press)
mouse_listener.start()
key_listener.start()