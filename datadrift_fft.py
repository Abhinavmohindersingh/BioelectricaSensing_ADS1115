import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FLASK_URL = "http://localhost:8080/submit"

def send_data_to_flask(df):
    """Send detrended data to Flask app row by row."""
    try:
        # Prepare data for Flask
        for index, row in df.iterrows():
            data = {
                "timestamp": row['Timestamp_AEST'],
                "voltages": {
                    "A0-A1": float(row['A0-A1_mV']),
                    "A2-A3": float(row['A2-A3_mV'])
                }
            }
            # Send POST request to Flask server
            response = requests.post(FLASK_URL, json=data)
            if response.status_code == 200:
                logging.info(f"Successfully sent row {index + 1}: {data}")
            else:
                logging.error(f"Failed to send row {index + 1}: {response.text}")
    except Exception as e:
        logging.error(f"Error sending data to Flask: {e}")

def apply_baseline_drift_correction(file_path, output_file_path, output_folder):
    """Load data, apply baseline drift correction, plot raw and corrected data, calculate correlation, and send to Flask."""
    try:
        logging.info("📂 Reading file: %s", file_path)
        df = pd.read_csv(file_path)

        # Ensure correct columns
        expected_columns = ['Timestamp_AEST', 'A0-A1_mV', 'A2-A3_mV']
        df = df[[col for col in expected_columns if col in df.columns]].copy()

        # Clean and preprocess
        df['A0-A1_mV'] = pd.to_numeric(df['A0-A1_mV'], errors='coerce')
        df['A2-A3_mV'] = pd.to_numeric(df['A2-A3_mV'], errors='coerce')
        df['Timestamp_AEST'] = pd.to_datetime(df['Timestamp_AEST'], errors='coerce')
        df.dropna(inplace=True)

        if df.empty:
            logging.error("❌ No valid data after preprocessing.")
            return

        # Create output folder for plots
        os.makedirs(output_folder, exist_ok=True)

        # Plot raw data
        plt.figure(figsize=(12, 6))
        plt.plot(df['Timestamp_AEST'], df['A0-A1_mV'], label='A0-A1 (Raw)', color='blue')
        plt.plot(df['Timestamp_AEST'], df['A2-A3_mV'], label='A2-A3 (Raw)', color='red')
        plt.xlabel('Time')
        plt.ylabel('mV')
        plt.title('Raw Data Before Baseline Drift Correction')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        raw_plot_path = os.path.join(output_folder, 'raw_data.png')
        plt.savefig(raw_plot_path)
        plt.close()
        logging.info("✅ Saved raw data plot: %s", raw_plot_path)

        # Apply baseline drift correction (detrending) to the entire dataset
        logging.info("🔧 Applying baseline drift correction...")
        df['A0-A1_mV'] = detrend(df['A0-A1_mV'].values)
        df['A2-A3_mV'] = detrend(df['A2-A3_mV'].values)

        # Calculate correlation between A0-A1 and A2-A3
        correlation = df['A0-A1_mV'].corr(df['A2-A3_mV'])
        logging.info("📊 Correlation between A0-A1 and A2-A3: %.4f", correlation)

        # Plot detrended data
        plt.figure(figsize=(12, 6))
        plt.plot(df['Timestamp_AEST'], df['A0-A1_mV'], label='A0-A1 (Detrended)', color='blue')
        plt.plot(df['Timestamp_AEST'], df['A2-A3_mV'], label='A2-A3 (Detrended)', color='red')
        plt.xlabel('Time')
        plt.ylabel('mV')
        plt.title(f'Data After Baseline Drift Correction (Correlation: {correlation:.4f})')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        detrended_plot_path = os.path.join(output_folder, 'detrended_data.png')
        plt.savefig(detrended_plot_path)
        plt.close()
        logging.info("✅ Saved detrended data plot: %s", detrended_plot_path)

        # Save the corrected data to a new CSV
        df.to_csv(output_file_path, index=False)
        logging.info("✅ Saved corrected data to: %s", output_file_path)

        # Send detrended data to Flask app
        logging.info("📤 Sending data to Flask app at %s...", FLASK_URL)
        send_data_to_flask(df)

    except FileNotFoundError:
        logging.error("❌ File not found: %s", file_path)
    except Exception as e:
        logging.error("❌ Error: %s", e)

if __name__ == "__main__":
    file_path = '/Users/abhinavsingh/Desktop/SEM1_2025/BIOME_Dashboard/Data_readings/gain16/differentialmode/gain4_17april_21april.csv'
    output_file_path = '/Users/abhinavsingh/Desktop/SEM1_2025/BIOME_Dashboard/Data_readings/gain16/differentialmode/gain4_17april_21april_detrended.csv'
    output_folder = 'detrend_plots'
    apply_baseline_drift_correction(file_path, output_file_path, output_folder)
