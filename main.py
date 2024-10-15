import argparse

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

instructions = iter(tracking_approach.get_calibration_instructions())


def show_calibration():
    global instructions
    instr = next(instructions, None)
    if instr is not None:
        gui.set_calibration_instruction(instr)
        gui.after(1000, show_calibration)
    else:
        gui.unset_calibration_instruction()
        gui.set_main_text("Done")
        gui.after(1000, lambda: gui.set_debug_text("nice"))


show_calibration()

gui.mainloop()
gui.stop()
