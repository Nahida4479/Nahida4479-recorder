import time
import threading
from pynput import mouse, keyboard
import json
import os

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
        self.cooldown = 1
        self.mouse_controller = mouse.Controller()
        self.kb_controller = keyboard.Controller()
        self.hotkey_start_play = keyboard.Key.f4
        self.hotkey_stop_play = keyboard.Key.f6
        self.hotkey_start_rec = keyboard.Key.f8
        self.hotkey_stop_rec = keyboard.Key.f9
        self.hotkey_emergency = keyboard.Key.f12
        self.binding_mode = False
        self.is_playing = False
        
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
        else:
            self.stop_recording()
            return False

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

    def add_event(self, event_type, data):
        if self.is_recording:
            timestamp = time.time() - self.start_time
            self.recorded_events.append((event_type, data, timestamp))

    def start_recording(self):
        now = time.time()
        elapsed = now - self.last_action_time
        if elapsed < self.cooldown:
            print(f"[ENGINE] Cooldown active: {round(3-elapsed, 1)}s remaining")
            remaining = round(self.cooldown - elapsed, 1)
            print(f"COOLDOWN: Wait {remaining}s")
            if self.show_toast:
                self.gui_log(f"Action blocked: Cooldown active ({round(self.cooldown - elapsed, 1)}s)")
            return False
        self.last_action_time = now
        self.last_action_time = time.time()
        self.recorded_events = []
        self.start_time = time.time()
        self.is_recording = True
        print("[ENGINE] Recording started...")
        if self.show_toast:
            self.show_toast("⏺ Recording started!", "#c0392b")
        return False

    def stop_recording(self):
        if time.time() - self.last_action_time < self.cooldown:
            return
        self.last_action_time = time.time()
        self.is_recording = False
        print("REC STOP")
        if self.show_toast:
            self.show_toast(f"⏹ Saved {len(self.recorded_events)} events", "#7f0000")

    def play_recording(self):
        if time.time() - self.last_action_time < self.cooldown:
            return False
        self.last_action_time = time.time()
        
        if not self.recorded_events:
            print("Error: No events to play! Record something first.")
            return False
        if self.on_play_finished:
            self.on_play_finished()
            return True

        self.is_playing = True
        time.sleep(2)

        last_time = 0
        for i, (event_type, data, timestamp) in enumerate(self.recorded_events):
            if not self.is_playing:
                break
            wait_time = timestamp - last_time
            if wait_time > 0:
                time.sleep(wait_time)
            last_time = timestamp

            if event_type == "click":
                x, y, button = data
                self.mouse_controller.position = (x, y)
                self.mouse_controller.click(button)
            elif event_type == "key":
                try:
                    self.kb_controller.press(data)
                    self.kb_controller.release(data)
                except Exception as e:
                    pass

        self.is_playing = False
        print("PLAY FINISHED")
        
        if self.on_play_finished:
            self.on_play_finished()
            
        if self.show_toast:
            self.show_toast("▶ Playback finished!", "#27ae60")

        if self.is_loop_enabled:
            print("Looping...")
            self.play_recording()

recorder = Nahida4479Recorder()

def on_click(x, y, button, pressed):
    if pressed and recorder.is_recording:
        recorder.add_event("click", (x, y, button))

def on_press(key):
    if recorder.binding_mode: return
    try:
        if key == recorder.hotkey_emergency:
            recorder.is_playing = False
            recorder.is_recording = False
            os._exit(0)
        elif key == recorder.hotkey_start_rec:
            if not recorder.is_recording: recorder.start_recording()
        elif key == recorder.hotkey_stop_rec:
            if recorder.is_recording: recorder.stop_recording()
        elif key == recorder.hotkey_start_play:
            if not recorder.is_playing:
                threading.Thread(target=recorder.play_recording, daemon=True).start()
        elif key == recorder.hotkey_stop_play:
            recorder.is_playing = False
        elif recorder.is_recording:
            recorder.add_event("key", key)
    except Exception:
        pass

mouse_listener = mouse.Listener(on_click=on_click)
key_listener = keyboard.Listener(on_press=on_press)
mouse_listener.start()
key_listener.start()