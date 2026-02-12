"""
Simplified data_manager module.
Replaces external 'requests' and 'termcolor' with standard-library code where possible.
Keeps the same CSV parsing behavior (skip 10 header rows for weather CSV).
"""

import pandas as pd
import urllib.request
import io
import os

STATION_ID = "9820"
MET_EIREANN_URL = f"https://cli.fusio.net/cli/climate_data/webdata/dly{STATION_ID}.csv"
BACKUP_FILE = "backup_weather.csv"
MICROBIT_FILE = "my_data.csv"

def p_colour(text, code):
    return f"\033[{code}m{text}\033[0m"

def get_weather_data() -> pd.DataFrame:
    #Attempt to download live weather CSV; on failure load local backup.
    #Expects the CSV to have 10 header rows, then column 'Rain'.
    
    print("\n" + "="*40)
    print(p_colour(f">> CONNECTING TO MET EIREANN STATION {STATION_ID}...", '36'))
    # Try live download using urllib
    try:
        with urllib.request.urlopen(MET_EIREANN_URL, timeout=8) as resp:
            raw = resp.read().decode('utf-8', errors='replace')
        df = pd.read_csv(io.StringIO(raw), skiprows=10, skipinitialspace=True)
        df.columns = df.columns.str.strip().str.lower()
        if 'rain' in df.columns:
            df['rain'] = pd.to_numeric(df['rain'], errors='coerce').fillna(0)
        print(p_colour(">> [SUCCESS] LIVE RAINFALL DATA RECEIVED.", '32'))
        return df
    except Exception as err:
        print(p_colour(f">> [WARNING] CONNECTION FAILED: {err}", '33'))
        print(p_colour(">> [SYSTEM] LOADING LOCAL BACKUP...", '31'))
        if os.path.exists(BACKUP_FILE):
            try:
                df = pd.read_csv(BACKUP_FILE, skiprows=10, skipinitialspace=True)
                df.columns = df.columns.str.strip().str.lower()
                if 'rain' in df.columns:
                    df['rain'] = pd.to_numeric(df['rain'], errors='coerce').fillna(0)
                return df
            except Exception as e2:
                print(p_colour(f">> [ERROR] FAILED TO READ BACKUP: {e2}", '31'))
                return pd.DataFrame()
        else:
            print(p_colour(">> [ERROR] NO BACKUP FILE FOUND.", '31'))
            return pd.DataFrame()

def get_microbit_data() -> pd.DataFrame:
    #Reads the local micro:bit CSV. Expects a header line followed by Time,Light,Temp columns
    print(p_colour(f">> READING LOCAL DATA ({MICROBIT_FILE})...", '36'))
    if not os.path.exists(MICROBIT_FILE):
        print(p_colour(f">> [ERROR] '{MICROBIT_FILE}' NOT FOUND.", '31'))
        return pd.DataFrame()
    try:
        df = pd.read_csv(MICROBIT_FILE, skip_blank_lines=True)
        # Normalize column names and ensure numeric types
        df.columns = df.columns.str.strip().str.capitalize()
        # Accept various column name possibilities
        if 'Time' not in df.columns and df.shape[1] >= 1:
            df.columns.values[0] = 'Time'
        if 'Light' not in df.columns and df.shape[1] >= 2:
            df.columns.values[1] = 'Light'
        if 'Temp' not in df.columns and df.shape[1] >= 3:
            df.columns.values[2] = 'Temp'

        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
        df['Light'] = pd.to_numeric(df['Light'], errors='coerce').fillna(0)
        df['Temp'] = pd.to_numeric(df['Temp'], errors='coerce').fillna(0)
        print(p_colour(f">> [SUCCESS] LOADED {len(df)} SENSOR READINGS.\n", '32'))
        return df
    except Exception as e:
        print(p_colour(f">> [ERROR] CORRUPT DATA FILE: {e}", '31'))
        return pd.DataFrame()


def display_microbit_summary(df):
    print(p_colour("\n\n>> SENSOR DATA SUMMARY\n", '32'))

    if df.empty:
        print("No sensor data available.")
        return

    avg_temp = df["Temp"].mean()
    max_temp = df["Temp"].max()
    min_temp = df["Temp"].min()
    avg_light = df["Light"].mean()
    time_range = df["Time"].max()

    print(f"Average Temperature: {avg_temp:.2f} °C")
    print(f"Temprature Maximum: {max_temp:.2f} °C Temprature Miniumn: {min_temp:.2f} °C")
    print(f"Temperature Range: {max_temp - min_temp:.2f} °C\n")
    print(f"Average Light Level: {avg_light:.2f} out of 225\n")
    if time_range > 60:
        print(f"Total Time Recorded: {time_range/60:.2f} hours")
    else:
        print(f"Total Time Recorded: {time_range:.2f} minutes")
    print("\n\n" + "="*40 + "\n")