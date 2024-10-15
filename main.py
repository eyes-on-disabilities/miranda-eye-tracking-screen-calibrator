import argparse

import calibration
from calibration import CalibrationResult
from data_sources import data_sources
from guis import guis
from publishers import publishers
from tracking_approaches import tracking_approaches

parser = argparse.ArgumentParser()
parser.add_argument(
    "--data-source",
    help='The provider of input data. default="%(default)s"',
    choices=data_sources,
    default=next(iter(data_sources)),  # the first mentioned key
)
parser.add_argument(
    "--tracking-approach",
    type=str,
    help='The tracking approach to transform the user\'s gaze into a certain mouse movement. default="%(default)s"',
    choices=tracking_approaches,
    default=next(iter(tracking_approaches)),
)
parser.add_argument(
    "--publisher",
    help='The method for publishing the resulting vectors. default="%(default)s"',
    choices=publishers,
    default=next(iter(publishers)),
)
parser.add_argument(
    "--gui",
    help='The GUI. default="%(default)s"',
    choices=guis,
    default=next(iter(guis)),
)

args = parser.parse_args()

data_source = data_sources[args.data_source]()
tracking_approach = tracking_approaches[args.tracking_approach]()
publisher = publishers[args.publisher]()
gui = guis[args.gui]()

gui.start()


def show_mouse():
    next_vector = data_source.get_next_vector()
    if next_vector is not None:
        next_vector = tracking_approach.get_next_mouse_movement(next_vector)
        if next_vector is not None:
            gui.set_mouse_point(next_vector)
    gui.after(100, show_mouse)


def calibrate(iterator, calibration_result=None):
    if calibration_result is None:
        calibration_result = []
    else:
        calibration_result.append(data_source.get_next_vector())
    instr = next(iterator, None)
    if instr is not None:
        gui.set_calibration_instruction(instr)
        gui.after(2000, calibrate, iterator, calibration_result)
    else:
        gui.unset_calibration_instruction()
        tracking_approach.calibrate(CalibrationResult(calibration_result))
        show_mouse()


if calibration.has_result(args.data_source, args.tracking_approach):
    tracking_approach.calibrate(calibration.load_result(args.data_source, args.tracking_approach))
    show_mouse()
else:
    calibration_instructions = iter(tracking_approach.get_calibration_instructions())
    calibrate(calibration_instructions)


gui.mainloop()
gui.stop()
