#Nahida4479
import time
import threading from pynput 
import mouse, keyboard

class Nahida4479Recorder:
    def __init__(self):
        self.recorded_events = []
        self.is_recording = False
        self.start_time = 0

        self.mouse_controller = mouse.Controller()
        self.kb_controller = keyboard.Controller()


        def add_event(self, event_type, data):
            if self.is_recording:

                timestamp = time.time() - self.start_time
                self.recorded_events.append((event_type, data, timestamp))

        def start_recording(self):
            self-recorded_events = []
            self.start_time = time.time()
            self.is_recording = True
            print("Recording...")

        def stop_recording(self):
            self.is_recording = False
            print("Recording finished")


        def on_click(x, y, button, pressed):
            if pressed:
                recorder.add_event('click', (x, y, button))
                return False
            recorder.add_event('key', key)
        recorder = Nahida4479Recorder()

    mouse_listener = mouse.Lisstener(on_click=on_click)
    key_listener = keyboard.Listener(on_press=on_press)