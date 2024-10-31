from data_sources.mouse_data_source import MouseDataSource
from data_sources.opentrack_data_source import OpentrackDataSource

data_sources = {
    "mouse": {
        "key": "mouse",
        "title": "Mouse Position",
        "description": "Uses the mouse position as input.\nGreat for testing.",
        "icon": "assets/data_source_mouse_icon.png",
        "class": MouseDataSource,
    },
    "opentrack": {
        "key": "opentrack",
        "title": "OpenTrack",
        "description": "Use the rotation of your\nhead with OpenTrack.",
        "icon": "assets/data_source_opentrack_icon.png",
        "class": OpentrackDataSource,
    },
}
