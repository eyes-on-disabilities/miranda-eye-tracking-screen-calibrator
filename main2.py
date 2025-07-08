import tkinter as tk
from tkinter import messagebox
from threading import Thread, Event
from typing import Optional
import time
import math
from misc import Vector  # Assumed to be something like: class Vector: def __init__(self, x: float, y: float): ...
from data_sources.pupil_data_source import PupilDataSource  # Implement this with DataSource interface

DIRECTIONS = ["left", "right", "up", "down", "center"]
THRESHOLD = 5  # Adjust as needed

class EyeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eye Tracker")
        self.calibration_data = {}
        self.datasource = PupilDataSource()
        self.running = Event()

        self.canvas = tk.Canvas(root, width=400, height=400)
        self.canvas.pack()

        self.boxes = {}
        self.create_ui()

        self.calibrate_button = tk.Button(root, text="Calibrate", command=self.start_calibration)
        self.calibrate_button.pack(pady=10)

        self.poll_thread = Thread(target=self.poll_data)
        self.poll_thread.daemon = True

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
        self.datasource.stop()
        self.datasource.start()

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

if __name__ == '__main__':
    root = tk.Tk()
    app = EyeTrackerApp(root)
    root.mainloop()
