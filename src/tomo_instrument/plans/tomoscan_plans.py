"""Bluesky plans for tomography scanning

This module provides Bluesky-compatible generator functions (plans) for
executing tomography scans using TomoScan ophyd devices.
"""

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp


def tomo_fly_scan(tomoscan_device, *, md=None):
    """Complete tomography fly scan with dark/flat fields

    This plan executes a full tomography scan including:
    - Dark field collection (if configured)
    - Flat field collection (if configured)
    - Projection collection
    - Post-scan dark/flat fields (if configured)

    The plan follows the standard Bluesky protocol of open_run/close_run
    and properly stages/unstages the device.

    Parameters
    ----------
    tomoscan_device : TomoScanDevice
        The tomoscan ophyd device to use for the scan
    md : dict, optional
        Additional metadata to include in the run

    Yields
    ------
    Msg
        Bluesky messages for the scan

    Examples
    --------
    >>> RE(tomo_fly_scan(tomo, md={'sample': 'test_sample_01'}))
    """
    _md = {
        'plan_name': 'tomo_fly_scan',
        'scan_type': 'tomography',
        'detectors': [tomoscan_device.name],
    }
    _md.update(md or {})

    @bpp.stage_decorator([tomoscan_device])
    @bpp.run_decorator(md=_md)
    def inner():
        # The device's trigger() method handles the complete scan sequence
        # including dark fields, flat fields, and projections
        yield from bps.trigger(tomoscan_device, wait=True)

    yield from inner()


def tomo_step_scan(tomoscan_device, *, md=None):
    """Tomography step scan

    Similar to tomo_fly_scan but for step-scan mode tomoscan devices.

    Parameters
    ----------
    tomoscan_device : TomoScanDevice
        The tomoscan ophyd device (must support step scanning)
    md : dict, optional
        Additional metadata

    Yields
    ------
    Msg
        Bluesky messages
    """
    _md = {
        'plan_name': 'tomo_step_scan',
        'scan_type': 'tomography_step',
        'detectors': [tomoscan_device.name],
    }
    _md.update(md or {})

    @bpp.stage_decorator([tomoscan_device])
    @bpp.run_decorator(md=_md)
    def inner():
        yield from bps.trigger(tomoscan_device, wait=True)

    yield from inner()


def tomo_multi_sample_scan(tomoscan_device, sample_positions, *, md=None):
    """Scan multiple samples at different XY positions

    This plan moves the sample stage to each position in the list and
    executes a complete tomography scan at each position.

    Parameters
    ----------
    tomoscan_device : TomoScanDevice
        The tomoscan ophyd device
    sample_positions : list of tuples
        List of (x, y, sample_name) tuples specifying:
        - x: Sample X position in mm
        - y: Sample Y position in mm
        - sample_name: String identifier for the sample
    md : dict, optional
        Additional metadata (will be updated with sample-specific info)

    Yields
    ------
    Msg
        Bluesky messages

    Examples
    --------
    >>> positions = [
    ...     (10.0, 5.0, 'sample_A'),
    ...     (15.0, 5.0, 'sample_B'),
    ...     (20.0, 5.0, 'sample_C'),
    ... ]
    >>> RE(tomo_multi_sample_scan(tomo, positions))
    """
    base_md = {
        'plan_name': 'tomo_multi_sample_scan',
        'num_samples': len(sample_positions),
    }
    base_md.update(md or {})

    for i, (x, y, sample_name) in enumerate(sample_positions):
        _md = base_md.copy()
        _md.update({
            'sample_name': sample_name,
            'sample_index': i,
            'sample_x': x,
            'sample_y': y,
        })

        # Move to sample position
        yield from bps.mv(tomoscan_device.sample_x.user_setpoint, x)
        yield from bps.mv(tomoscan_device.sample_y.user_setpoint, y)

        # Update sample name PV
        yield from bps.mv(tomoscan_device.sample_name, sample_name)

        # Run scan at this position
        yield from tomo_fly_scan(tomoscan_device, md=_md)


def tomo_grid_scan(tomoscan_device, x_start, x_num, x_step,
                   y_start, y_num, y_step, *, md=None):
    """Scan a grid of positions

    This plan creates a rectangular grid of positions and scans each one.

    Parameters
    ----------
    tomoscan_device : TomoScanDevice
        The tomoscan ophyd device
    x_start : float
        Starting X position in mm
    x_num : int
        Number of X positions
    x_step : float
        Step size in X (mm)
    y_start : float
        Starting Y position in mm
    y_num : int
        Number of Y positions
    y_step : float
        Step size in Y (mm)
    md : dict, optional
        Additional metadata

    Yields
    ------
    Msg
        Bluesky messages

    Examples
    --------
    >>> # Scan a 3x3 grid starting at (0,0) with 5mm spacing
    >>> RE(tomo_grid_scan(tomo, 0, 3, 5.0, 0, 3, 5.0))
    """
    import numpy as np

    # Generate grid positions
    x_positions = x_start + np.arange(x_num) * x_step
    y_positions = y_start + np.arange(y_num) * y_step

    sample_positions = []
    for i, y in enumerate(y_positions):
        for j, x in enumerate(x_positions):
            sample_name = f'grid_{i}_{j}'
            sample_positions.append((x, y, sample_name))

    _md = {
        'plan_name': 'tomo_grid_scan',
        'grid_shape': (y_num, x_num),
        'x_range': (x_start, x_start + (x_num - 1) * x_step),
        'y_range': (y_start, y_start + (y_num - 1) * y_step),
    }
    _md.update(md or {})

    yield from tomo_multi_sample_scan(tomoscan_device, sample_positions, md=_md)


