from guis.tkinter_gui import MainMenuOption
from tracking_approaches.d_pad_tracking_approach import DPadTrackingApproach
from tracking_approaches.gaze_on_screen_tracking_approach import \
    GazeOnScreenTrackingApproach

tracking_approaches: dict[MainMenuOption] = {
    "gaze-on-screen": MainMenuOption(
        key="gaze-on-screen",
        title="Gaze on Screen",
        description="Take the gaze and map it\nto the screen directly.",
        icon="assets/tracking_approach_gaze_on_screen_icon.png",
        clazz=GazeOnScreenTrackingApproach,
    ),
    "d-pad": MainMenuOption(
        key="d-pad",
        title="D-Pad",
        description='Control the "gaze" by\nlooking on a D-Pad.',
        icon="assets/tracking_approach_d_pad_icon.png",
        clazz=DPadTrackingApproach,
    ),
}
