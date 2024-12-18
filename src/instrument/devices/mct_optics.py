# Lens name is read/write
# Name of the camera

from pathlib import Path

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO


EPSILON = 0.1
data_path = Path(__file__).parent / "data"


class MCTOptics(Device):
    """
    Ophyd Device for controlling TXM optics via EPICS.
    """

    # Configurable PVs
    lens_select = Cpt(EpicsSignal, "LensSelect") # Use numbers 0-2
    camera_select = Cpt(EpicsSignal, "CameraSelect") # Use number 0-1
    camera_selected = Cpt(EpicsSignalRO, "CameraSelected", string="true") # Use number 0-1

    cross_select = Cpt(EpicsSignal, "CrossSelect")
    sync = Cpt(EpicsSignal, "Sync", string="true")
    cut = Cpt(EpicsSignal, "Cut", string="true")
    mct_status = Cpt(EpicsSignal, "MCTStatus", string="true")

    # Camera PVs
    # cam0_acquire_time = Cpt(EpicsSignal, "Cam0:AcquireTime")
    # cam1_acquire_time = Cpt(EpicsSignal, "Cam1:AcquireTime")

    # cam0_acquire = Cpt(EpicsSignal, "Cam0:Acquire")
    # cam1_acquire = Cpt(EpicsSignal, "Cam1:Acquire")

    # cam0_size_x = Cpt(EpicsSignal, "Cam0:SizeX")
    # cam0_size_y = Cpt(EpicsSignal, "Cam0:SizeY")
    # cam1_size_x = Cpt(EpicsSignal, "Cam1:SizeX")
    # cam1_size_y = Cpt(EpicsSignal, "Cam1:SizeY")

    # cam0_bin_x = Cpt(EpicsSignal, "Cam0:BinX")
    # cam0_bin_y = Cpt(EpicsSignal, "Cam0:BinY")
    # cam1_bin_x = Cpt(EpicsSignal, "Cam1:BinX")
    # cam1_bin_y = Cpt(EpicsSignal, "Cam1:BinY")

    # detector_pixel_size = Cpt(EpicsSignal, "DetectorPixelSize")
    # image_pixel_size = Cpt(EpicsSignal, "ImagePixelSize")



# Example initialization
optics = MCTOptics("2bm:MCTOptics:", name="optics")
