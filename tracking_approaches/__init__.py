from tracking_approaches.d_pad_tracking_approach import DPadTrackingApproach
from tracking_approaches.gaze_on_screen_tracking_approach import \
    GazeOnScreenTrackingApproach

tracking_approaches = {
    "gaze-on-screen": GazeOnScreenTrackingApproach,
    "d-pad": DPadTrackingApproach,
}
