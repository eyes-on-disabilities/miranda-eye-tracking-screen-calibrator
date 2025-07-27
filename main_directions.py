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

THRESHOLD = 5
STEP_TIMEOUT = 2.0
NOTE_DURATION = 0.25
SUCCESS_WAIT = 0.25
SUCCESS_NOTE_DURATION = 0.1
CHOREO_NOTES = [261.63, 329.63, 392.00, 523.25]
DIRECTIONS = ["left", "right", "up", "down", "center"]

MATERIAL_COLORS = {
    "background": "#121212",
    "button": "#1F1B24",
    "button_active": "#3700B3",
    "text": "#FFFFFF",
    "highlight": "#03DAC6",
    "box_default": "#2C2C2C",
    "box_active": "#03DAC6"
}

class EyeTrackerApp:
    def __init__(self, root, datasource):
        self.root = root
        self.datasource = datasource
        self.running = Event()
        self.calibration_data = {}

        self.root.title("Eye Tracker")
        self.root.configure(bg=MATERIAL_COLORS["background"])
        self.root.attributes('-fullscreen', True)

        self.canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), bg=MATERIAL_COLORS["background"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.boxes = {}
        self.create_ui()

        self.calibrate_button = tk.Button(root, text="CALIBRATE", command=self.start_calibration,
                                          font=("Helvetica", 24, "bold"),
                                          bg=MATERIAL_COLORS["button"],
                                          fg=MATERIAL_COLORS["text"],
                                          activebackground=MATERIAL_COLORS["button_active"],
                                          activeforeground=MATERIAL_COLORS["highlight"],
                                          relief="flat", padx=20, pady=10)
        self.calibrate_button.place(relx=0.5, rely=0.9, anchor="center")

        self.poll_thread = Thread(target=self.poll_data, daemon=True)
        self.sound_queue = Queue()
        self.sound_thread = Thread(target=self.sound_loop, daemon=True)
        self.sound_thread.start()

        self.choreography_mode = True
        self.choreography_steps = ["left", "up", "right", "down"]
        self.choreography_index = 0
        self.last_step_time = None

    def create_ui(self):
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        box_size = min(w, h) // 6

        positions = {
            "up": (w/2 - box_size/2, h/4 - box_size/2),
            "down": (w/2 - box_size/2, 3*h/4 - box_size/2),
            "left": (w/4 - box_size/2, h/2 - box_size/2),
            "right": (3*w/4 - box_size/2, h/2 - box_size/2),
            "center": (w/2 - box_size/2, h/2 - box_size/2)
        }

        for direction, (x, y) in positions.items():
            box = self.canvas.create_rectangle(x, y, x + box_size, y + box_size,
                                               fill=MATERIAL_COLORS["box_default"], outline="")
            self.canvas.create_text(x + box_size/2, y + box_size/2,
                                    text=direction.upper(),
                                    fill=MATERIAL_COLORS["text"],
                                    font=("Helvetica", 28, "bold"))
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
        win.configure(bg=MATERIAL_COLORS["background"])
        label = tk.Label(win, text=f"Look {direction.upper()} and press ENTER",
                         font=("Helvetica", 28, "bold"),
                         bg=MATERIAL_COLORS["background"],
                         fg=MATERIAL_COLORS["highlight"])
        label.pack(padx=50, pady=80)

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
            color = MATERIAL_COLORS["box_active"] if direction == active else MATERIAL_COLORS["box_default"]
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