def tomo_time_series(tomoscan_device, num_scans, delay=0, *, md=None):
    """Execute a time series of tomography scans

    This plan repeats a tomography scan multiple times with an optional
    delay between scans. Useful for in-situ experiments or studying
    time-dependent phenomena.

    Parameters
    ----------
    tomoscan_device : TomoScanDevice
        The tomoscan ophyd device
    num_scans : int
        Number of scans to execute
    delay : float, optional
        Delay time between scans in seconds (default: 0)
    md : dict, optional
        Additional metadata

    Yields
    ------
    Msg
        Bluesky messages

    Examples
    --------
    >>> # Take 10 scans with 60 second delay between each
    >>> RE(tomo_time_series(tomo, 10, delay=60))
    """
    import time

    _md = {
        'plan_name': 'tomo_time_series',
        'num_scans': num_scans,
        'inter_scan_delay': delay,
    }
    _md.update(md or {})

    for i in range(num_scans):
        scan_md = _md.copy()
        scan_md['time_series_index'] = i

        yield from tomo_fly_scan(tomoscan_device, md=scan_md)

        # Delay before next scan (except after the last one)
        if i < num_scans - 1 and delay > 0:
            yield from bps.sleep(delay)


def tomo_dark_flat_only(tomoscan_device, *, md=None):
    """Collect only dark and flat fields without projections

    This plan is useful for calibration or testing the dark/flat field
    collection without running a full scan.

    Parameters
    ----------
    tomoscan_device : TomoScanDevice
        The tomoscan ophyd device
    md : dict, optional
        Additional metadata

    Yields
    ------
    Msg
        Bluesky messages
    """
    _md = {
        'plan_name': 'tomo_dark_flat_only',
        'scan_type': 'calibration',
    }
    _md.update(md or {})

    @bpp.stage_decorator([tomoscan_device])
    @bpp.run_decorator(md=_md)
    def inner():
        # Collect dark fields
        dark_mode = tomoscan_device.dark_field_mode.get(as_string=True)
        if dark_mode in ('Start', 'Both'):
            yield from bps.mv(tomoscan_device.scan_status, 'Collecting dark fields')
            tomoscan_device.collect_dark_fields()

        # Collect flat fields
        flat_mode = tomoscan_device.flat_field_mode.get(as_string=True)
        if flat_mode in ('Start', 'Both'):
            yield from bps.mv(tomoscan_device.scan_status, 'Collecting flat fields')
            tomoscan_device.collect_flat_fields()

    yield from inner()


def tomo_scan_with_shutter_control(tomoscan_device, *, open_shutter=True,
                                   close_shutter=True, md=None):
    """Tomography scan with explicit shutter control

    This plan provides explicit control over shutter opening and closing,
    useful for beamlines where automatic shutter control needs to be
    overridden.

    Parameters
    ----------
    tomoscan_device : TomoScanDevice
        The tomoscan ophyd device
    open_shutter : bool, optional
        Whether to open shutter before scan (default: True)
    close_shutter : bool, optional
        Whether to close shutter after scan (default: True)
    md : dict, optional
        Additional metadata

    Yields
    ------
    Msg
        Bluesky messages
    """
    _md = {
        'plan_name': 'tomo_scan_with_shutter_control',
        'explicit_shutter_control': True,
    }
    _md.update(md or {})

    @bpp.run_decorator(md=_md)
    def inner():
        # Open shutter if requested
        if open_shutter:
            if hasattr(tomoscan_device, 'open_frontend_shutter'):
                tomoscan_device.open_frontend_shutter()
            else:
                open_val = tomoscan_device.open_shutter_value.get()
                yield from bps.mv(tomoscan_device.open_shutter_pv, open_val)

        # Stage and run scan
        yield from bps.stage(tomoscan_device)
        yield from bps.trigger(tomoscan_device, wait=True)
        yield from bps.unstage(tomoscan_device)

        # Close shutter if requested
        if close_shutter:
            if hasattr(tomoscan_device, 'close_frontend_shutter'):
                tomoscan_device.close_frontend_shutter()
            else:
                close_val = tomoscan_device.close_shutter_value.get()
                yield from bps.mv(tomoscan_device.close_shutter_pv, close_val)

    yield from inner()


def tomo_configuration_scan(tomoscan_device, config_file, *, md=None):
    """Load configuration and execute scan

    This plan loads scan parameters from a JSON configuration file and
    executes the scan with those settings.

    Parameters
    ----------
    tomoscan_device : TomoScanDevice
        The tomoscan ophyd device
    config_file : str
        Path to JSON configuration file
    md : dict, optional
        Additional metadata

    Yields
    ------
    Msg
        Bluesky messages
    """
    # Load configuration
    tomoscan_device.load_configuration(config_file)

    _md = {
        'plan_name': 'tomo_configuration_scan',
        'config_file': config_file,
    }
    _md.update(md or {})

    yield from tomo_fly_scan(tomoscan_device, md=_md)
