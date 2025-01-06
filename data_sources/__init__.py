from data_sources.mouse_data_source import MouseDataSource
from data_sources.opentrack_data_source import OpentrackDataSource
from data_sources.pupil_data_source import PupilDataSource
from guis.tkinter.main_menu_window import MainMenuOption
from misc import resource_path
from data_sources.eyetrackvr_data_source import EyeTrackVRDataSource
from data_sources.opentrack_and_pupil_data_source import OpentrackAndPupilDataSource

data_sources: dict[MainMenuOption] = {
    "opentrack_and_pupil": MainMenuOption(
        key="opentrack_and_pupil",
        title="OpenTrack and Pupil",
        description="Test.",
        icon=resource_path("assets/data_source_opentrack.png"),
        clazz=OpentrackAndPupilDataSource,
    ),
    "mouse": MainMenuOption(
        key="mouse",
        title="Mouse Position",
        description="The mouse position as input. Great for testing.",
        icon=resource_path("assets/data_source_mouse.png"),
        clazz=MouseDataSource,
    ),
    "opentrack": MainMenuOption(
        key="opentrack",
        title="OpenTrack",
        description="The rotation of your head with OpenTrack.",
        icon=resource_path("assets/data_source_opentrack.png"),
        clazz=OpentrackDataSource,
    ),
    "pupil": MainMenuOption(
        key="pupil",
        title="Pupil",
        description="Pupil Lab's 3d-eye detection.",
        icon=resource_path("assets/data_source_pupil.png"),
        clazz=PupilDataSource,
    ),
    "eyetrackvr": MainMenuOption(
        key="eyetrackvr",
        title="EyeTrackVR",
        description="Eye tracking with EyeTrackVR.",
        icon=resource_path("assets/data_source_eyetrackvr.png"),
        clazz=EyeTrackVRDataSource,
    ),
}
