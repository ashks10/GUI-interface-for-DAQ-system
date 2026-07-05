# GUI Interface for DAQ System

**Design and Development of a GUI for a Pulsating Sensor based Control and Data Acquisition (DAQ) System**

Developed at EIG/SISD/IGCAR, Kalpakkam.

## Overview

This project provides a PyQt5-based graphical user interface for acquiring, visualizing, and analyzing data from a pulsating (frequency-based) sensor system interfaced through an Arduino microcontroller. The GUI supports both **real-time (online) monitoring** and **offline analysis** of previously recorded sensor data, and is built for translating raw frequency signals into calibrated physical parameters (e.g. inductance, capacitance, amplitude) using configurable polynomial coefficients.

## Features

### Online Analysis
- Auto-detects and lists available serial (COM) ports, with configurable baud rate
- Live plotting of Frequency, Amplitude, or a derived Parameter vs. Time using PyQtGraph
- Configurable sampling interval and rolling plot window (in seconds)
- On-the-fly conversion of frequency readings to a physical parameter using a cubic calibration equation:
  `parameter = a·f³ + b·f² + c·f + d`, with coefficients A–D entered directly in the UI
- Start/Stop plotting control, live connection status, and current frequency readout
- Save the acquired session data to a CSV file
- Clear plot / reset session at any time

### Offline Analysis
- Browse and load previously saved CSV files
- Automatically detects the time column (supports several naming conventions)
- Two plot modes: **Frequency vs Time** and **Parameter vs Time** (auto-detects Amplitude, Inductance, or Capacitance columns and their calibration coefficients if present)
- Computes summary statistics: maximum amplitude, standard deviation, skewness, kurtosis, and average value over a fixed time window (10–12 s)
- Displays probe parameter details (parameter name, unit, and calibration coefficients) alongside the graph

### Arduino Firmware
- `Arduinothreel.ino` handles onboard signal acquisition from the pulsating sensor and streams `Frequency:` / `Amplitude:` readings over serial to the GUI

## Repository Structure
GUI-interface-for-DAQ-system/
├── GUI for pulsating sensor based DAQ system.py   # Main PyQt5 application (Online + Offline tabs)
├── Arduinothreel.ino                              # Arduino firmware for sensor signal acquisition
├── Ascending Analysis/                            # Sample data / results for ascending sensor sweep
├── Descending Analysis/                           # Sample data / results for descending sensor sweep
├── Screenshots/                                   # Application screenshots
├── Offline Analysis.png                           # Screenshot of the Offline Analysis tab
├── OnlineFreqAnalysis.png                          # Screenshot of Online Frequency vs Time view
├── OnlineLvlAnalysis.png                           # Screenshot of Online Parameter/Level view

## Requirements

- Python 3.8+
- Arduino board (interfaced over USB serial) running `Arduinothreel.ino`

### Python Dependencies

```bash
pip install PyQt5 pyqtgraph pandas numpy scipy pyserial
```

## Usage

1. **Flash the Arduino**
   Upload `Arduinothreel.ino` to your Arduino board using the Arduino IDE, and connect it to the pulsating sensor hardware.

2. **Run the GUI**
```bash
   python "GUI for pulsating sensor based DAQ system.py"
```

3. **Online Analysis tab**
   - Select the correct COM port and baud rate under **Port Settings**
   - Enter the probe's calibration parameter name, unit, and coefficients (A–D) under **Probe Parameter**
   - Set the sample time and plotting window under **Time Settings**
   - Click **Start Plotting** to begin live acquisition; use **Save as CSV** to export the session, or **Clear Plot** to reset

4. **Offline Analysis tab**
   - Click **Browse** to select a previously saved CSV file
   - Click **Start** to load the file, generate the plot, and compute statistics

## Screenshots

See the `Screenshots/` folder and the included PNGs (`OnlineFreqAnalysis.png`, `OnlineLvlAnalysis.png`, `Offline Analysis.png`) for examples of the Online and Offline analysis views.

## License
Please contact [ashks10] (https://github.com/ashks10) before reuse or redistribution.

