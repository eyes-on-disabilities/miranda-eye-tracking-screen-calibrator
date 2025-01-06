from typing import Optional

import numpy as np

from data_sources.clients.opentrack import Opentrack
from data_sources.clients.pupil import Pupil
from data_sources.data_source import DataSource
from misc import Vector


class OpentrackAndPupilDataSource(DataSource):

    def __init__(self):
        self.opentrack = Opentrack()
        self.pupil = Pupil()

    def start(self):
        self.opentrack.start()
        self.pupil.start()

    def stop(self):
        self.opentrack.stop()
        self.pupil.stop()

    def get_next_vector(self) -> Optional[Vector]:
        """
        example data:
        head:
        {'x': -1.5079885326367384, 'y': 6.658496056673861, 'z': 114.1457147374053, 'yaw': -3.694162298337043, 'pitch': 15.147858993968914, 'roll': 1.7161668507331909}
        eye:
        {
          "norm_pos": [0.6230617370365481, 0.449595459323777],
          "sphere": {
            "center": [6.7109385469479275, 1.6606580627008913, 67.99231785358006],
            "radius": 10.392304845413264
          },
          "projected_sphere": {
            "center": [417.25137406222336, 264.1373773194449],
            "axes": [359.1299569911837, 359.1299569911837],
            "angle": 0.0
          },
          "circle_3d": {
            "center": [4.671217960276486, 1.4050545057383488, 57.80535526652906],
            "normal": [
              -0.19627220496439637, -0.024595463736358302, -0.9802409319764236
            ],
            "radius": 2.1060521273894866
          },
          "diameter_3d": 4.212104254778973,
          "ellipse": {
            "center": [398.7595117033908, 264.19417952458707],
            "axes": [82.42911034745876, 82.73431891534082],
            "angle": 167.54346135904302
          },
          "location": [398.7595117033908, 264.19417952458707],
          "model_confidence": 1.0,
          "theta": 1.5953942709902191,
          "phi": -1.76841162139929
        }
        """

        eye = self.pupil.get_last_data()
        head = self.opentrack.get_last_data()

        if eye["3d"] is not None:
            eye_yaw = eye["3d"]["phi"]
            eye_pitch = eye["3d"]["theta"]
            print("eye", eye_yaw, eye_pitch)

        if head is not None:
            head_yaw = head["yaw"] * np.pi / 180.0
            head_pitch = head["pitch"] * np.pi / 180.0
            print("head", head_yaw, head_pitch)

        return (head_yaw - eye_yaw, -head_pitch - eye_pitch) if eye["3d"] and head else None
