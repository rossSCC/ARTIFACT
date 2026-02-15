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
import random


def analyse_risk(micro_df: pd.DataFrame, weather_df: pd.DataFrame, temp_shaping=0, light_shaping=0, rain_shaping=0):
    """Return micro_df with a new 'Risk_Score' column and the recent rain sum."""

    # ---- Safety: Handle empty microbit data ----
    if micro_df is None or micro_df.empty:
        return micro_df, 0.0

    micro = micro_df.copy().reset_index(drop=True)

    if 'Temp' not in micro.columns or 'Light' not in micro.columns:
        raise ValueError(
            "Microbit data must contain 'Temp' and 'Light' columns.")

    # Prepare weather safely
    weather = None
    if (weather_df is not None and not weather_df.empty
            and 'rain' in weather_df.columns):
        weather = weather_df.copy().reset_index(drop=True)
        weather['rain'] = pd.to_numeric(weather['rain'],
                                        errors='coerce').fillna(0)

    # ---- Rolling recent rain (last 5 overall rows) ----
    recent_rain = 0.0
    if weather is not None:
        recent_rain = float(weather.tail(5)['rain'].sum()) + rain_shaping

    # ---- Compute rolling rain modifier per row ----
    risk_scores = []

    for i in range(len(micro)):

        rain_modifier = 0.0

        if weather is not None and len(weather) > 0:

            # Use 5 previous readings relative to index
            start_idx = max(0, i - 4)
            end_idx = min(i + 1, len(weather))

            recent_weather = weather.iloc[start_idx:end_idx]

            dry_days = (recent_weather['rain'] < 0.1).sum()
            avg_rain = recent_weather['rain'].mean()

            # Dry spell increase
            if dry_days >= 5:
                rain_modifier += 20.0
            elif dry_days == 4:
                rain_modifier += 12.0
            elif dry_days == 3:
                rain_modifier += 5.0

            # Rain reduction
            if avg_rain > 5.0:
                rain_modifier -= 25.0
            elif avg_rain > 1.0:
                rain_modifier -= 10.0

            #print(f"Row {i}: Rain mod {rain_modifier}")

        # ---- Base risk ----
        try:
            base = (float(micro.at[i, 'Temp'] + temp_shaping) * 2.0) + (67 * ((float(micro.at[i, 'Light'] + light_shaping) / 230)**3))
        except (TypeError, ValueError):
            base = 0.0

        final = base + rain_modifier
        final = max(0.0, min(100.0, final))

        risk_scores.append(final)

    micro['Risk_Score'] = risk_scores

    return micro, recent_rain


"""
    
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
    return micro, recent_rain"""


def plot_analysis(df: pd.DataFrame, rain_amount: float):

    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(df['Time'], df['Risk_Score'], linewidth=2, label='Risk Score')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Risk Index (0-100)')
    ax1.set_ylim(0, 100)
    ax1.fill_between(df['Time'], df['Risk_Score'], alpha=0.12)

    ax2 = ax1.twinx()
    ax2.plot(df['Time'], df['Temp'], linestyle='--', alpha=0.7, label='Temp')
    ax2.set_ylabel('Temp (°C)')

    ax1.axhline(70, linestyle=':', label='Critical Threshold')
    plt.title(
        f"Forest Sentinel: Risk Analysis (Recent rain: {rain_amount} mm)")
    fig.tight_layout()
    plt.legend()

    try:
        plt.show()
    finally:
        print("Display not supported – saving graph as image instead.")
        plt.savefig("risk_analysis.png", dpi=150)
        print("Saved as risk_analysis.png")


def run_what_if(micro_df: pd.DataFrame, weather_df: pd.DataFrame):

    #
    df, rain = analyse_risk(micro_df, weather_df)
    
    print("\n\n" + "="*40)
    print(p_colour("       POSSIBLE SCENARIOS", '1;37'))  # bold white
    print("="*40)
    print(p_colour("[1]", '36'), "Heatwave Impact")
    print(p_colour("[2]", '36'), "Drought Impact")
    choice = input(p_colour("\n>> ENTER OPTION: ", '33;'))  # yellow
    
    if choice == '1':
        
    df['Risk_Heatwave'] = ((df['Temp'] + random.randint(5,12)) * 2.0) + (df['Light'] / 4.0)
    df['Risk_Heatwave'] = df['Risk_Heatwave'].clip(0, 100)
    plt.figure(figsize=(10, 5))
    plt.plot(df['Time'], df['Risk_Score'], label='Current')
    plt.plot(df['Time'],
             df['Risk_Heatwave'],
             linestyle='--',
             label='+5°C Heatwave')
    plt.title('What-If: Heatwave Impact')
    plt.xlabel('Time (s)')
    plt.ylabel('Risk')
    plt.legend()

    try:
        plt.show()
    finally:
        print("Display not supported – saving graph as image instead.")
        plt.savefig("risk_whatif.png", dpi=150)
        print("Saved as risk_analysis.png")


# Minimal placeholders for the reporting path used by main.py
def calculate_fire_risk_weather(weather_df: pd.DataFrame):
    # For report purposes, compute a simple daily risk column in the weather df
    df = weather_df.copy()
    if 'rain' in df.columns:
        df['daily_risk'] = (
            df['rain'].apply(lambda r: 0 if r > 1 else 50)).astype(float)
    else:
        df['daily_risk'] = 50.0
    return df


def generate_report(df: pd.DataFrame, out_file='daily_report.csv'):
    # Save a short CSV summary to disk
    summary = df.head(10).copy()
    summary.to_csv(out_file, index=False)
    print(f"Report saved to {out_file}")
