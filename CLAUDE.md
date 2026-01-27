# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`tomo-bits` is a Bluesky instrument package for tomography data acquisition at APS (Advanced Photon Source). It provides a model implementation of a Bluesky Data Acquisition Instrument that can run in console, notebook, and queueserver modes. The package is built on the `apsbits` framework and provides tomography-specific devices, plans, and callbacks.

## Development Environment Setup

```bash
export ENV_NAME=tomo_bits
conda create -y -n $ENV_NAME python=3.11 pyepics
conda activate $ENV_NAME
pip install -e ."[all]"
```

## Essential Commands

### Testing
```bash
# Run all tests
pytest -vvv --lf ./src

# Run tests with coverage
pytest -vvv --cov=tomo_instrument ./src
```

### Code Quality
```bash
# Run linting and formatting (via pre-commit)
pre-commit run --all-files

# Manual formatting with ruff
ruff format .

# Manual linting with ruff
ruff check .
```

### Documentation
```bash
# Build documentation (requires pandoc: conda install conda-forge::pandoc)
make -C docs clean html

# View documentation
BROWSER ./docs/build/html/index.html &
```

### Running the Instrument

#### IPython Console
```python
ipython
# Inside IPython:
from tomo_instrument.startup import *
```

#### QueueServer
```bash
# Start/restart the queueserver
./qserver/qs_host.sh restart

# Launch GUI client
queue-monitor &

# Run directly (console mode)
cd ./qserver
start-re-manager --config=./qs-config.yml
```

## Architecture

### Core Structure

The package follows the apsbits instrument pattern with these key components:

1. **Startup System (`startup.py`)**: Central initialization that:
   - Loads configuration from `configs/iconfig.yml`
   - Initializes core Bluesky components (RunEngine, BestEffortCallback, Catalog)
   - Conditionally imports callbacks (NeXus, SPEC writers)
   - Creates ophyd devices from YAML configs
   - Sets up different import patterns for queueserver vs. interactive modes

2. **Configuration Cascade**:
   - `configs/iconfig.yml`: Main instrument configuration
   - `configs/devices.yml`: Device definitions (loaded for all environments)
   - `configs/devices_aps_only.yml`: APS-specific devices (loaded only on APS subnet)

3. **TomoScan Device Hierarchy**:
   - `TomoScanDevice` (base): Core EPICS PV interface for tomography scanning
   - `TomoScanPSODevice`: Adds PSO (Position Synchronized Output) fly-scan capability
   - `TomoScanHelicalDevice`: Adds helical scan support
   - `TomoScan2BMDevice`: Beamline-specific (2-BM) with dual cameras, shutters, data transfer

### Key Patterns

**Device Creation**: Uses `apsbits.core.instrument_init.make_devices()` to dynamically create ophyd devices from YAML files. This returns a plan that creates and registers devices.

**Conditional Imports**: Different import strategies for queueserver vs. interactive:
- QueueServer: Imports standard Bluesky plans by `*` to make them available
- Interactive: Uses conventional prefixes (`bp` for plans, `bps` for stubs, `*` for apstools)

**Callback System**: Data file writers (NeXus, SPEC) are conditionally enabled based on `iconfig.yml` settings and initialized with the RunEngine.

### TomoScan Plans Architecture

The `plans/tomoscan_plans.py` module provides Bluesky generator functions for tomography:
- Plans use `@bpp.stage_decorator` and `@bpp.run_decorator` for proper Bluesky protocol
- The device's `trigger()` method handles the complete scan sequence
- Plans include: basic scans, multi-sample, grid scans, time series, calibration

### Module Organization

```
src/tomo_instrument/
├── startup.py           # Main entry point for all session types
├── configs/             # YAML configuration files
├── devices/             # Ophyd device definitions
│   ├── tomoscan_base.py     # Base tomoscan ophyd Device
│   ├── tomoscan_pso.py      # PSO fly-scan extension
│   ├── tomoscan_helical.py  # Helical scan support
│   ├── tomoscan_2bm.py      # 2-BM beamline-specific
│   └── mct_optics.py        # Camera optics devices
├── plans/               # Bluesky plans
│   ├── tomoscan_plans.py    # Tomography scan plans
│   ├── sim_plans.py         # Simulation/test plans
│   └── dm_plans.py          # APS Data Management integration
├── callbacks/           # Data file writers
│   ├── nexus_data_file_writer.py
│   └── spec_data_file_writer.py
├── suspenders/          # Beam/shutter suspenders
└── utils/               # Helper utilities
```

## Code Style

- **Python Version**: 3.11+
- **Line Length**: 88 characters (ruff), 115 for black fallback
- **Import Style**: Force single-line imports (`from foo import bar`, not `from foo import (bar, baz)`)
- **Docstrings**: Required for all public modules, classes, methods, and functions (D100-D107 enforced)
- **Quote Style**: Double quotes for strings

## Testing Notes

- Tests use `pytest` with `--import-mode=importlib`
- Tests run in the `src/` directory
- `--lf` flag runs last-failed tests first
- Deprecation warnings are filtered in test configuration

## Important Implementation Details

1. **Environment Detection**: Code checks `running_in_queueserver()` and `host_on_aps_subnet()` to adapt behavior

2. **Ophyd Control Layer**: Configured via `iconfig.yml` (PyEpics or caproto), defaults to PyEpics

3. **Metadata Autosave**: RunEngine metadata is autosaved to `.re_md_dict.yml`

4. **APS Data Management**: Integration via `dm_plans.py` for workflow submission and processing job management

5. **Device Registry**: Uses `apsbits.core.instrument_init.oregistry` which is cleared before device creation in startup

6. **QueueServer Files**: The queueserver writes runtime files to `qserver/` directory - this should NOT be moved into the package as it may be in a read-only location

## Development Workflow

1. When adding new devices: Update `configs/devices.yml` or create new ophyd Device classes in `devices/`
2. When adding new plans: Add to appropriate module in `plans/` and export in `plans/__init__.py`
3. When modifying configuration: Edit `configs/iconfig.yml` and restart the session/queueserver
4. The package depends on `apsbits` as its core framework - see apsbits documentation for device creation patterns
