import customtkinter as ctk
import threading
from engine import recorder
import time

app = ctk.CTk()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

PLAY_COLOR      = "#27ae60"
PLAY_HOVER      = "#1e8449"
PLAY_CLICK      = "#145a32"
RECORD_COLOR    = "#c0392b"
RECORD_HOVER    = "#a93226"
RECORD_CLICK    = "#7b241c"
LOOP_ON_COLOR   = "#cc0000"
BG_MAIN         = "#1e1e1e"
BG_CONTROL      = "#2a2a2a"
BG_LOG          = "#1a1a1a"
TOAST_BG        = "#7f0000"
MENU_BG         = "#8b0000"   
    

app.title("Nahida4479 Recorder")
app.geometry("480x380")          
app.resizable(False, False)
app.configure(fg_color=BG_MAIN)

top_bar = ctk.CTkFrame(app, fg_color="#000000", height=45, corner_radius=0)
top_bar.pack(fill="x", side="top")
top_bar.pack_propagate(False)

menu_container = ctk.CTkFrame(top_bar, fg_color="transparent", border_width=0, height=32)
menu_container.pack(side="left", padx=10, pady=6)

btn_file = ctk.CTkButton(menu_container, text="File", width=65, height=28, fg_color="#333333", hover_color="#444444", text_color="#FFFFFF", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), corner_radius=6 )            
btn_file.pack(side="left", padx=(5, 2))

btn_edit = ctk.CTkButton(menu_container, text="Edit", width=65, height=28, fg_color="#333333", hover_color="#444444", text_color="#FFFFFF", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), corner_radius=6)
btn_edit.pack(side="left", padx=(2, 5))

status_label = ctk.CTkLabel(app, text="STATUS: READY", font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), text_color="#FFFFFF")
status_label.pack(pady=(18, 12))

control_frame = ctk.CTkFrame(app, fg_color=BG_CONTROL, corner_radius=10, height=80)
control_frame.pack(fill="x", padx=25, pady=(0, 12))
control_frame.pack_propagate(False)

def update_record_button():
    success = recorder.toggle_record()
    if success:
        if recorder.is_recording:
            btn_record.configure(text="⏹ Stop Rec", fg_color="#7f0000")
            print("[GUI] UI updated to: Recording")
            log_to_gui("Recording started...")
        else:
            btn_record.configure(text="⏺  Record", fg_color=RECORD_COLOR)
            print("[GUI] UI updated to: Idle")
            log_to_gui("Recording stopped and saved.")
    else:
        print("[GUI] Action blocked by Engine (cooldown or error)")
        log_to_gui("Action blocked: Cooldown active")

def update_play_button():
    if not recorder.is_playing:
        success = recorder.play_recording_is_thread()
        if success:
            btn_play.configure(text="⏹ Stop", fg_color="#c0392b")
            threading.Thread(target=recorder.play_recording, daemon=True).start()
        else:
            btn_play.configure(text="▶  Play", fg_color=PLAY_COLOR)
    else:
        recorder.is_playing = False
        btn_play.configure(text="▶  Play", fg_color=PLAY_COLOR)
    

def reset_play_button():
    btn_play.configure(text="▶  Play", fg_color=PLAY_COLOR)

recorder.on_play_finished = reset_play_button

def update_loop():
    recorder.is_loop_enabled = bool(loop_switch.get())

def on_play_enter(e):   btn_play.configure(fg_color=PLAY_HOVER)
def on_play_leave(e):   btn_play.configure(fg_color=PLAY_COLOR)
def on_play_press(e):   btn_play.configure(fg_color=PLAY_CLICK)
def on_play_release(e): btn_play.configure(fg_color=PLAY_HOVER)

btn_play = ctk.CTkButton(
    control_frame, text="▶  Play", width=155, height=44,
    fg_color=PLAY_COLOR, hover_color=PLAY_COLOR,
    text_color="#FFFFFF", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
    corner_radius=12, command=update_play_button
)
btn_play.pack(side="left", padx=(12, 8), pady=18)
btn_play.bind("<Enter>", on_play_enter)
btn_play.bind("<Leave>", on_play_leave)
btn_play.bind("<ButtonPress-1>", on_play_press)
btn_play.bind("<ButtonRelease-1>", on_play_release)

def on_rec_enter(e):   btn_record.configure(fg_color=RECORD_HOVER)
def on_rec_leave(e):   btn_record.configure(fg_color=RECORD_COLOR)
def on_rec_press(e):   btn_record.configure(fg_color=RECORD_CLICK)
def on_rec_release(e): btn_record.configure(fg_color=RECORD_HOVER)

btn_record = ctk.CTkButton(
    control_frame, text="⏺  Record", width=155, height=44,
    fg_color=RECORD_COLOR, hover_color=RECORD_COLOR,
    text_color="#FFFFFF", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
    corner_radius=12, command=update_record_button
)
btn_record.pack(side="left", padx=(0, 12), pady=18)
btn_record.bind("<Enter>", on_rec_enter)
btn_record.bind("<Leave>", on_rec_leave)
btn_record.bind("<ButtonPress-1>", on_rec_press)
btn_record.bind("<ButtonRelease-1>", on_rec_release)

loop_col = ctk.CTkFrame(control_frame, fg_color="transparent")
loop_col.pack(side="left", fill="y", expand=True, padx=(0, 15))

loop_switch = ctk.CTkSwitch(
    loop_col, text="", onvalue=True, offvalue=False,
    progress_color=LOOP_ON_COLOR, button_color="#FFFFFF",
    button_hover_color="#DDDDDD", fg_color="#555555",
    width=46, height=22, switch_width=46, switch_height=22,
    command=update_loop
)
loop_switch.pack(pady=(18, 2))

loop_lbl = ctk.CTkLabel(loop_col, text="Loop", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#FFFFFF")
loop_lbl.pack()

log_box = ctk.CTkTextbox(
    app, 
    height=110, 
    font=ctk.CTkFont(family="Segoe UI", size=12), 
    fg_color=BG_LOG, 
    border_color="#555555", 
    border_width=1, 
    text_color="#CCCCCC", 
    corner_radius=8
)
log_box.pack(fill="x", padx=25, pady=(10, 5))
log_box.configure(state="disabled")

toast_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#FFFFFF", fg_color="#27ae60", corner_radius=8, padx=14, pady=6)
toast_label.place_forget()

def show_toast(message, color="#27ae60"):
    toast_label.configure(text=message, fg_color=color)
    toast_label.place(relx=0.5, rely=0.8, anchor="center")
    app.after(2000, toast_label.place_forget)

recorder.show_toast = show_toast


def log_to_gui(message):
    current_time = time.strftime("%H:%M:%S")
    full_message = f"[{current_time}] {message}\n"
    log_box.configure(state="normal")
    log_box.insert("end", full_message)
    log_box.configure(state="disabled")
    log_box.see("end")

recorder.gui_log = log_to_gui
log_to_gui("System initialized and ready.")

if __name__ == "__main__":
    app.mainloop()