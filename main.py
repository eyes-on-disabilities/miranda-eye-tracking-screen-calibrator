import argparse
import time
import traceback
from datetime import datetime, timedelta
from threading import Thread
from typing import Callable, Iterator, List

import numpy as np
import screeninfo

import calibration
import config
from calibration import CalibrationInstruction, CalibrationResult
from data_sources import data_sources
from guis.tkinter.calibration_window import (CalibrationWindow,
                                             CalibrationWindowButton)
from guis.tkinter.main_menu_window import MainMenuWindow
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

args = parser.parse_args()

selected_data_source = None
selected_tracking_approach = None
selected_publisher = None

data_source = None
tracking_approach = None
publisher = None

running = True

calibration_result = None
temp_calibration_result = None

main_menu_window = None
calibration_window = None
in_calibration = False

request_loop_thread = None
last_data_source_vector = None
monitor = screeninfo.get_monitors()[0]
last_mouse_position = [monitor.width / 2, monitor.height / 2]


def reload_data_source(data_source_key):
    global selected_data_source, data_source
    selected_data_source = data_source_key
    if data_source is not None:
        data_source.stop()
    data_source = data_sources[selected_data_source].clazz()
    data_source.start()


def reload_tracking_approach(tracking_approach_key):
    global selected_tracking_approach, tracking_approach
    selected_tracking_approach = tracking_approach_key
    tracking_approach = tracking_approaches[selected_tracking_approach].clazz()


def reload_publisher(publisher_key):
    global selected_publisher, publisher
    selected_publisher = publisher_key
    if publisher is not None:
        publisher.stop()
    publisher = publishers[selected_publisher].clazz()
    publisher.start()


def reload_calibration_result():
    global selected_data_source, selected_tracking_approach, tracking_approach
    global calibration_result, main_menu_window, last_mouse_position
    calibration_result = None
    last_mouse_position = [monitor.width / 2, monitor.height / 2]
    if calibration.has_result(selected_data_source, selected_tracking_approach):
        calibration_result = calibration.load_result(selected_data_source, selected_tracking_approach)
        tracking_approach.calibrate(calibration_result)
    main_menu_window.set_has_calibration_result(calibration_result is not None)


def loop():
    global last_data_source_vector, last_mouse_position
    while running:
        try:
            last_data_source_vector = data_source.get_next_vector()
            main_menu_window.unset_mouse_point()
            main_menu_window.set_data_source_has_data(last_data_source_vector is not None)
            if last_data_source_vector is not None and tracking_approach.is_calibrated():
                mouse_movement = tracking_approach.get_next_mouse_movement(last_data_source_vector)
                if mouse_movement is not None:
                    last_mouse_position = get_new_mouse_position(mouse_movement, last_mouse_position)
                    if calibration_window is not None:
                        if not in_calibration:
                            calibration_window.set_mouse_point(last_mouse_position)
                    else:
                        main_menu_window.set_mouse_point(last_mouse_position)
                        publisher.push(last_mouse_position)
        except Exception:
            traceback.print_exc()
        time.sleep(config.LOOP_SLEEP_IN_MILLISEC / 1000)


def close_and_unset_calibration_window():
    global calibration_window, in_calibration
    in_calibration = False
    calibration_window.close_window()
    calibration_window = None


def accept_or_reject_temp_calibration_result(accept_temp_calibration_result: bool):
    global temp_calibration_result, calibration_result
    if accept_temp_calibration_result:
        calibration_result = temp_calibration_result
        calibration.delete_result(selected_data_source, selected_tracking_approach)
        calibration.save_result(selected_data_source, selected_tracking_approach, calibration_result)
    else:
        tracking_approach.calibrate(calibration_result)
    temp_calibration_result = None


def redo_calibration():
    if not in_calibration:
        calibration_window.unset_buttons()
        on_calibration_requested(calibration_window)


def show_final_text_for_seconds(seconds, on_finish):
    if in_calibration or calibration_window is None:  # when a calibration started somewhere else or the gui was closed
        return
    if seconds == 0:
        on_finish()
    else:
        calibration_window.set_main_text(
            "Calibration Done. Do you like this calibration?"
            + "\nEither click or look at the options below."
            + f"\nIf you don't decide, a re-calibration starts in {seconds}"
        )
        calibration_window.after(1000, show_final_text_for_seconds, seconds - 1, on_finish)


def calibration_done():
    global in_calibration
    in_calibration = False
    calibration_window.set_buttons(
        [
            CalibrationWindowButton(
                text="Keep Calibration\n(or press <Enter>)",
                func=lambda: (close_and_unset_calibration_window(), accept_or_reject_temp_calibration_result(True)),
                sequence="<Return>",
            ),
            CalibrationWindowButton(
                text='Redo Calibration\n(or press "r")',
                func=redo_calibration,
                sequence="r",
            ),
            CalibrationWindowButton(
                text="Cancel and Close\n(or press <Escape>)",
                func=lambda: (close_and_unset_calibration_window(), accept_or_reject_temp_calibration_result(False)),
                sequence="<Escape>",
            ),
        ]
    )
    show_final_text_for_seconds(config.SHOW_FINAL_CALIBRATION_TEXT_FOR_SEC, redo_calibration)


