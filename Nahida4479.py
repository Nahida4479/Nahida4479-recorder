# Nahida4479
import time
import threading
from pynput import mouse, keyboard
import tkinter as tk
import json
from tkinter import filedialog, messagebox
import os
import emoji


class Nahida4479Recorder:

    def save_to_file(self, filepath):
        data = []
        for event_type, event_data, timestamp in self.recorded_events:
            if event_type == "click":
                x, y, button = event_data
                data.append(
                    {
                        "type": "click",
                        "x": x,
                        "y": y,
                        "button": str(button),
                        "timestamp": timestamp,
                    }
                )
            elif event_type == "key":
                data.append(
                    {type: "key", "key": str(event_data), "timestamp": timestamp}
                )
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved to {filepath}")

    def __init__(self):
        self.recorded_events = []
        self.is_recording = False
        self.start_time = 0
        self.used_keys = {}

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
        print(emoji.emojize("REC START :red_circle:"))
        messagebox.showinfo("Recorder", "Recording started!")

    def stop_recording(self):
        self.is_recording = False
        print("REC STOP")
        messagebox.showinfo(
            "Recorder", f"Recording stopped. Saved {len(self.recorded_events)} :)"
        )

    def play_recording(self):
        if not self.recorded_events:
            print("ERROR: You didn't record the script :(")
            return
        print("PLAY START in 2 seconds")

        self.is_playing = True
        time.sleep(2)

        last_time = 0
        for i, (event_type, data, timestamp) in enumerate(self.recorded_events):
            if not self.is_playing:
                break

        print(f"Step {i+1}/{len(self.recorded_events)}: {event_type}")

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
        print("PLAY FINISHED")
        messagebox.showinfo("Recorder", "Playback finished!")


def on_click(x, y, button, pressed):
    if pressed:
        if "recorder" in globals() and recorder.is_recording:
            recorder.add_event("click", (x, y, button))


