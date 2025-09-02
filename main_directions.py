import tkinter as tk
from tkinter import messagebox
from threading import Thread, Event
from queue import Queue
from typing import Optional
import time
import math
import numpy as np
import sounddevice as sd
import soundfile as sf
from misc import Vector
from data_sources.mouse_data_source import MouseDataSource

# --- Tuning ---
THRESHOLD = 250
STEP_TIMEOUT = 2.0
NOTE_DURATION = 0.25
SUCCESS_WAIT = 0.0
CHOREO_NOTES = [261.63, 329.63, 392.00, 523.25]
DIRECTIONS = ["left", "right", "up", "down"]
TRIGGER_SOUND = "assets/trigger_sound.wav"
BG_FLASH_FACTOR = 1

# --- Animation controls ---
FADE_STEPS = 12           # frames for box color fade-out
BG_FADE_STEPS = 120       # frames for background fade-out
FADE_INTERVAL_MS = 16     # ms per fade frame

MATERIAL_COLORS = {
    "background": "#121212",
    "button": "#1F1B24",
    "button_active": "#3700B3",
    "text": "#FFFFFF",
    "highlight": "#03DAC6",
    "box_default": "#2C2C2C",
    "box_active": "#03DAC6"
}

# --- Color helpers ---
def _hex_to_rgb(h: str):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def _blend_hex(base_hex: str, target_hex: str, alpha: float) -> str:
    br, bg, bb = _hex_to_rgb(base_hex)
    tr, tg, tb = _hex_to_rgb(target_hex)
    mix = (
        int(br + (tr - br) * alpha),
        int(bg + (tg - bg) * alpha),
        int(bb + (tb - bb) * alpha),
    )
    return _rgb_to_hex(mix)


