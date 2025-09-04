import tkinter as tk
from tkinter import messagebox
from threading import Thread, Event
from queue import Queue
from typing import Optional
import time
import math
import serial
import numpy as np
import sounddevice as sd
import soundfile as sf
from misc import Vector
from data_sources.mouse_data_source import MouseDataSource
from data_sources.orlosky_data_source import OrloskyDataSource
from data_sources.pupil_data_source import PupilDataSource
import sys

if len(sys.argv) < 2:
    datasource = OrloskyDataSource()
else:
    arg = sys.argv[1].lower()
    if arg == "mouse":
        datasource = MouseDataSource()
    elif arg == "pupil":
        datasource = PupilDataSource()
    else:
        datasource = OrloskyDataSource()
print("picking data source:", type(datasource).__name__)

# --- Tuning ---
DWELL_SECONDS = 3.0                 # gaze time needed to trigger final sound
LOOKAWAY_RESET_SECONDS = 0.8        # time looking away to reset dwell
NOTE_DURATION = 0.25
SUCCESS_WAIT = 0.0
DIRECTIONS = ["left", "right"]

# --- Sounds ---
TICK_SOUND = "assets/sounds/tick.wav"
FINAL_SOUNDS = {
    "right": "assets/sounds/trigger_sound_2.wav",
    "left": "assets/sounds/hunger.wav",
}

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