def on_press(key):
    if recorder.binding_mode:
        return
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

    root.configure(bg="#1e1e1e")
    root.geometry("500x500")
    current_file = {"path": None}
    
    def save():
        if current_file["path"] is None:
            save_as()
        else:
            recorder.save_to_file(current_file["path"])

    def save_as():
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            current_file["path"] = path
            recorder.save_to_file(path)

    def bind_key(action_name, attr_name):
        popup = tk.Toplevel(root)
        recorder.binding_mode = True
        popup.title(f"Bind: {action_name}")
        popup.geometry("300x100")

        label = tk.Label(popup, text="Press the key...")
        label.pack(pady=20)

        def on_key(event):
            key_map = {
                "F1": keyboard.Key.f1,
                "F2": keyboard.Key.f2,
                "F3": keyboard.Key.f3,
                "F4": keyboard.Key.f4,
                "F5": keyboard.Key.f5,
                "F6": keyboard.Key.f6,
                "F7": keyboard.Key.f7,
                "F8": keyboard.Key.f8,
                "F9": keyboard.Key.f9,
                "F10": keyboard.Key.f10,
            }
            key_name = event.keysym
            if key_name in key_map:
                new_key = key_map[key_name]
                if new_key in recorder.used_keys and recorder.used_keys[new_key] != attr_name:
                    label.config(text=f"Error key set to: {recorder.used_keys[new_key]}!")
                    return
                old_key = getattr(recorder, attr_name)
                if old_key in recorder.used_keys:
                    del recorder.used_keys[old_key]
                    
                recorder.used_keys[new_key] = attr_name
                setattr(recorder,attr_name,new_key)
                label.config(text=f"Key set: {key_name}")
                recorder.binding_mode = False
                popup.after(800, popup.destroy)
            else:
                label.config(text="ERROR: Use F1-F12 only!")
                print(f"KEY BIND ERROR: {key_name} is not F1-F12")

        popup.bind("<Key>", on_key)
        popup.focus_force()
        popup.protocol(
            "WM_DELETE_WINDOW",
            lambda: [setattr(recorder, "binding_mode", False), popup.destroy()],
        )

    btn_style = {
        "bg": "#252526",
        "fg": "white",
        "relief": "flat",
        "activebackground": "#3e3e42",
        "font": ("Segoe UI", 9)
    }
    
    def show_file_menu():
        x = file_btn.winfo_rootx()
        y = file_btn.winfo_rooty() + file_btn.winfo_height()
        file_context_menu.post(x, y)
        root.bind("<Button-1>", lambda e: file_context_menu.unpost())
        root.bind("<Configure>", lambda e: file_context_menu.unpost())
        
    def show_edit_menu():
        x = edit_btn.winfo_rootx()
        y = edit_btn.winfo_rooty() + edit_btn.winfo_height()
        key_menu.post(x, y)  
        root.bind("<Button-1>", lambda e: key_menu.unpost())
        root.bind("<Configure>", lambda e: key_menu.unpost())

        
    def toggle_record():
        if not recorder.is_recording:
            recorder.start_recording()
            record_btn.config(text="⏹ Stop Rec", bg="#7f0000")
            
        else:
            recorder.stop_recording()
            record_btn.config(text="⏺ Record", bg="#c0392b")
            
    def toggle_play():
        if not recorder.is_playing:
            t = threading.Thread(target=recorder.play_recording)
            t.daemon = True
            t.start()
            play_btn.config(text="⏹ Stop", bg="#c0392b")
        else:
            recorder.is_playing = False
            play_btn.config(text="▶ Play", bg="#27ae60")
    
    file_context_menu = tk.Menu(root, tearoff=0, bg="#252526", fg="white", activebackground="#3e3e42", bd=0)
    file_context_menu.add_command(label="Save", command=save)
    file_context_menu.add_command(label="Save as", command=save_as)
    file_context_menu.add_separator()
    file_context_menu.add_command(label="Exit", command=root.quit)
    
    key_menu = tk.Menu(root, tearoff=0, bg="#252526", fg="white", activebackground="#3e3e42", bd=0)
    key_menu.add_command(label="Start script key", command=lambda: bind_key("Start Play", "hotkey_start_play"))
    key_menu.add_command(label="Stop script key", command=lambda: bind_key("Stop Play", "hotkey_stop_play"))
    key_menu.add_separator()
    key_menu.add_command(label="Start Record key", command=lambda: bind_key("Start Record", "hotkey_start_rec"))
    key_menu.add_command(label="Stop Record key", command=lambda: bind_key("Stop Record", "hotkey_stop_rec"))
    key_menu.add_separator()
    key_menu.add_command(label="Emergency Stop Key", command=lambda: bind_key("Emergency Stop", "hotkey_emergency"))
    
    top_bar = tk.Frame(root, bg="#252526", height=35)
    top_bar.pack(side="top", fill="x")

    file_btn = tk.Button(top_bar, text="File", command=show_file_menu, **btn_style)
    file_btn.pack(side="left", padx=5, pady=5)
    
    edit_btn = tk.Button(top_bar, text="Edit", command=show_edit_menu, **btn_style)
    edit_btn.pack(side="left", padx=5, pady=5)
    
    btn_style = {
        "bg": "#252526",
        "fg": "white",
        "relief": "flat",
        "activebackground": "#3e3e42",
        "font": ("Segoe UI", 9),
    }


    is_loop = tk.BooleanVar (value=False)
    control_bar = tk.Frame(root, bg="#1e1e1e")
    control_bar.pack(side="top", fill="x", padx=10, pady=5)
    
    record_btn = tk.Button(control_bar, text="⏺ Record", bg="#c0392b", fg="white", relief="flat", font=("Segoe UI", 9), activebackground="#2ecc71", command=lambda: toggle_record())
    record_btn.pack(side="left", padx=5)
    
    play_btn = tk.Button(control_bar, text="▶ Play", bg="#27ae60", fg="white", relief="flat", font=("Segoe UI", 9), activebackground="#2ecc71", command=lambda: toggle_play())
    play_btn.pack(side="left", padx=5)
    
    loop_check = tk.Checkbutton(control_bar, text="Loop", variable=is_loop, bg="#1e1e1e", fg="white", selectcolor="#1e1e1e", activebackground="#1e1e1e", activeforeground="white", font=("Segoe UI", 9))
    loop_check.pack(side="left", padx=5)
        
    root.mainloop()

if __name__ == "__main__":

    recorder = Nahida4479Recorder()

    mouse_listener = mouse.Listener(on_click=on_click)
    key_listener = keyboard.Listener(on_press=on_press)
    mouse_listener.start()
    key_listener.start()

    setup_gui()
