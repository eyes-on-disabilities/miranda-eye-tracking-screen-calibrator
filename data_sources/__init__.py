from data_sources.mouse_data_source import MouseDataSource
from data_sources.opentrack_data_source import OpentrackDataSource
from misc import resource_path
from guis.tkinter.main_menu_window import MainMenuOption

data_sources: dict[MainMenuOption] = {
    "mouse": MainMenuOption(
        key="mouse",
        title="Mouse Position",
        description="Uses the mouse position as input.\nGreat for testing.",
        icon=resource_path("assets/data_source_mouse_icon.png"),
        clazz=MouseDataSource,
    ),
    "opentrack": MainMenuOption(
        key="opentrack",
        title="OpenTrack",
        description="Use the rotation of your\nhead with OpenTrack.",
        icon=resource_path("assets/data_source_opentrack_icon.png"),
        clazz=OpentrackDataSource,
    ),
}
