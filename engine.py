import platform
import os
import sys
import time
import threading
import json
from pynput import mouse, keyboard

SYSTEM = platform.system()
LINUX_EVDEV = False

if SYSTEM == "Linux":
    try:
        from evdev import UInput, ecodes as e, list_devices, InputDevice
        LINUX_EVDEV = True
    except ImportError:
        LINUX_EVDEV = False
        

class Nahida4479Recorder:
    def __init__(self):
        self.is_loop_enabled = False
        self.recorded_events = []
        self.is_recording = False
        self.is_playing = False
        self.start_time = 0
        self.last_action_time = 0
        
        self.mouse_controller = mouse.Controller()
        self.kb_controller = keyboard.Controller()
        
        self.hotkey_start_play = keyboard.Key.f4
        self.hotkey_stop_play = keyboard.Key.f6
        self.hotkey_start_rec = keyboard.Key.f8
        self.hotkey_stop_rec = keyboard.Key.f9
        self.hotkey_emergency = keyboard.Key.f12
        
        self.on_play_finished = None
        self.on_before_play = None
        self.show_toast = None
        self.binding_mode = False
        
        self._evdev_devices = []
        
        if SYSTEM == "Linux" and LINUX_EVDEV:
            self._setup_linux_devices()
            threading.Thread(target=self._linux_hotkey_loop, daemon=True).start()
            
            
    def _setup_linux_devices(self):
        from evdev import list_devices, InputDevice, ecodes
        for path in list_devices():
            try:
                dev = InputDevice(path)
                
                if any(cap in dev.capabilities() for cap in [ecodes.EV_KEY, ecodes.EV_REL]):       
                    self._evdev_devices.append(dev)
            except (PermissionError, OSError):
                continue
            
    def _linux_hotkey_loop(self):
        import select
        from evdev import ecodes
        dev_map = {dev.fd: dev for dev in self._evdev_devices}
        
        while True:
            r, _, _ = select.select(list(dev_map.keys()), [], [])
            for fd in r:
                try:
                    for ev in dev_map[fd].read():
                        if ev.type == ecodes.EV_KEY and ev.value == 1: 
                            key_name = ecodes.KEY.get(ev.code, "UNKNOWN")
                            

                            if key_name == "KEY_F8":
                                self.start_recording()
                            elif key_name == "KEY_F9":
                                self.stop_recording()
                            elif key_name == "KEY_F12":
                                os._exit(0)
                except (BlockingIOError, OSError):
                    continue
                                   
    def _linux_record_loop(self):
        import select
        from evdev import ecodes
        dev_map = {dev.fd: dev for dev in self._evdev_devices}
        
        print("[ENGINE] Linux Record Loop started.")
        while self.is_recording:
            r, _, _ = select.select(list(dev_map.keys()), [], [], 0.1)
            for fd in r:
                dev = dev_map[fd]
                try:
                    for ev in dev.read():
                        if not self.is_recording: break
                        ts = ev.timestamp() - self.start_time
                        
                        if ev.type == ecodes.EV_KEY:
                            self.recorded_events.append(("key", ev.code, ts))
                        elif ev.type == ecodes.EV_REL:
                            self.recorded_events.append(("move_rel", (ev.code, ev.value), ts))
                except (BlockingIOError, OSError):
                    continue
                        
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
        self.is_recording = True
        self.start_time = time.time()
        
        if self.show_toast:
            self.show_toast("⏺ Recording started!", "#c0392b")
            
            
        if SYSTEM == "Linux" and LINUX_EVDEV:
            self.recording_thread = threading.Thread(target=self._linux_record_loop, daemon=True)
            self.recording_thread.start()
        else:
            from pynput import mouse, keyboard
            self.m_rec = mouse.Listener(on_click=self.on_click, on_move=self.on_move)
            self.k_rec = keyboard.Listener(on_press=self.on_k_press, on_release=self.on_k_release)
            self.m_rec.start()
            self.k_rec.start()
        return True
  
    
    
    def stop_recording(self):
        self.last_action_time = time.time()
        self.is_recording = False
        print("REC STOP")
        
        if hasattr(self, 'm_rec') and self.m_rec:
            self.m_rec.stop()
            self.m_rec = None
        if hasattr(self, 'k_rec') and self.k_rec:
            self.k_rec.stop()
            self.k_rec = None
        
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

