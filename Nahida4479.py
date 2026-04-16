# Nahida4479
import time
import threading
from pynput import mouse, keyboard
import tkinter as tk
import json
from tkinter import filedialog, messagebox
import os

class Nahida4479Recorder:
    
    def save_to_file(self, filepath):
        data = []
        for event_type, event_data, timestamp in self.recorded_events:
            if event_type == "click":
                x, y, button = event_data
                data.append({
                    "type": "click",
                    "x": x,
                    "y": y,
                    "button": str(button),
                    "timestamp": timestamp
                })
            elif event_type == "key":
                data.append({
                    type: "key",
                    "key": str(event_data),
                    "timestamp": timestamp
                })
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved to {filepath}")
    
    
    def __init__(self):
        self.recorded_events = []
        self.is_recording = False
        self.start_time = 0

        self.mouse_controller = mouse.Controller()
        self.kb_controller = keyboard.Controller()
        self.hotkey_start_play = keyboard.Key.f4
        self.hotkey_stop_play = keyboard.Key.f6
        self.hotkey_start_rec = keyboard.Key.f8
        self.hotkey_stop_rec = keyboard.Key.f9
        self.hotkey_emergency = keyboard.Key.f12
        self.binding_mode = False
        self.is_playing = False
        

    def add_event(self, event_type, data):
        if self.is_recording:

            timestamp = time.time() - self.start_time
            self.recorded_events.append((event_type, data, timestamp))

    def start_recording(self):
        self.recorded_events = []
        self.start_time = time.time()
        self.is_recording = True
        print("Recording...")

    def stop_recording(self):
        self.is_recording = False
        print("Recording finished")

    def play_recording(self):
        if not self.recorded_events:
            print("You didn't record the script :(")
            return
        print("Play starts in 2 seconds")
        self.is_playing = True
        time.sleep(2)
        last_time = 0
        for event_type, data, timestamp in self.recorder_events:
            if not self.is_playing:
                    print("Playback stopped")
            return
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
                print(f"Error: {e}")
        self.is_playing = False
        print("Script stop")

def on_click(x, y, button, pressed):
    if pressed:
        if "recorder" in globals() and recorder.is_recording:
            recorder.add_event("click", (x, y, button))


def on_press(key):
    try:
        if key == recorder.hotkey_emergency:
            print("EMERGENCY STOP")
            recorder.is_playing = False
            recorder.is_recording = False
            os._exit(0)
        if key == recorder.hotkey_start_rec:
            if not recorder.is_recording:
                recorder.start_recording()
                return
            if key == recorder.hotkey_stop_rec:
                if recorder.is_recording:
                    recorder.stop_recording()
            return 
        if key == recorder.hotkey_start_play:
            if not recorder.is_playing:
                t = threading.Thread(target=recorder.play_recording)
                t.daemon = True
                t.start()
                return
        if key == recorder.hotkey_stop_play:
            recorder.id_playing = False
            return
        if recorder.is_recording:
                recorder.add_event("key", key)
    except Exception as e:
            print(f"Error: {e}")
            
def setup_gui():
    root = tk.Tk()
    root.title("Nahida4479 Recorder")

    root.geometry("500x500")
    menubar = tk.Menu(root)

    current_file = {"path": None}

    def save():
        if current_file["path"] is None:
            save_as()
        else:
            recorder.save_to_file(current_file["path"])

    def save_as():
        path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
        if path:
            current_file["path"] = path
            recorder.save_to_file(path)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Save", command=save)
    file_menu.add_command(label="Save as", command=save_as)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)

    def bind_key(action_name, attr_name):
        popup = tk.Toplevel(root)
        recorder.binding_mode = True
        popup.title(f"Bind: {action_name}")
        popup.geometry("300x100")
        label = tk.Label(popup, text="Press the key...")
        label.pack(pady=20)
    
    def on_key(event):
        key_map = {
            "F1": keyboard.Key.f1, "F2": keyboard.Key.f2,
            "F3": keyboard.Key.f3, "F4": keyboard.Key.f4,
            "F5": keyboard.Key.f5, "F6": keyboard.Key.f6,
            "F7": keyboard.Key.f7, "F8": keyboard.Key.f8,
            "F9": keyboard.Key.f9, "F10": keyboard.Key.f10,
        }
        key_name = event.keysym
        if key_name in key_map:
            setattr(recorder, attr_name, key_map[key_name])
            label.config(text=f"Key set: {key_name}")
            recorder.binding_mode = False
            popup.after(800, popup.destroy)
        else:
            label.config(text="Use F1-F10")
            popup.bind("<Key>", on_key)
            popup.focus_force()   
            pupup.protocol("WM_DELETE_WINDOW", lambda: [setattr(recorder, "binding_mode", False), popup.destroy()])
    keyboard_menu = tk.Menu(menubar, tearoff=0)
    keyboard_menu.add_command(label="Start Play key", command=lambda: bind_key("Start Play", "hotkey_start_play"))
    keyboard_menu.add_command(label="Stop Play key",     command=lambda: bind_key("Stop Play",    "hotkey_stop_play"))
    keyboard_menu.add_command(label="Start Record key",  command=lambda: bind_key("Start Record", "hotkey_start_rec"))
    keyboard_menu.add_command(label="Stop Record key",   command=lambda: bind_key("Stop Record",  "hotkey_stop_rec"))
    keyboard_menu.add_separator()
    keyboard_menu.add_command(label="Emergency Stop Key", command=lambda: bind_key("Emergency Stop", "hotkey_emergency"))
    menubar.add_cascade(label="Keyboard", menu=keyboard_menu)
    root.config(menu=menubar)
    root.mainloop()

    

if __name__ == "__main__":
    
    recorder = Nahida4479Recorder()
    mouse_listener = mouse.Listener(on_click=on_click)
    key_listener = keyboard.Listener(on_press=on_press)
    mouse_listener.start()
    key_listener.start()
    setup_gui()
    mouse_listener = mouse.Listener(on_click=on_click)
    key_listener = keyboard.Listener(on_press=on_press)
