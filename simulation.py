"""
Simplified simulation module.
Keeps core functionality:
 - analyze_hybrid_risk: produce Risk_Score based on Temp, Light and recent rain
 - plot_analysis: show a matplotlib figure
 - run_what_if: create a heatwave scenario plot
Additional helper functions for reporting are kept minimal.
"""

import pandas as pd
import matplotlib.pyplot as plt

def analyse_risk(micro_df: pd.DataFrame, weather_df: pd.DataFrame):
    """Return micro_df with a new 'Risk_Score' column and the recent rain sum."""
    # Use last 30 rows (approx 30 days in original)
    recent_rain = 0.0
    if weather_df is not None and not weather_df.empty and 'rain' in weather_df.columns:
        recent_rain = float(weather_df.tail(30)['rain'].sum())

    # Determine modifier
    if recent_rain > 5.0:
        rain_mod = -40.0
    elif recent_rain > 0.5:
        rain_mod = -20.0
    else:
        rain_mod = 0.0

    # Compute risk for each row
    def compute_row_risk(temp, light):
        base = (float(temp) * 2.0) + (float(light) / 4.0)
        final = base + rain_mod
        return max(0.0, min(100.0, final))

    micro = micro_df.copy()
    micro['Risk_Score'] = micro.apply(lambda r: compute_row_risk(r.get('Temp', 0), r.get('Light', 0)), axis=1)
    return micro, recent_rain

def plot_analysis(df: pd.DataFrame, rain_amount: float):
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(10,5))
    ax1.plot(df['Time'], df['Risk_Score'], linewidth=2, label='Risk Score')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Risk Index (0-100)')
    ax1.set_ylim(0,100)
    ax1.fill_between(df['Time'], df['Risk_Score'], alpha=0.12)

    ax2 = ax1.twinx()
    ax2.plot(df['Time'], df['Temp'], linestyle='--', alpha=0.7, label='Temp')
    ax2.set_ylabel('Temp (°C)')

    ax1.axhline(70, linestyle=':', label='Critical Threshold')
    plt.title(f"Forest Sentinel: Risk Analysis (Recent rain: {rain_amount} mm)")
    fig.tight_layout()
    
    print("Display not supported – saving graph as image instead.")
    plt.savefig("risk_analysis.png", dpi=150)
    print("Saved as risk_analysis.png")


def run_what_if(micro_df: pd.DataFrame, weather_df: pd.DataFrame):
    df, rain = analyse_risk(micro_df, weather_df)
    df['Risk_Heatwave'] = ((df['Temp'] + 5.0) * 2.0) + (df['Light'] / 4.0)
    df['Risk_Heatwave'] = df['Risk_Heatwave'].clip(0,100)
    plt.figure(figsize=(10,5))
    plt.plot(df['Time'], df['Risk_Score'], label='Current')
    plt.plot(df['Time'], df['Risk_Heatwave'], linestyle='--', label='+5°C Heatwave')
    plt.title('What-If: Heatwave Impact')
    plt.xlabel('Time (s)')
    plt.ylabel('Risk')
    plt.legend()
    print("Display not supported – saving graph as image instead.")
    plt.savefig("risk_whatif.png", dpi=150)
    print("Saved as risk_analysis.png")

# Minimal placeholders for the reporting path used by main.py
def calculate_fire_risk_weather(weather_df: pd.DataFrame):
    # For report purposes, compute a simple daily risk column in the weather df
    df = weather_df.copy()
    if 'rain' in df.columns:
        df['daily_risk'] = (df['rain'].apply(lambda r: 0 if r>1 else 50)).astype(float)
    else:
        df['daily_risk'] = 50.0
    return df

def generate_report(df: pd.DataFrame, out_file='daily_report.csv'):
    # Save a short CSV summary to disk
    summary = df.head(10).copy()
    summary.to_csv(out_file, index=False)
    print(f"Report saved to {out_file}")