def on_calibration_requested(new_calibration_window: CalibrationWindow):
    global calibration_window, in_calibration
    calibration_window = new_calibration_window

    in_calibration = True
    calibration_window.unset_mouse_point()

    calibration_instructions = tracking_approach.get_calibration_instructions()
    show_preparational_text(
        calibration_instructions.preparational_text,
        lambda: execute_calibrations(iter(calibration_instructions.instructions), calibration_done),
    )


def show_preparational_text(preparational_text: str, on_finish: Callable, end_time=None):
    now = datetime.now()
    if end_time is None:
        end_time = now + timedelta(seconds=config.SHOW_PREP_CALIBRATION_TEXT_FOR_SEC)

    if end_time < now:
        calibration_window.unset_main_text()
        on_finish()
    else:
        remaining_seconds = int((end_time - now).total_seconds())
        calibration_window.set_main_text(
            preparational_text
            + "\nYou can close this window by pressing <Escape>."
            + f"\nInstructions come in {remaining_seconds}"
        )
        calibration_window.bind("<Escape>", lambda _: close_and_unset_calibration_window())
        calibration_window.after(250, show_preparational_text, preparational_text, on_finish, end_time)


def scale_vector_to_screen(vector):
    return ((vector[0] + 1) * 0.5 * monitor.width, (vector[1] - 1) * 0.5 * -monitor.height)


def get_new_mouse_position(mouse_movement, last_mouse_position):
    if mouse_movement.type == MouseMovementType.TO_POSITION:
        new_mouse_position = scale_vector_to_screen(mouse_movement.vector)
    if mouse_movement.type == MouseMovementType.BY:
        new_mouse_position = [
            last_mouse_position[0] + mouse_movement.vector[0] * config.MOUSE_SPEED_IN_PX,
            last_mouse_position[1] - mouse_movement.vector[1] * config.MOUSE_SPEED_IN_PX,
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
    global temp_calibration_result
    next_instruction = next(calibration_instructions, None)
    if next_instruction is None:
        calibration_window.unset_calibration_point()
        calibration_window.unset_main_text()
        calibration_window.unset_image()
        temp_calibration_result = CalibrationResult(collected_vectors)
        tracking_approach.calibrate(temp_calibration_result)
        on_finish()
    else:
        execute_calibration(
            next_instruction,
            lambda vector: execute_calibrations(calibration_instructions, on_finish, collected_vectors + [vector]),
        )


def execute_calibration(calibration_instruction: CalibrationInstruction, on_finish: Callable[[Vector], None]):
    calibration_window.unset_calibration_point()
    calibration_window.unset_main_text()
    calibration_window.unset_image()

    vector = calibration_instruction.vector
    text = calibration_instruction.text
    image = calibration_instruction.image

    if vector is not None:
        calibration_window.set_calibration_point(scale_vector_to_screen(vector))
    if text is not None:
        calibration_window.set_main_text(text)
    if image is not None:
        calibration_window.set_image(image)

    end_time = datetime.now() + timedelta(
        seconds=config.WAIT_TIME_BEFORE_COLLECTING_VECTORS_IN_SEC + config.VECTOR_COLLECTION_TIME_IN_SEC
    )
    calibration_window.after(
        config.WAIT_TIME_BEFORE_COLLECTING_VECTORS_IN_SEC * 1000,
        collect_calibration_vectors,
        calibration_instruction,
        on_finish,
        end_time,
    )


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
            calibration_window.set_calibration_point(scale_vector_to_screen(vector), str(remaining_seconds))
        elif text is not None:
            calibration_window.set_main_text(text + f" ... {remaining_seconds}")
        else:
            calibration_window.set_main_text(str(remaining_seconds))

        calibration_window.after(
            config.LOOP_SLEEP_IN_MILLISEC,
            collect_calibration_vectors,
            calibration_instruction,
            on_finish,
            end_time,
            vectors,
        )


main_menu_window = MainMenuWindow()

reload_data_source(args.data_source)
reload_tracking_approach(args.tracking_approach)
reload_publisher(args.publisher)
reload_calibration_result()

main_menu_window.set_data_source_options(data_sources)
main_menu_window.set_current_data_source(selected_data_source)
main_menu_window.on_data_source_change_requested(
    lambda new_data_source: (reload_data_source(new_data_source), reload_calibration_result())
)

main_menu_window.set_tracking_approach_options(tracking_approaches)
main_menu_window.set_current_tracking_approach(selected_tracking_approach)
main_menu_window.on_tracking_approach_change_requested(
    lambda new_tracking_approach: (reload_tracking_approach(new_tracking_approach), reload_calibration_result())
)

main_menu_window.set_publisher_options(publishers)
main_menu_window.set_current_publisher(selected_publisher)
main_menu_window.on_publisher_change_requested(reload_publisher)

main_menu_window.on_calibration_requested(on_calibration_requested)

request_loop = Thread(target=loop)
request_loop.start()

main_menu_window.mainloop()
running = False
request_loop.join(timeout=1)
data_source.stop()
publisher.stop()
