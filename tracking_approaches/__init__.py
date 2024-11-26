from tracking_approaches.d_pad_tracking_approach import DPadTrackingApproach
from tracking_approaches.gaze_on_screen_tracking_approach import \
    GazeOnScreenTrackingApproach
from misc import resource_path
from guis.tkinter.main_menu_window import MainMenuOption

tracking_approaches: dict[MainMenuOption] = {
    "gaze-on-screen": MainMenuOption(
        key="gaze-on-screen",
        title="Gaze on Screen",
        description="Take the gaze and map it to the screen directly.",
        icon=resource_path("assets/tracking_approach_gaze_on_screen.png"),
        clazz=GazeOnScreenTrackingApproach,
    ),
    "d-pad": MainMenuOption(
        key="d-pad",
        title="D-Pad",
        description='Control the "gaze" by looking on a D-Pad.',
        icon=resource_path("assets/tracking_approach_d_pad.png"),
        clazz=DPadTrackingApproach,
    ),
}
