# Miranda – The Eye Tracking Screen Calibrator

Miranda is a GUI tool for calibrating eye and head tracker input to match your screen gaze. It enables seamless integration with other applications, allowing you to use your calibrated tracker data in various ways.

For example, you can use Opentrack as an input source, calibrate your head rotation to your screen, and output the data as UDP messages. This enables you to control applications like OptiKey with your head movements.

## Run Miranda

Install Python >=3.12.6 and Pip. Then load the dependencies and run `main.py`:
```
pip install -r requirements.txt
python main.py
```

## Concepts

In short, data comes from a _data source_, this data will be translated into mouse movements using a _tracking approach_, and these mouse movements will be _published_ for further usage. Every data source and tracking approach combination needs a calibration first.

### Data Source
A _data source_ is where eye and head tracking data comes from. The data could be the yaw and pitch rotation of your eyes in degrees. The data source is mostly a different application, that needs to run alongside Miranda. Since the data itself gives no indication of where the user is looking at or how the mouse cursor shall be moved, we need a _tracking approach_.

### Tracking Approach
A _tracking approach_ tells how the data from the data source shall be translated into a mouse movement. There are two approaches:

- **Gaze on Screen**: The user is directly looking at the screen. The cursor shall follow the gaze. This is the most straight-forward and probably mostly used approach.
- **D-Pad**: This approach is a good alternative if your input device is not accurate enough for the _Gaze on Screen_ approach. Usually, a D-pad is a flat, typically thumb-operated, directional control. Likewise with this approach the cursor is looking at a d-pad to steer the cursor. E.g. by looking at the "up" arrow, the cursor moves up.

### Calibration
Before we can translate the data from the data source into mouse movements, we need to do a calibration first. Every data source and tracking approach combination needs its own calibration. Once such a calibration is done the result will be stored and is available on the next start of Miranda.

### Publishers
_Publishers_ take the mouse movements created by the tracking approach and publish them for further usage of other applications. Currently there is just the _UDP-Publisher_, which publishes the mouse coordinates via UDP to 127.0.0.1 port 9999 in the following format:
```
# example
{"x": 173, "y": 432, "timestamp": "2024-11-14 00:56:42.308879"}
```
