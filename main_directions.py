import tkinter as tk
from tkinter import messagebox
from threading import Thread, Event
from queue import Queue
from typing import Optional
import time
import math
import numpy as np
import sounddevice as sd
from misc import Vector
from data_sources.orlosky_data_source import OrloskyDataSource

# Configuration
THRESHOLD = 5
STEP_TIMEOUT = 2.0            # Seconds to perform next step
NOTE_DURATION = 0.5           # Seconds for normal choreography note
SUCCESS_WAIT = 0.25            # Seconds pause before success sequence
SUCCESS_NOTE_DURATION = 0.25   # Seconds per note in success sequence

# Notes: C4, E4, G4, C5
CHOREO_NOTES = [261.63, 329.63, 392.00, 523.25]

DIRECTIONS = ["left", "right", "up", "down", "center"]

class EyeTrackerApp:
    def __init__(self, root, datasource):
        self.root = root
        self.root.title("Eye Tracker")
        self.calibration_data = {}
        self.datasource = datasource
        self.running = Event()

        self.canvas = tk.Canvas(root, width=400, height=400)
        self.canvas.pack()

        self.boxes = {}
        self.create_ui()

        self.calibrate_button = tk.Button(root, text="Calibrate", command=self.start_calibration)
        self.calibrate_button.pack(pady=10)

        self.poll_thread = Thread(target=self.poll_data)
        self.poll_thread.daemon = True

        self.sound_queue = Queue()
        self.sound_thread = Thread(target=self.sound_loop)
        self.sound_thread.daemon = True
        self.sound_thread.start()

        self.choreography_mode = True
        self.choreography_steps = ["left", "up", "right", "down"]
        self.choreography_index = 0
        self.last_step_time = None

    def create_ui(self):
        positions = {
            "up": (150, 50),
            "down": (150, 250),
            "left": (50, 150),
            "right": (250, 150),
            "center": (150, 150)
        }
        for direction, (x, y) in positions.items():
            box = self.canvas.create_rectangle(x, y, x + 100, y + 100, fill="gray")
            self.canvas.create_text(x + 50, y + 50, text=direction.capitalize(), fill="white")
            self.boxes[direction] = box

    def start_calibration(self):
        self.running.clear()
        self.root.withdraw()
        for direction in DIRECTIONS:
            self.calibrate_direction(direction)
        self.root.deiconify()

        self.running.set()
        if not self.poll_thread.is_alive():
            self.poll_thread.start()

    def calibrate_direction(self, direction):
        win = tk.Toplevel()
        win.title(f"Calibrating {direction}")
        label = tk.Label(win, text=f"Look {direction.upper()} and press ENTER", font=("Arial", 20))
        label.pack(padx=20, pady=40)

        def on_enter(event):
            vec = self.datasource.get_next_vector()
            if vec:
                self.calibration_data[direction] = vec
                win.destroy()
            else:
                messagebox.showerror("Error", "No vector received. Try again.")

        win.bind("<Return>", on_enter)
        win.grab_set()
        win.wait_window()

    def poll_data(self):
        while True:
            if not self.running.is_set():
                time.sleep(0.1)
                continue

            vec = self.datasource.get_next_vector()
            if vec:
                match = self.match_direction(vec)
                if self.choreography_mode:
                    self.handle_choreography(match)
                else:
                    self.update_boxes(match)
            time.sleep(0.05)

    def update_boxes(self, active):
        for direction, box in self.boxes.items():
            color = "green" if direction == active else "gray"
            self.canvas.itemconfig(box, fill=color)

    def match_direction(self, vec: Vector) -> Optional[str]:
        if not self.calibration_data:
            return None

        def distance(v1: Vector, v2: Vector) -> float:
            return math.sqrt((v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2)

        min_dir = None
        min_dist = float('inf')
        for direction, ref_vec in self.calibration_data.items():
            dist = distance(vec, ref_vec)
            if dist < min_dist:
                min_dist = dist
                min_dir = direction

        return min_dir if min_dist <= THRESHOLD else None

    def play_note(self, freq, duration):
        self.sound_queue.put(("note", freq, duration))

    def play_success_sequence(self):
        self.sound_queue.put(("success",))

    def sound_loop(self):
        sample_rate = 44100
        while True:
            task = self.sound_queue.get()
            if task[0] == "note":
                _, freq, duration = task
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                wave = 0.5 * np.sin(2 * np.pi * freq * t)
                sd.play(wave, samplerate=sample_rate, blocking=True)
            elif task[0] == "success":
                time.sleep(SUCCESS_WAIT)
                for freq in CHOREO_NOTES:
                    t = np.linspace(0, SUCCESS_NOTE_DURATION, int(sample_rate * SUCCESS_NOTE_DURATION), False)
                    wave = 0.5 * np.sin(2 * np.pi * freq * t)
                    sd.play(wave, samplerate=sample_rate, blocking=True)

    def handle_choreography(self, match):
        if match is None:
            return

        current_time = time.time()

        if self.choreography_index == 0:
            if match == self.choreography_steps[0]:
                self.choreography_index = 1
                self.last_step_time = current_time
                self.play_note(CHOREO_NOTES[0], NOTE_DURATION)
        else:
            if match == self.choreography_steps[self.choreography_index]:
                self.play_note(CHOREO_NOTES[self.choreography_index], NOTE_DURATION)
                self.choreography_index += 1
                self.last_step_time = current_time

                if self.choreography_index == len(self.choreography_steps):
                    print("done")
                    self.play_success_sequence()
                    self.choreography_index = 0
                    self.last_step_time = None
            elif current_time - self.last_step_time > STEP_TIMEOUT:
                self.choreography_index = 0
                self.last_step_time = None

        self.update_boxes(match)

if __name__ == '__main__':
    root = tk.Tk()
    datasource = OrloskyDataSource()
    datasource.start()
    app = EyeTrackerApp(root, datasource)
    root.mainloop()
    datasource.stop()

