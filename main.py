import argparse
from datetime import datetime, timedelta
from typing import Callable, Iterator, List

import numpy as np
import screeninfo

import calibration
from calibration import CalibrationInstruction, CalibrationResult
from data_sources import data_sources
from guis import guis
from mouse_movement import MouseMovementType
from publishers import publishers
from tracking_approaches import tracking_approaches
from misc import Vector

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
data_source.start()
publisher.start()


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


def load_calibration(on_success: Callable, on_failure: Callable):
    if calibration.has_result(args.data_source, args.tracking_approach):
        tracking_approach.calibrate(calibration.load_result(args.data_source, args.tracking_approach))
        on_success()
    else:
        on_failure()


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
        calibration.save_result(args.data_source, args.tracking_approach, result)
        tracking_approach.calibrate(result)
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


def show_mouse():
    next_vector = data_source.get_next_vector()
    if next_vector is not None:
        mouse_movement = tracking_approach.get_next_mouse_movement(next_vector)
        if mouse_movement is not None:
            update_mouse_position(mouse_movement)
            gui.set_mouse_point(mouse_position)
            publisher.push(mouse_position)
    gui.after(50, show_mouse)


load_calibration(
    on_success=show_mouse,
    on_failure=lambda: execute_calibrations(iter(tracking_approach.get_calibration_instructions()), show_mouse),
)


gui.mainloop()
data_source.stop()
publisher.stop()
