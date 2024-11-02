import argparse
import time
from datetime import datetime, timedelta
from threading import Thread
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

running = True

selected_data_source = None
selected_tracking_approach = None
selected_publisher = None

data_source = None
tracking_approach = None
publisher = None

calibration_result = None

main_menu_gui = None
calibration_gui = None
in_calibration = False

request_loop_thread = None
last_data_source_vector = None
monitor = screeninfo.get_monitors()[0]
last_mouse_position = [monitor.width / 2, monitor.height / 2]
mouse_speed = 10


def reload_data_source(data_source_key):
    global selected_data_source, data_source
    selected_data_source = data_source_key
    if data_source is not None:
        data_source.stop()
    data_source = data_sources[selected_data_source]["class"]()
    data_source.start()


def reload_tracking_approach(tracking_approach_key):
    global selected_tracking_approach, tracking_approach
    selected_tracking_approach = tracking_approach_key
    tracking_approach = tracking_approaches[selected_tracking_approach]["class"]()


def reload_publisher(publisher_key):
    global selected_publisher, publisher
    selected_publisher = publisher_key
    if publisher is not None:
        publisher.stop()
    publisher = publishers[selected_publisher]["class"]()
    publisher.start()


def reload_calibration_result():
    global selected_data_source, selected_tracking_approach, tracking_approach, calibration_result, main_menu_gui
    calibration_result = None
    if calibration.has_result(selected_data_source, selected_tracking_approach):
        calibration_result = calibration.load_result(selected_data_source, selected_tracking_approach)
        tracking_approach.calibrate(calibration_result)
    main_menu_gui.set_has_calibration_result(calibration_result is not None)


def loop():
    global last_data_source_vector, last_mouse_position
    while running:
        try:
            main_menu_gui.unset_mouse_point()
            last_data_source_vector = data_source.get_next_vector()
            if main_menu_gui is not None:
                main_menu_gui.set_data_source_has_data(last_data_source_vector is not None)
            if last_data_source_vector is not None and tracking_approach.is_calibrated():
                mouse_movement = tracking_approach.get_next_mouse_movement(last_data_source_vector)
                if mouse_movement is not None:
                    last_mouse_position = get_new_mouse_position(mouse_movement, last_mouse_position)
                    main_menu_gui.set_mouse_point(last_mouse_position)
                    if calibration_gui is not None and not in_calibration:
                        calibration_gui.set_mouse_point(last_mouse_position)
                    publisher.push(last_mouse_position)
        except Exception as e:
            print(e)
        time.sleep(0.1)


def unset_calibration_gui():
    global calibration_gui
    calibration_gui = None
    in_calibration = False


def calibration_done():
    global in_calibration
    in_calibration = False
    calibration_gui.set_main_text("Calibration Done. Press <ESC> or <CTRL-c> or close this window.")


def on_calibration_requested(new_calibration_gui):
    global calibration_gui, in_calibration
    calibration_gui = new_calibration_gui
    calibration_gui.on_close(unset_calibration_gui)
    in_calibration = True
    execute_calibrations(iter(tracking_approach.get_calibration_instructions()), calibration_done)


def scale_vector_to_screen(vector):
    return ((vector[0] + 1) * 0.5 * monitor.width, (vector[1] - 1) * 0.5 * -monitor.height)


def get_new_mouse_position(mouse_movement, last_mouse_position):
    if mouse_movement.type == MouseMovementType.TO_POSITION:
        new_mouse_position = scale_vector_to_screen(mouse_movement.vector)
    if mouse_movement.type == MouseMovementType.BY:
        new_mouse_position = [
            last_mouse_position[0] + mouse_movement.vector[0] * mouse_speed,
            last_mouse_position[1] - mouse_movement.vector[1] * mouse_speed,
        ]
        if new_mouse_position[0] < 0:
            new_mouse_position[0] = 0
        if new_mouse_position[0] > monitor.width:
            new_mouse_position[0] = monitor.width
        if new_mouse_position[1] < 0:
            new_mouse_position[1] = 0
        if new_mouse_position[1] > monitor.height:
            new_mouse_position[1] = monitor.height
    return new_mouse_position


def execute_calibrations(
    calibration_instructions: Iterator,
    on_finish: Callable,
    collected_vectors: List[Vector] = [],
):
    next_instruction = next(calibration_instructions, None)
    if next_instruction is None:
        calibration_gui.unset_calibration_point()
        calibration_gui.unset_main_text()
        calibration_gui.unset_image()
        result = CalibrationResult(collected_vectors)
        calibration.delete_result(selected_data_source, selected_tracking_approach)
        calibration.save_result(selected_data_source, selected_tracking_approach, result)
        reload_calibration_result()
        on_finish()
    else:
        execute_calibration(
            next_instruction,
            lambda vector: execute_calibrations(calibration_instructions, on_finish, collected_vectors + [vector]),
        )


def execute_calibration(calibration_instruction: CalibrationInstruction, on_finish: Callable[[Vector], None]):
    calibration_gui.unset_calibration_point()
    calibration_gui.unset_main_text()
    calibration_gui.unset_image()

    vector = calibration_instruction.vector
    text = calibration_instruction.text
    image = calibration_instruction.image

    if vector is not None:
        calibration_gui.set_calibration_point(scale_vector_to_screen(vector))
    if text is not None:
        calibration_gui.set_main_text(text)
    if image is not None:
        calibration_gui.set_image(image)

    end_time = datetime.now() + timedelta(seconds=5)
    calibration_gui.after(2000, collect_calibration_vectors, calibration_instruction, on_finish, end_time)


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
        if last_data_source_vector is not None:
            vectors.append(last_data_source_vector)

        vector = calibration_instruction.vector
        text = calibration_instruction.text
        remaining_seconds = int((end_time - now).total_seconds())

        if vector is not None:
            calibration_gui.set_calibration_point(scale_vector_to_screen(vector), str(remaining_seconds))
        elif text is not None:
            calibration_gui.set_main_text(text + f" ... {remaining_seconds}")
        else:
            calibration_gui.set_main_text(str(remaining_seconds))

        calibration_gui.after(100, collect_calibration_vectors, calibration_instruction, on_finish, end_time, vectors)


main_menu_gui = MainMenuGUI()

reload_data_source(args.data_source)
reload_tracking_approach(args.tracking_approach)
reload_publisher(args.publisher)
reload_calibration_result()

main_menu_gui.set_data_source_options(data_sources)
main_menu_gui.set_current_data_source(selected_data_source)
main_menu_gui.on_data_source_change_requested(
    lambda new_data_source: (reload_data_source(new_data_source), reload_calibration_result())
)

main_menu_gui.set_tracking_approach_options(tracking_approaches)
main_menu_gui.set_current_tracking_approach(selected_tracking_approach)
main_menu_gui.on_tracking_approach_change_requested(
    lambda new_tracking_approach: (reload_tracking_approach(new_tracking_approach), reload_calibration_result())
)

main_menu_gui.set_publisher_options(publishers)
main_menu_gui.set_current_publisher(selected_publisher)
main_menu_gui.on_publisher_change_requested(reload_publisher)

main_menu_gui.on_calibration_requested(on_calibration_requested)

request_loop = Thread(target=loop)
request_loop.start()

main_menu_gui.mainloop()
running = False
request_loop.join()
data_source.stop()
publisher.stop()
