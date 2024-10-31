import argparse
from datetime import datetime, timedelta
from typing import Callable, Iterator, List

import numpy as np
import screeninfo

import calibration
from calibration import CalibrationInstruction, CalibrationResult
from data_sources import data_sources
from guis import guis
from guis.tkinter_gui import MainMenuGUI
from misc import Vector
from mouse_movement import MouseMovementType
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

selected_data_source = args.data_source
selected_tracking_approach = args.tracking_approach
selected_publisher = args.publisher

data_source = data_sources[selected_data_source]["class"]()
tracking_approach = tracking_approaches[selected_tracking_approach]["class"]()
publisher = publishers[selected_publisher]()
# gui = guis[args.gui]()

main_menu = MainMenuGUI()
data_source.start()
publisher.start()

gui = None


def reload_data_source(new_data_source):
    global selected_data_source, data_source, has_calibration_result
    selected_data_source = new_data_source
    if data_source is not None:
        data_source.stop()
    data_source = data_sources[selected_data_source]["class"]()
    data_source.start()

    has_calibration_result = calibration.has_result(selected_data_source, selected_tracking_approach)
    main_menu.set_has_calibration_result(has_calibration_result)
    if has_calibration_result:
        current_calibration_result = calibration.load_result(selected_data_source, selected_tracking_approach)
        tracking_approach.calibrate(current_calibration_result)


def reload_tracking_approach(new_tracking_approach):
    global selected_tracking_approach, tracking_approach, has_calibration_result
    selected_tracking_approach = new_tracking_approach
    tracking_approach = tracking_approaches[selected_tracking_approach]["class"]()

    has_calibration_result = calibration.has_result(selected_data_source, selected_tracking_approach)
    main_menu.set_has_calibration_result(has_calibration_result)
    if has_calibration_result:
        current_calibration_result = calibration.load_result(selected_data_source, selected_tracking_approach)
        tracking_approach.calibrate(current_calibration_result)


def on_calibration_requested(calibration_gui):
    global gui
    gui = calibration_gui
    execute_calibrations(iter(tracking_approach.get_calibration_instructions()), show_mouse)


main_menu.set_data_source_options(data_sources)
main_menu.set_tracking_approach_options(tracking_approaches)
main_menu.set_current_data_source(selected_data_source)
main_menu.set_current_tracking_approach(selected_tracking_approach)
main_menu.on_data_source_change_requested(reload_data_source)
main_menu.on_tracking_approach_change_requested(reload_tracking_approach)

main_menu.on_calibration_requested(on_calibration_requested)

has_calibration_result = calibration.has_result(selected_data_source, selected_tracking_approach)
main_menu.set_has_calibration_result(has_calibration_result)
if has_calibration_result:
    current_calibration_result = calibration.load_result(selected_data_source, selected_tracking_approach)
    tracking_approach.calibrate(current_calibration_result)


monitor = screeninfo.get_monitors()[0]
screen = (monitor.width, monitor.height)

mouse_position = [screen[0] / 2, screen[1] / 2]
multi = 10


def scale_to_screen(vector):
    return ((vector[0] + 1) * 0.5 * screen[0], (vector[1] - 1) * 0.5 * -screen[1])


def update_mouse_position(mouse_movement):
    global mouse_position

    if mouse_movement.type == MouseMovementType.TO_POSITION:
        mouse_position = scale_to_screen(mouse_movement.vector)
    if mouse_movement.type == MouseMovementType.BY:
        mouse_position[0] += mouse_movement.vector[0] * multi
        mouse_position[1] -= mouse_movement.vector[1] * multi
        if mouse_position[0] < 0:
            mouse_position[0] = 0
        if mouse_position[0] > screen[0]:
            mouse_position[0] = screen[0]
        if mouse_position[1] < 0:
            mouse_position[1] = 0
        if mouse_position[1] > screen[1]:
            mouse_position[1] = screen[1]


def execute_calibrations(
    calibration_instructions: Iterator,
    on_finish: Callable,
    collected_vectors: List[Vector] = [],
):
    global args, tracking_approach
    next_instruction = next(calibration_instructions, None)
    if next_instruction is None:
        gui.unset_calibration_point()
        gui.unset_main_text()
        gui.unset_image()
        result = CalibrationResult(collected_vectors)
        calibration.delete_result(selected_data_source, selected_tracking_approach)
        calibration.save_result(selected_data_source, selected_tracking_approach, result)
        tracking_approach.calibrate(result)
        main_menu.set_has_calibration_result(True)
        on_finish()
    else:
        execute_calibration(
            next_instruction,
            lambda vector: execute_calibrations(calibration_instructions, on_finish, collected_vectors + [vector]),
        )


def execute_calibration(calibration_instruction: CalibrationInstruction, on_finish: Callable[[Vector], None]):
    gui.unset_calibration_point()
    gui.unset_main_text()
    gui.unset_image()

    vector = calibration_instruction.vector
    text = calibration_instruction.text
    image = calibration_instruction.image

    if vector is not None:
        gui.set_calibration_point(scale_to_screen(vector))
    if text is not None:
        gui.set_main_text(text)
    if image is not None:
        gui.set_image(image)

    end_time = datetime.now() + timedelta(seconds=5)
    gui.after(2000, collect_calibration_vectors, calibration_instruction, on_finish, end_time)


def collect_calibration_vectors(
    calibration_instruction: CalibrationInstruction,
    on_finish: Callable[[Vector], None],
    end_time: datetime,
    vectors: List[Vector] = None,
):
    if vectors is None:
        vectors = []

    now = datetime.now()
    if now > end_time:
        on_finish(np.mean(np.array(vectors), axis=0) if len(vectors) > 0 else (0, 0))
    else:
        next_vector = data_source.get_next_vector()
        if next_vector is not None:
            vectors.append(next_vector)

        vector = calibration_instruction.vector
        text = calibration_instruction.text
        remaining_seconds = int((end_time - now).total_seconds())

        if vector is not None:
            gui.set_calibration_point(scale_to_screen(vector), str(remaining_seconds))
        elif text is not None:
            gui.set_main_text(text + f" ... {remaining_seconds}")
        else:
            gui.set_main_text(str(remaining_seconds))

        gui.after(100, collect_calibration_vectors, calibration_instruction, on_finish, end_time, vectors)


def show_mouse(entered_first_time=True):
    if entered_first_time:
        gui.set_main_text("Calibration Done. Press <ESC> or <CTRL-c> or close this window.")
    next_vector = data_source.get_next_vector()
    if next_vector is not None:
        mouse_movement = tracking_approach.get_next_mouse_movement(next_vector)
        if mouse_movement is not None:
            update_mouse_position(mouse_movement)
            gui.set_mouse_point(mouse_position)
            publisher.push(mouse_position)
    gui.after(50, show_mouse, False)


main_menu.mainloop()
data_source.stop()
publisher.stop()
