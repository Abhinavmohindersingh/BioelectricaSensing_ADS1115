# BioelectricaSensing_ADS1115
Sensing Silent Signals: Electrical Characterisation of mycelial Network


# Mycellium ADC Data logger
This project uses a Raspberry Pi (or compatible board) with an ADS1115 ADC to read voltages from four analog channels, log them to a file (`mushroom.txt`), and send them to a Flask server for real-time monitoring.

## Features
- Reads voltages from ADS1115 channels A0–A3 (gain set to ±0.256V).
- Logs timestamped voltage data to `mushroom.txt`.
- Sends data to a Flask server via HTTP POST requests.
- Runs continuously, updating every second.

## Hardware Requirements
- Raspberry Pi (or any board with I2C support)
- Gravity ADS1115 ADC module
- Sensors or analog inputs connected to A0–A3
- Internet connection (for Flask server communication)

## Software Requirements
- Python 3.6+
- Libraries: `adafruit-circuitpython-ads1x15`, `requests`

## Installation
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Create a Virtual enviornment and install libraies
    ```bash
    pip install adafruit-circuitpython-ads1x15 requests
    ```
