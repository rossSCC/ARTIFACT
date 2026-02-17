# replit.md

## Overview

This is a **Forest Fire Risk System** built in Python for an LC 2026 Computer Science project (#357528). The application analyzes fire risk by combining micro:bit sensor data (temperature and light) with live rainfall data from Met Éireann weather stations. It provides risk scoring, "what-if" disaster scenario simulations, and risk analytics through a terminal-based menu interface.

The project is currently **incomplete/in-progress** — several menu options reference functions that aren't fully implemented yet, and the simulation module's `analyse_risk` function is truncated.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure

The project follows a simple modular Python architecture with three main files:

- **`main.py`** — Entry point with a terminal-based menu system (options 1-4 plus exit). Handles user interaction and delegates to other modules. Uses ANSI color codes for styled terminal output.
- **`data_manager.py`** — Responsible for fetching and loading data from two sources: Met Éireann weather CSV (live download with local backup fallback) and micro:bit sensor CSV.
- **`simulation.py`** — Contains risk analysis logic combining micro:bit sensor readings with weather data, plus matplotlib-based visualization. Computes a `Risk_Score` column from temperature, light, and rainfall inputs with configurable shaping multipliers.

### Data Flow

1. **Weather data**: Downloaded live from Met Éireann's CSV endpoint (`https://cli.fusio.net/cli/climate_data/webdata/dly9820.csv`) using `urllib`. Falls back to a local `backup_weather.csv` file if the network request fails. The CSV has 9-10 header rows that get skipped during parsing.
2. **Micro:bit data**: Read from a local CSV file (`my_data.csv`) containing at minimum `Temp` and `Light` columns.
3. **Risk analysis**: Combines both data sources with shaping multipliers for temperature, light, and rain to produce a risk score per reading.

### Key Design Decisions

- **No external HTTP library**: Uses `urllib.request` from the standard library instead of `requests` to minimize dependencies.
- **No external color library**: Uses raw ANSI escape codes via a `p_colour()` helper function (defined in both `main.py` and `data_manager.py`) instead of `termcolor`.
- **Pandas for data processing**: All CSV parsing and data manipulation uses pandas DataFrames.
- **Matplotlib for visualization**: Charts and plots use matplotlib (`simulation.py`).
- **Graceful degradation**: Weather data loading has a try/except pattern that falls back to a local backup file when the network is unavailable.

### Incomplete Features

- `main.py` menu options 2, 3, and 4 are not fully wired up (the code is cut off after option 1).
- `data_manager.get_microbit_data()` and `data_manager.display_microbit_summary()` are referenced but not defined in the provided `data_manager.py`.
- `simulation.analyse_risk()` is incomplete — the risk score calculation logic is missing.
- `simulation.plot_analysis()` and `simulation.run_what_if()` are referenced in docstrings but not implemented.

When completing these features, maintain the existing patterns: pandas DataFrames for data, ANSI colors for terminal output, and matplotlib for plots.

## External Dependencies

### Python Packages
- **pandas** — Core data manipulation and CSV parsing
- **matplotlib** — Data visualization and plotting
- **urllib** (stdlib) — HTTP requests to Met Éireann API
- **io** (stdlib) — String-based CSV stream handling
- **os** (stdlib) — File existence checks for backup data

### External Data Sources
- **Met Éireann Climate Data API** — Station 9820 daily weather CSV at `https://cli.fusio.net/cli/climate_data/webdata/dly9820.csv`. Provides rainfall data among other weather metrics. CSV format has ~10 metadata header rows before the actual column headers.
- **Micro:bit sensor data** — Local CSV file (`my_data.csv`) with temperature and light sensor readings, presumably exported from a BBC micro:bit device.

### Local Data Files
- `backup_weather.csv` — Offline fallback copy of Met Éireann weather data (10 header rows to skip)
- `my_data.csv` — Micro:bit sensor readings