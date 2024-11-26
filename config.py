# meta
from misc import resource_path
APP_SHORT_NAME = "Miranda"
APP_FULL_NAME = "Miranda Eye Tracking Screen Calibrator"
APP_VERSION = "1.0.0-alpha.1"
APP_ICON_LINUX = resource_path("assets/icon.png")
APP_ICON_WINDOWS = resource_path("assets/icon.ico")
APP_DESCRIPTION = "The tool for calibrating eye and head tracker input to match your gaze on the screen."
APP_LINK_WEBSITE = "https://gaming.ifb-stiftung.de/eyes-on-disabilities-home/"
APP_LINK_CODE = "https://codeberg.org/eyes-on-disabilities/miranda-eye-tracking-screen-calibrator"

# in application
MOUSE_SPEED_IN_PX = 20
LOOP_SLEEP_IN_MILLISEC = 100
SHOW_FINAL_CALIBRATION_TEXT_FOR_SEC = 10
SHOW_PREP_CALIBRATION_TEXT_FOR_SEC = 10
WAIT_TIME_BEFORE_COLLECTING_VECTORS_IN_SEC = 3
VECTOR_COLLECTION_TIME_IN_SEC = 3
