"""
MCT Optics Ophyd device class and instatiation
"""

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent as FCpt


class MCTOpticsLensInfo(Device):
    # Lens Names
    name_0 = Cpt(EpicsSignal, "Name0")
    name_1 = Cpt(EpicsSignal, "Name1")
    name_2 = Cpt(EpicsSignal, "Name2")

    # Lens Motor PVs
    motor_name = Cpt(EpicsSignal, "MotorPVName")
    sample_x_name = Cpt(EpicsSignal, "SampleXPVName")
    sample_y_name = Cpt(EpicsSignal, "SampleYPVName")
    sample_z_name = Cpt(EpicsSignal, "SampleZPVName")

    # Lens Focus PVs
    focus_name_0 = Cpt(EpicsSignal, "0FocusPVName")
    focus_name_1 = Cpt(EpicsSignal, "1FocusPVName")
    focus_name_2 = Cpt(EpicsSignal, "2FocusPVName")

class MCTOpticsLensOffset(Device):

    # Lens Offset
    x_offset = Cpt(EpicsSignal, "XOffset")
    y_offset = Cpt(EpicsSignal, "YOffset")
    z_offset = Cpt(EpicsSignal, "ZOffset")
    rotation = Cpt(EpicsSignal, "Rotation")
    focus = Cpt(EpicsSignal, "Focus")

class MCTOpticsLensControl(Device):

    # Lens Positions
    pos_0 = Cpt(EpicsSignal, "Pos0")
    pos_1 = Cpt(EpicsSignal, "Pos1")
    pos_2 = Cpt(EpicsSignal, "Pos2")
    lens_1 = Cpt(MCTOpticsLensOffset, "1")
    lens_2 = Cpt(MCTOpticsLensOffset, "2")

class MCTOpticsCameraControl(Device):

    def __init__(
        self,
        prefix: str,
        *args,
        **kwargs,
    ):
        # Identify the position where the trailing number starts
        split_index = len(prefix.rstrip("0123456789"))

        # Separate the base prefix and the trailing number
        self.base_prefix = prefix[:split_index]
        self.last_number = prefix[split_index:]

        super().__init__(prefix, *args, **kwargs)

    # Name
    pos = FCpt(EpicsSignal, "{base_prefix}Pos{last_number}")
    pv_name = FCpt(EpicsSignal, "{base_prefix}Name{last_number}")

    # Camera Rotation PV Name
    rotation_name = Cpt(EpicsSignal, "RotationPVName")

    # Lens Control
    lens_ctrl = Cpt(MCTOpticsLensControl, "Lens")


class MCTOptics(Device):
    """
    Ophyd Device Class for controlling MCT optics via EPICS.
    """

    # Configurable PVs
    lens_select = Cpt(EpicsSignal, "LensSelect")  # Use numbers 0-2

    camera_select = Cpt(EpicsSignal, "CameraSelect")  # Use number 0-1
    camera_selected = Cpt(EpicsSignalRO, "CameraSelected", string="true")

    cross_select = Cpt(EpicsSignal, "CrossSelect")
    sync = Cpt(EpicsSignal, "Sync", string="true")
    server_running = Cpt(EpicsSignal, "ServerRunning", string="true")
    mct_status = Cpt(EpicsSignal, "MCTStatus", string="true")

    # Scintillator Information
    scintillator_type = Cpt(EpicsSignal, "ScintillatorType")
    scintillator_thickness = Cpt(EpicsSignal, "ScintillatorThickness")

    # Image and Detector Pixel Size
    image_pixel_size = Cpt(EpicsSignal, "ImagePixelSize")
    detector_pixel_size = Cpt(EpicsSignal, "DetectorPixelSize")

    # Camera Objectives
    camera_objective = Cpt(EpicsSignal, "CameraObjective")
    camera_tube_length = Cpt(EpicsSignal, "CameraTubeLength")

    # # Lens Names
    lens_info = Cpt(MCTOpticsLensInfo, "Lens")

    # Camera Lens Positions, Offsets, & Movement
    camera_0 = Cpt(MCTOpticsCameraControl, "Camera0")
    camera_1 = Cpt(MCTOpticsCameraControl, "Camera1")

# Example initialization
optics = MCTOptics("2bm:MCTOptics:", name="optics")