class EyeTrackerApp:
    def __init__(self, root, datasource):
        self.root = root
        self.datasource = datasource
        self.running = Event()
        self.calibration_x = {}  # store x-only thresholds for left/right

        self.root.title("Eye Tracker")
        self.root.configure(bg=MATERIAL_COLORS["background"])
        # self.root.attributes('-fullscreen', True)

        self.canvas = tk.Canvas(
            root,
            width=root.winfo_screenwidth(),
            height=root.winfo_screenheight(),
            bg=MATERIAL_COLORS["background"],
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.boxes = {}
        self.text_ids = {}
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

        # Audio
        self.poll_thread = Thread(target=self.poll_data, daemon=True)
        self.sound_queue = Queue()
        self.sound_thread = Thread(target=self.sound_loop, daemon=True)
        self.sound_thread.start()
        self.audio_cache = {}  # path -> (data, fs)

        # Dwell state
        self.current_target: Optional[str] = None
        self.dwell_start_time: Optional[float] = None
        self.last_tick_second: Optional[int] = None
        self.last_seen_time: Optional[float] = None

    def create_ui(self):
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        margin = 16
        bottom_reserve = 140  # leave room for calibrate button

        left_x1, left_y1 = margin, margin
        left_x2, left_y2 = w * 0.42, h - bottom_reserve - margin

        right_x1, right_y1 = w * 0.58, margin
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
        }

        labels = {"right": "Personalruf", "left": "Hunger"}

        for direction, (x1, y1, x2, y2) in layout.items():
            box = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=MATERIAL_COLORS["box_default"],
                outline="",
            )
            txt = self.canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=labels[direction],
                fill=MATERIAL_COLORS["text"],
                font=("Helvetica", 48, "bold"),
            )
            self.boxes[direction] = box
            self.text_ids[direction] = txt

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
                self.calibration_x[direction] = vec[1] if type(datasource).__name__ == "PupilDataSource" else vec[0]
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
            match = self.match_direction(vec) if vec else None
            self.update_dwell(match)
            self.update_boxes(match)
            time.sleep(0.05)

    # ---------- Dwell logic ----------
    def update_dwell(self, match: Optional[str]):
        now = time.time()
        if match is None:
            # No focus. If we were tracking, check lookaway reset.
            if self.current_target is not None and self.last_seen_time is not None:
                if now - self.last_seen_time >= LOOKAWAY_RESET_SECONDS:
                    self._reset_dwell()
            return

        if self.current_target is None:
            # Start tracking a new target
            self.current_target = match
            self.dwell_start_time = now
            self.last_tick_second = 0
            self.last_seen_time = now
            return

        if match == self.current_target:
            # Continue tracking
            self.last_seen_time = now
            elapsed = now - (self.dwell_start_time or now)
            whole = int(elapsed)
            if whole > (self.last_tick_second or 0) and whole < int(DWELL_SECONDS):
                self.play_wav(TICK_SOUND)
                self.last_tick_second = whole
            if elapsed >= DWELL_SECONDS:
                # Trigger final
                final_path = FINAL_SOUNDS.get(self.current_target)
                if final_path:
                    self.play_wav(final_path)
                self.trigger_bg_flash()
                self._reset_dwell(reset_all=True)
        else:
            # Different target than current. Treat as look away from current.
            if self.last_seen_time is not None and (now - self.last_seen_time) >= LOOKAWAY_RESET_SECONDS:
                # Switch to new target
                self.current_target = match
                self.dwell_start_time = now
                self.last_tick_second = 0
                self.last_seen_time = now
            else:
                # brief flicker, do not reset yet
                pass

    def _reset_dwell(self, reset_all: bool = False):
        self.current_target = None
        self.dwell_start_time = None
        self.last_tick_second = None
        self.last_seen_time = None
        if reset_all:
            # ensure boxes can start fresh fades
            pass

    # ---------- Visuals ----------
    def update_boxes(self, active: Optional[str]):
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
        active = MATERIAL_COLORS["box_active"]
        base = MATERIAL_COLORS["background"]
        self.canvas.configure(bg=active)
        self.root.configure(bg=active)
        self._start_bg_fade(active, base)

    # ---------- Direction match ----------
    def match_direction(self, vec: Optional[Vector]) -> Optional[str]:
        if vec is None:
            return None
        if not ("left" in self.calibration_x and "right" in self.calibration_x):
            return None
        try:
            x = vec[1] if type(datasource).__name__ == "PupilDataSource" else vec[0]
        except Exception:
            x = float(vec.x) if hasattr(vec, 'x') else None
        if x is None:
            return None
        lx = self.calibration_x["left"]
        rx = self.calibration_x["right"]
        if lx < rx:
            if x <= lx:
                return "left"
            if x >= rx:
                return "right"
        else:
            if x >= lx:
                return "left"
            if x <= rx:
                return "right"
        return None

    def toggle(self):
        ser = serial.Serial("/dev/ttyUSB0", 115200)
        ser.write(b"a")

    def ingegret(self):
        try:
            self.toggle()
            time.sleep(1.5)
            self.toggle()
        except Exception as _:
            pass

    # ---------- Audio ----------
    def play_wav(self, path: str):
        self.sound_queue.put(("wav", path))

    def play_note(self, freq, duration):
        self.sound_queue.put(("note", freq, duration))

    def sound_loop(self):
        sample_rate = 44100
        while True:
            task = self.sound_queue.get()
            kind = task[0]
            if kind == "note":
                _, freq, duration = task
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                wave = 0.5 * np.sin(2 * np.pi * freq * t)
                sd.play(wave, samplerate=sample_rate, blocking=True)
            elif kind == "wav":
                _, path = task
                data, fs = self._get_audio(path)
                if data is not None:
                    sd.play(data, samplerate=fs, blocking=True)
                    if path == "assets/sounds/trigger_sound_2.wav":
                        self.ingegret()

    def _get_audio(self, path: str):
        if path in self.audio_cache:
            return self.audio_cache[path]
        try:
            data, fs = sf.read(path, dtype="float32")
            self.audio_cache[path] = (data, fs)
            return data, fs
        except Exception:
            return None, None


if __name__ == '__main__':
    root = tk.Tk()
    datasource.start()
    app = EyeTrackerApp(root, datasource)
    root.bind('<Escape>', lambda e: root.destroy())
    root.mainloop()
    datasource.stop()
