# Bioelectrical Sensing using Gravity ADS1115 
Sensing Silent Signals: Electrical Characterisation of mycelial Network
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
    
## Processing Logic
1. Reading the ADC Values
   ```bash
   from adafruit_ads1x15.analog_in import AnalogIn
   import adafruit_ads1x15.ads1115 as ADS
   
   i2c = busio.I2C(board.SCL, board.SDA)
   print("I2C initialized successfully")
   ads = ADS.ADS1115(i2c)
   ads.gain = 8
               
   chan_diff1 = AnalogIn(ads, ADS.P0, ADS.P1)  # Differential A0 - A1 (P0 - P1)
   chan_diff2 = AnalogIn(ads, ADS.P2, ADS.P3)  # Differential A2 - A3 (P2 - P3)
   
   def get_adc_values():
    """Read differential voltages from ADS1115 channels."""
    v_diff1 = chan_diff1.voltage * 1000  # A0 - A1 in mV (can be negative)
    v_diff2 = chan_diff2.voltage * 1000  # A2 - A3 in mV (can be negative)
    print(f"Gain: {ads.gain}, Raw: A0-A1={chan_diff1.value}, A2-A3={chan_diff2.value}")
    print(f"Voltage: A0-A1={v_diff1:.3f} mV, A2-A3={v_diff2:.3f} mV")
    return {"A0-A1": v_diff1, "A2-A3": v_diff2}
   ```

2. Data logging logic
     ```bash
     with open("mushroom_data.txt", "a") as f:
     f.write("Timestamp,A0-A1_mV,A2-A3_mV\n")  # Header for differential data
     print("Starting ADC reading and sending to Flask... Press Ctrl+C to stop.")
     try:
        while True:
            adc_values = get_adc_values()
            # Log locally
            f.write(f"{time.time()},{adc_values['A0-A1']:.3f},{adc_values['A2-A3']:.3f}\n")
            f.flush()  # Make sure it's written to file
            # Send to Flask
            send_to_flask(adc_values)
            time.sleep(1)  # Sample every second
     except KeyboardInterrupt:
        print("Stopped recording.")
     ```
---


     
