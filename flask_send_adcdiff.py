import time
import board
import busio
import requests
import json
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1115 as ADS

# Flask endpoint on MacBook
FLASK_URL = "http://172.20.10.2:8080/submit"

# Initialize I2C and ADS1115
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    print("I2C initialized successfully")
    ads = ADS.ADS1115(i2c)
    ads.gain = 8            
    print(f"ADS1115 initialized, gain set to {ads.gain}")
except Exception as e:
    print(f"Failed to initialize I2C or ADS1115: {e}")
    exit(1)

# Define ADC channels in differential mode
chan_diff1 = AnalogIn(ads, ADS.P0, ADS.P1)  # Differential A0 - A1 (P0 - P1)
chan_diff2 = AnalogIn(ads, ADS.P2, ADS.P3)  # Differential A2 - A3 (P2 - P3)

def get_adc_values():
    """Read differential voltages from ADS1115 channels."""
    v_diff1 = chan_diff1.voltage * 1000  # A0 - A1 in mV (can be negative)
    v_diff2 = chan_diff2.voltage * 1000  # A2 - A3 in mV (can be negative)
    print(f"Gain: {ads.gain}, Raw: A0-A1={chan_diff1.value}, A2-A3={chan_diff2.value}")
    print(f"Voltage: A0-A1={v_diff1:.3f} mV, A2-A3={v_diff2:.3f} mV")
    return {"A0-A1": v_diff1, "A2-A3": v_diff2}

def send_to_flask(data):
    """Send differential ADC data to Flask."""
    payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "voltages": {
            "A0-A1": data["A0-A1"],  # Differential voltage A0 - A1
            "A2-A3": data["A2-A3"]   # Differential voltage A2 - A3
        }
    }
    try:
        response = requests.post(FLASK_URL, json=payload)
        print(f"Sent to Flask: {json.dumps(payload, indent=2)}")
        print(f"Response: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Failed to send data: {e}")

# Main loop with local file logging
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
