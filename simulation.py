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

def p_colour(text, code):
    return f"\033[{code}m{text}\033[0m"


def analyse_risk(micro_df: pd.DataFrame, weather_df: pd.DataFrame, temp_shaping=1.0, light_shaping=1.0, rain_shaping=1.0):
    """Return micro_df with a new 'Risk_Score' column and the recent rain sum."""

    # ---- Safety: Handle empty microbit data ----
    if micro_df is None or micro_df.empty:
        return micro_df, 0.0
    micro = micro_df.copy().reset_index(drop=True)
    
    # ---- Apply input shaping directly to dataframe ----
    micro['Temp'] = micro['Temp'] * temp_shaping
    micro['Light'] = micro['Light'] * light_shaping

    if (
        weather_df is not None
        and not weather_df.empty
        and 'rain' in weather_df.columns
    ):
        weather_df = weather_df.copy().reset_index(drop=True)
        weather_df['rain'] = pd.to_numeric(weather_df['rain'], errors='coerce').fillna(0)
        weather_df['rain'] = weather_df['rain'] * rain_shaping


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
        recent_rain = float(weather.tail(len(micro))['rain'].sum()) * rain_shaping

    # ---- Compute rolling rain modifier per row ----
    risk_scores = []
    offset = len(weather) - len(micro)

    for i in range(len(micro)):

        rain_modifier = 0.0

        if weather is not None and len(weather) > 0:

            # Use 5 previous readings relative to index
            start_idx = max(0, i - 4)
            start_idx += offset
            
            end_idx = min(i + 1, len(weather))
            end_idx += offset
            

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
            base = float(micro.at[i, 'Temp'] * 2.0) + (67 * ((float(micro.at[i, 'Light']) / 230)**3))
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


def plot_analysis(df: pd.DataFrame, rain_amount: float, title, file_name, text=""):

    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(df['Time'], df['Risk_Score'], linewidth=2, label='Risk Score', color='crimson')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Risk Index (0-100)')
    ax1.set_ylim(0, 101)
    ax1.fill_between(df['Time'], df['Risk_Score'], alpha=0.07, color="crimson")

    ax2 = ax1.twinx()
    ax2.plot(df['Time'], df['Temp'], linestyle='--', alpha=0.7, label='Temp', color="cornflowerblue")
    ax2.set_ylabel('Temp (°C)')

    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    ax3.plot(df['Time'], df['Light'], linestyle='-.', alpha=0.7, label='Light', color="yellow")
    ax3.set_ylabel('Light Level')
    ax3.set_ylim(0, 230)


    avg_risk = df['Risk_Score'].mean()
    ax1.axhline(avg_risk, linestyle=':', label='Avgerage Risk', color="darkred")

    txt = f"""
    Recent Rainfall: {rain_amount} mm.
    Avgerage Risk: {avg_risk:.2f}%.
    Avgerage Temp: {df['Temp'].mean():.2f}°C.
    Avg Light Level: {df['Light'].mean():.2f}. {text}
    """
    plt.text(.1,.1,txt)
    
    if not title:
        title = "Forest Fire Risk Analysis"
    plt.title(
        f"{title} (Recent rain: {rain_amount:.2f} mm)")
    fig.tight_layout()
    
    # Collect legend items from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()


    ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper right')


    try:
        plt.show()
    finally:
        if not file_name:
            file_name = "risk_analysis.png"
        print("Display not supported – saving graph as image instead.")
        plt.savefig(file_name, dpi=150)
        print("Saved as ", file_name)


def run_what_if(micro_df: pd.DataFrame, weather_df: pd.DataFrame):

    #
    
    print("\n\n" + "="*40)
    print(p_colour("       POSSIBLE SCENARIOS", '1;37'))  # bold white
    print("="*40)
    print(p_colour("[1]", '36'), "Variable Heatwave Impact")
    print(p_colour("[2]", '36'), "Prolonged Rain Impact")
    choice = input(p_colour("\n>> ENTER OPTION: ", '33;'))  # yellow
    
    if choice == '1':
        severity = input(p_colour(">> ENTER HEATWAVE SEVERITY (1-3): ", '33'))
        print("\n" + "="*40 + "\n")

        if severity == '1':
            df, rain = analyse_risk(micro_df, weather_df, temp_shaping=1.1, light_shaping=1.2, rain_shaping=0.5)
            print(p_colour(">> Mild Heatwave Scenario", '32'))
            print("Temperature increase: 10%\n Light increase: 20%\n  Rain reduction: 50%\n")
            text = "T +10%, L +20%, R -50%"
        elif severity == '2':
            df, rain = analyse_risk(micro_df, weather_df, temp_shaping=1.2, light_shaping=1.3, rain_shaping=0.3)
            print(p_colour(">> Moderate Heatwave Scenario", '32'))
            print("Temperature increase: 20%\n Light increase: 30%\n  Rain reduction: 70%\n")
            text = "T +20%, L +30%, R -70%"
        elif severity == '3':
            df, rain = analyse_risk(micro_df, weather_df, temp_shaping=1.3, light_shaping=1.5, rain_shaping=0.1)
            print(p_colour(">> Extreme Heatwave Scenario", '32'))
            print("Temperature increase: 30%\n Light increase: 50%\n  Rain reduction: 90%\n")
            text = "T +30%, L +50%, R -90%"
        else:
            print(">> Invalid severity.")
        plot_analysis(df, rain, "Heatwave Scenario", f"heatwave_s{severity}.png", text)

    elif choice == '2':
        print("\n" + "="*40 + "\n")
        df, rain = analyse_risk(micro_df, weather_df, temp_shaping=0.65, light_shaping=0.32, rain_shaping=1.84)
        print(p_colour(">> PROLONGED RAIN SCENARIO\n", '32'))
        print("Temperature reduction: 45%\n Light reduction: 68%\n  Rain increase: 84%\n")
        plot_analysis(df, rain, "Prolonged Rain Scenario", "prolonged_rain.png", "\nT -45%, L -68%, R +84%")

    else:
        print(">> Invalid Command.")

def load_test():
    return(p_colour(f">> SIMULATION MODULE CONNECTED...", '36'))
    