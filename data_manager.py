"""
============================================================
DATA PROCESSING MODULE
============================================================

Outline:
This module is responsible for loading, validating, 
and preparing environmental data for analysis.

Design Considerations:
- Both datasets may be empty due to device failure 
  or API errors.
- The most recent reading is assumed to be stored 
  in the last row of each dataset.
- Data validation to catch missing data points
  
THIS FILE CONTAINS:
- Reading micro:bit csv data from file
- Requesting rainfall data from API
- Clean and validate datasets
- Handle missing or empty data safely
- Extract most recent readings in the case of historical API data
- Calculate statistical analysis data

This module does NOT calculate risk directly —
it prepares data for the risk algorithm.

============================================================
"""

# Imports
import pandas as pd # for storing the data as a dataframe
import urllib.request # for downloading weather data
import io # for handling the initial downloaded data
import os # for checking if the backup file exists and for clearing the screen

# Constants
STATION_ID = "9820"  # Met Éireann station ID for Mt. Lough Ouler
MET_EIREANN_URL = f"https://cli.fusio.net/cli/climate_data/webdata/dly{STATION_ID}.csv" # URL for the weather data
BACKUP_FILE = "backup_weather.csv" # Backup file for the weather data
MICROBIT_FILE = "my_data.csv" # Default microbit file for the data

# Helper function for coloured text
def p_colour(text, code):
    return f"\033[{code}m{text}\033[0m"


# Functions
# ============================================
# Load weather data from Met Éireann API
# ============================================
def get_weather_data() -> pd.DataFrame:
    #Attempt to download live weather CSV; on failure load local backup.
    #Expects the CSV to have 10 header rows, then column 'Rain'.
    
    print("\n" + "="*40)
    print(p_colour(f">> CONNECTING TO MET EIREANN STATION {STATION_ID}...", '36'))
    # Try request download using urllib
    try:
        # reach out to the API and get the response, this always comes as a csv
        with urllib.request.urlopen(MET_EIREANN_URL, timeout=8) as resp:
            raw = resp.read().decode('utf-8', errors='replace')
            print("\n" + raw[0:87])
        df = pd.read_csv(io.StringIO(raw), skiprows=9, skipinitialspace=True)
        df.columns = df.columns.str.strip().str.lower()
        # if we found a rain column then everything is ok
        if 'rain' in df.columns:
            df['rain'] = pd.to_numeric(df['rain'], errors='coerce').fillna(0)
        print(p_colour(">> [SUCCESS] LIVE RAINFALL DATA RECEIVED.", '32'))
        print(p_colour(">> Last date: ", '33') + df.iloc[-1]["date"])
        return df

    # if we fail to get the data from the API, we will try to load the backup file
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


# ============================================
# Load micro:bit data from CSV file
# ============================================
def get_microbit_data() -> pd.DataFrame:
    #Reads the local micro:bit CSV. Expects a header line followed by Time,Light,Temp columns
    print(p_colour(f">> READING LOCAL DATA ({MICROBIT_FILE})...", '36'))
    if not os.path.exists(MICROBIT_FILE):
        print(p_colour(f">> [ERROR] '{MICROBIT_FILE}' NOT FOUND.", '31'))
        return pd.DataFrame()
    try:
        df = pd.read_csv(MICROBIT_FILE, skip_blank_lines=True)
        # Normalize column names and order
        df.columns = df.columns.str.strip().str.capitalize()
        # If theres no names just go with order
        if 'Time' not in df.columns and df.shape[1] >= 1:
            df.columns.values[0] = 'Time'
        if 'Light' not in df.columns and df.shape[1] >= 2:
            df.columns.values[1] = 'Light'
        if 'Temp' not in df.columns and df.shape[1] >= 3:
            df.columns.values[2] = 'Temp'

        # some data cleaning
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
        df['Light'] = pd.to_numeric(df['Light'], errors='coerce').fillna(0)
        df['Temp'] = pd.to_numeric(df['Temp'], errors='coerce').fillna(0)
        print(p_colour(f">> [SUCCESS] LOADED {len(df)} SENSOR READINGS.\n", '32'))
        return df
    except Exception as e:
        print(p_colour(f">> [ERROR] CORRUPT DATA FILE: {e}", '31'))
        return pd.DataFrame()

# ============================================
# Display summary statistics for micro:bit data
# ============================================
def display_microbit_summary(df):
    print(p_colour("\n\n>> SENSOR DATA SUMMARY\n", '32'))

    if df.empty:
        print("No sensor data available.")
        return

    # Calculate summary statistics using average functions
    avg_temp = df["Temp"].mean()
    max_temp = df["Temp"].max()
    min_temp = df["Temp"].min()
    avg_light = df["Light"].mean()
    time_range = df["Time"].max()

    print(f"Average Temperature: {avg_temp:.2f} °C")
    print(f"Temprature Maximum: {max_temp:.2f} °C Temprature Miniumn: {min_temp:.2f} °C")
    print(f"Temperature Range: {max_temp - min_temp:.2f} °C\n")
    print(f"Average Light Level: {avg_light:.2f} out of 225\n")
    # this does presumably time is in mins since start, this would as such not apply to testing mode
    if time_range > 60:
        print(f"Total Time Recorded: {time_range/60:.2f} hours")
    else:
        print(f"Total Time Recorded: {time_range:.2f} minutes")
    print("\n\n" + "="*40 + "\n")


# ============================================
# Calculate risk analytics
# ============================================
# Helper function to classify risk levels
def classify_risk(r):
    if r >= 80:
        return "Extreme"
    elif r >= 60:
        return "High"
    elif r >= 40:
        return "Moderate"
    elif r >= 20:
        return "Low"
    else:
        return "Negligible"

# Main analytics function
def analytics(df):
    # Apply classification and calculate the number of each risk level
    df['Risk_Level'] = df['Risk_Score'].apply(classify_risk)
    distribution = df['Risk_Level'].value_counts()

    # Calculate streaks of high risk days
    max_streak = 0
    current = 0
    critical_days = 0
    for r in df['Risk_Score']:
        if r >= 70:
            current += 1
            max_streak = max(max_streak, current)
            critical_days += 1
        else:
            current = 0

    # Calculate trend
    # if the last risk score is higher than the first, the trend is increasing
    # this is a simplist way to do it, but it works for this case
    if len(df) >= 2:
        if df['Risk_Score'].iloc[-1] > df['Risk_Score'].iloc[0]:
            trend = "Increasing"
        elif df['Risk_Score'].iloc[-1] < df['Risk_Score'].iloc[0]:
            trend = "Decreasing"
        else:
            trend = "Stable"
    else:
        trend = "Insufficient Data"
    df['Risk_MA_3'] = df['Risk_Score'].rolling(window=3).mean()
    latest_ma = df['Risk_MA_3'].iloc[-1]

    volatility = df['Risk_Score'].std()

    corr_temp = df['Temp'].corr(df['Risk_Score'])
    corr_light = df['Light'].corr(df['Risk_Score'])

    return distribution, max_streak, current, trend, volatility, latest_ma, corr_temp, corr_light, critical_days


def load_test():
    return(p_colour(">> DATA MANAGER MODULE CONNECTED...", '36'))