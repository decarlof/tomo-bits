"""
Ophyd device class and instatiation
"""

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO


class MCTOptics(Device):
    """
    Ophyd Device Class for controlling MCT optics via EPICS.
    """

    # Configurable PVs
    lens_select = Cpt(EpicsSignal, "LensSelect")  # Use numbers 0-2
    camera_select = Cpt(EpicsSignal, "CameraSelect")  # Use number 0-1
    camera_selected = Cpt(
        EpicsSignalRO, "CameraSelected", string="true"
    )  # Use number 0-1

    cross_select = Cpt(EpicsSignal, "CrossSelect")
    sync = Cpt(EpicsSignal, "Sync", string="true")

    # Camera Positions and Names
    camera_pos_0 = Cpt(EpicsSignalRO, "CameraPos0")
    camera_pos_1 = Cpt(EpicsSignalRO, "CameraPos1")
    camera_name_0 = Cpt(EpicsSignalRO, "CameraName0")
    camera_name_1 = Cpt(EpicsSignalRO, "CameraName1")

    # Lens Names
    lens_name_0 = Cpt(EpicsSignal, "LensName0")  # Lens name is read/write
    lens_name_1 = Cpt(EpicsSignal, "LensName1")
    lens_name_2 = Cpt(EpicsSignal, "LensName2")

    # Lens Motor PVs
    lens_motor = Cpt(EpicsSignal, "LensMotorPVName")
    lens_sample_x = Cpt(EpicsSignal, "LensSampleXPVName")
    lens_sample_y = Cpt(EpicsSignal, "LensSampleYPVName")
    lens_sample_z = Cpt(EpicsSignal, "LensSampleZPVName")

    # Lens Focus PVs
    lens_0_focus = Cpt(EpicsSignal, "Lens0FocusPVName")
    lens_1_focus = Cpt(EpicsSignal, "Lens1FocusPVName")
    lens_2_focus = Cpt(EpicsSignal, "Lens2FocusPVName")

    # Camera Rotation
    camera_0_rotation = Cpt(EpicsSignal, "Camera0RotationPVName")
    camera_1_rotation = Cpt(EpicsSignal, "Camera1RotationPVName")

    # Camera Lens Positions
    camera_0_lens_pos_0 = Cpt(EpicsSignal, "Camera0LensPos0")
    camera_0_lens_pos_1 = Cpt(EpicsSignal, "Camera0LensPos1")
    camera_0_lens_pos_2 = Cpt(EpicsSignal, "Camera0LensPos2")

    camera_1_lens_pos_0 = Cpt(EpicsSignal, "Camera1LensPos0")
    camera_1_lens_pos_1 = Cpt(EpicsSignal, "Camera1LensPos1")
    camera_1_lens_pos_2 = Cpt(EpicsSignal, "Camera1LensPos2")

    # Camera Lens Offsets
    camera_0_lens_1_x_offset = Cpt(EpicsSignal, "Camera0Lens1XOffset")
    camera_0_lens_1_y_offset = Cpt(EpicsSignal, "Camera0Lens1YOffset")
    camera_0_lens_1_z_offset = Cpt(EpicsSignal, "Camera0Lens1ZOffset")

    camera_1_lens_1_x_offset = Cpt(EpicsSignal, "Camera1Lens1XOffset")
    camera_1_lens_1_y_offset = Cpt(EpicsSignal, "Camera1Lens1YOffset")
    camera_1_lens_1_z_offset = Cpt(EpicsSignal, "Camera1Lens1ZOffset")

    # Scintillator Information
    scintillator_type = Cpt(EpicsSignal, "ScintillatorType")
    scintillator_thickness = Cpt(EpicsSignal, "ScintillatorThickness")

    # Image and Detector Pixel Size
    image_pixel_size = Cpt(EpicsSignal, "ImagePixelSize")
    detector_pixel_size = Cpt(EpicsSignal, "DetectorPixelSize")

    # Camera Objectives
    camera_objective = Cpt(EpicsSignal, "CameraObjective")
    camera_tube_length = Cpt(EpicsSignal, "CameraTubeLength")

    # Camera Names
    camera_0_name = Cpt(EpicsSignal, "Camera0Name")
    camera_1_name = Cpt(EpicsSignal, "Camera1Name")


# Example initialization
optics = MCTOptics("2bm:MCTOptics:", name="optics")