class EyeTrackerApp:
    def __init__(self, root, datasource):
        self.root = root
        self.datasource = datasource
        self.running = Event()
        self.calibration_data = {}

        self.root.title("Eye Tracker")
        self.root.configure(bg=MATERIAL_COLORS["background"])
        self.root.attributes('-fullscreen', True)

        self.canvas = tk.Canvas(
            root,
            width=root.winfo_screenwidth(),
            height=root.winfo_screenheight(),
            bg=MATERIAL_COLORS["background"],
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.boxes = {}
        self.fade_jobs = {}
        self.bg_fade_job = None
        self.create_ui()

        self.calibrate_button = tk.Button(
            root,
            text="CALIBRATE",
            command=self.start_calibration,
            font=("Helvetica", 24, "bold"),
            bg=MATERIAL_COLORS["button"],
            fg=MATERIAL_COLORS["text"],
            activebackground=MATERIAL_COLORS["button_active"],
            activeforeground=MATERIAL_COLORS["highlight"],
            relief="flat",
            padx=20,
            pady=10,
        )
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
        margin = 16
        bottom_reserve = 140  # leave room for calibrate button

        left_x1, left_y1 = margin, margin
        left_x2, left_y2 = w * 0.22, h - bottom_reserve - margin

        right_x1, right_y1 = w * 0.78, margin
        right_x2, right_y2 = w - margin, h - bottom_reserve - margin

        center_x1 = left_x2 + margin
        center_x2 = right_x1 - margin

        center_top_y1 = margin
        center_top_y2 = (h - bottom_reserve - 2 * margin) / 2
        center_bottom_y1 = center_top_y2 + margin
        center_bottom_y2 = h - bottom_reserve - margin

        layout = {
            "left": (left_x1, left_y1, left_x2, left_y2),
            "right": (right_x1, right_y1, right_x2, right_y2),
            "up": (center_x1, center_top_y1, center_x2, center_top_y2),
            "down": (center_x1, center_bottom_y1, center_x2, center_bottom_y2),
        }

        for direction, (x1, y1, x2, y2) in layout.items():
            box = self.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=MATERIAL_COLORS["box_default"],
                outline="",
            )

            self.canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=direction.upper(),
                fill=MATERIAL_COLORS["text"],
                font=("Helvetica", 48, "bold"),
            )

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
        label = tk.Label(
            win,
            text=f"Look {direction.upper()} and press ENTER",
            font=("Helvetica", 28, "bold"),
            bg=MATERIAL_COLORS["background"],
            fg=MATERIAL_COLORS["highlight"],
        )
        label.pack(padx=50, pady=80)

        def on_enter(_event):
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
            else:
                # no vector -> fade everything
                self.update_boxes(None)
            time.sleep(0.05)

    def update_boxes(self, active: Optional[str]):
        # Active box gets immediate active color. Others fade to default.
        for direction, box in self.boxes.items():
            if active is not None and direction == active:
                job = self.fade_jobs.pop(direction, None)
                if job:
                    self.root.after_cancel(job)
                self.canvas.itemconfig(box, fill=MATERIAL_COLORS["box_active"]) 
            else:
                current = self.canvas.itemcget(box, "fill")
                if not current or current[0] != '#':
                    current = MATERIAL_COLORS["box_default"]
                target = MATERIAL_COLORS["box_default"]
                if current != target:
                    self._start_fade(direction, current, target)

    def _start_fade(self, direction: str, start_hex: str, end_hex: str):
        job = self.fade_jobs.pop(direction, None)
        if job:
            self.root.after_cancel(job)
        if start_hex == end_hex:
            return
        box = self.boxes[direction]
        start_rgb = _hex_to_rgb(start_hex)
        end_rgb = _hex_to_rgb(end_hex)

        def step(i: int = 0):
            if i >= FADE_STEPS:
                self.canvas.itemconfig(box, fill=end_hex)
                self.fade_jobs.pop(direction, None)
                return
            t = i / float(FADE_STEPS)
            rgb = tuple(int(start_rgb[k] + (end_rgb[k] - start_rgb[k]) * t) for k in range(3))
            self.canvas.itemconfig(box, fill=_rgb_to_hex(rgb))
            self.fade_jobs[direction] = self.root.after(FADE_INTERVAL_MS, step, i + 1)

        step()

    def _start_bg_fade(self, start_hex: str, end_hex: str):
        if self.bg_fade_job is not None:
            self.root.after_cancel(self.bg_fade_job)
            self.bg_fade_job = None
        start_rgb = _hex_to_rgb(start_hex)
        end_rgb = _hex_to_rgb(end_hex)

        def step(i: int = 0):
            if i >= BG_FADE_STEPS:
                self.canvas.configure(bg=end_hex)
                self.root.configure(bg=end_hex)
                self.bg_fade_job = None
                return
            t = i / float(BG_FADE_STEPS)
            rgb = tuple(int(start_rgb[k] + (end_rgb[k] - start_rgb[k]) * t) for k in range(3))
            hexcol = _rgb_to_hex(rgb)
            self.canvas.configure(bg=hexcol)
            self.root.configure(bg=hexcol)
            self.bg_fade_job = self.root.after(FADE_INTERVAL_MS, step, i + 1)

        step()

    def trigger_bg_flash(self):
        base = MATERIAL_COLORS["background"]
        active = MATERIAL_COLORS["box_active"]
        flash = _blend_hex(base, active, BG_FLASH_FACTOR)
        self.canvas.configure(bg=flash)
        self.root.configure(bg=flash)
        self._start_bg_fade(flash, base)

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
                data, fs = sf.read(TRIGGER_SOUND, dtype="float32")
                sd.play(data, samplerate=fs, blocking=True)

    def handle_choreography(self, match):
        if match is None:
            self.update_boxes(None)
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
                    self.trigger_bg_flash()
            elif current_time - self.last_step_time > STEP_TIMEOUT:
                self.choreography_index = 0
                self.last_step_time = None

        self.update_boxes(match)


if __name__ == '__main__':
    root = tk.Tk()
    datasource = MouseDataSource()
    datasource.start()
    app = EyeTrackerApp(root, datasource)
    root.mainloop()
    datasource.stop()
