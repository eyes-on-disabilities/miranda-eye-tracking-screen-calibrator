from data_sources.mouse_data_source import MouseDataSource
from data_sources.opentrack_data_source import OpentrackDataSource
from data_sources.pupil_data_source import PupilDataSource
from guis.tkinter.main_menu_window import MainMenuOption
from misc import resource_path

data_sources: dict[MainMenuOption] = {
    "mouse": MainMenuOption(
        key="mouse",
        title="Mouse Position",
        description="Use the mouse as input. Great for testing.",
        icon=resource_path("assets/data_source_mouse.png"),
        clazz=MouseDataSource,
    ),
    "opentrack": MainMenuOption(
        key="opentrack",
        title="OpenTrack",
        description="Use the rotation of your head with OpenTrack.",
        icon=resource_path("assets/data_source_opentrack.png"),
        clazz=OpentrackDataSource,
    ),
    "pupil": MainMenuOption(
        key="pupil",
        title="Pupil",
        description="Use Pupil Lab's 3d-eye detection.",
        icon=resource_path("assets/data_source_pupil.png"),
        clazz=PupilDataSource,
    ),
}
