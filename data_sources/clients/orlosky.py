import os
import threading
import time
import tkinter.filedialog as fd
from typing import Dict, Optional


class Orlosky:
    def __init__(self):
        self._data_lock = threading.Lock()
        self._latest_data: Optional[Dict[str, float]] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._tracker_path: Optional[str] = None
        self._path_cache_file = os.path.join(os.getcwd(), ".orlosky_tracker_path")

    def start(self):
        if not self._select_valid_directory():
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()

    def get_last_data(self) -> Optional[Dict[str, float]]:
        with self._data_lock:
            return self._latest_data.copy() if self._latest_data else None

    def _select_valid_directory(self) -> bool:
        # Try reading cached path first
        if os.path.exists(self._path_cache_file):
            try:
                with open(self._path_cache_file, "r") as f:
                    cached_path = f.read().strip()
                if os.path.isdir(os.path.join(cached_path, "3DTracker")):
                    self._tracker_path = cached_path
                    return True
                else:
                    os.remove(self._path_cache_file)  # Invalid path, remove cache
            except Exception:
                pass  # Fail silently and fall back to UI

        # Fallback: ask user via file dialog
        while True:
            selected_path = fd.askdirectory(title="Select git repo of JEOresearch/EyeTracker")
            if not selected_path:
                return False
            if os.path.isdir(os.path.join(selected_path, "3DTracker")):
                self._tracker_path = selected_path
                try:
                    with open(self._path_cache_file, "w") as f:
                        f.write(selected_path)
                except Exception:
                    pass  # Don't crash on write failure
                return True

    def _run_loop(self):
        gaze_file = os.path.join(self._tracker_path, "3DTracker", "gaze_vector.txt")
        while self._running:
            try:
                if os.path.exists(gaze_file):
                    with open(gaze_file, "r") as f:
                        line = f.read().strip()
                        if line:
                            parts = [float(p) for p in line.split(",")]
                            if len(parts) >= 6:
                                x, y, z = parts[3], parts[4], parts[5]
                                with self._data_lock:
                                    self._latest_data = {"x": x, "y": y, "z": z}
            except Exception:
                pass
            time.sleep(0.05)

