#Nahida4479
import time
import threading
from pynput import mouse, keyboard

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
            self.recorded_events = []
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

    def play_recording(self):
        if not self-recorder_events:
            print("You didn't record the script :(")
            return
        print("Play starts in 2 seconds")
        time.sleep(2)


        last_time = 0

        for event_type, data, timestamp in self.recorded_events:
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
                        print("Error: {e}")

            print("Script stop")

    def on_press(key):
        try:
            if 'recorder' in globals() and recorder.is_recording:
                if key == keyboard.Key.esc:
                    recorder.stop_recording()
                    return False
            recorder.add_event('key', key)
        except NameError:
            pass
        
        recorder = Nahida4479Recorder()

    mouse_listener = mouse.Listener(on_click=on_click)
    key_listener = keyboard.Listener(on_press=on_press)


    