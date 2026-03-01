"""
============================================================
SIMULATION MODULE
============================================================

Outline:
This module applies an algorithm to calculate
an environmental risk score based on:

- Temperature (micro:bit)
- Light intensity (micro:bit)
- Rainfall (weather API)

Algorithm Design:
Each variable contributes to the final risk score
using assigned weightings.

THIS FILE CONTAINS:
- Risk calculation algorithm (analyse_risk)
- Graphical display of results (plot_analysis)
- What-if scenario testing (run_what_if)

============================================================
"""

# Imports
import pandas as pd  # for storing the data as a dataframe
import matplotlib.pyplot as plt  # for graphing the data

# Helper function for coloured text
def p_colour(text, code):
    return f"\033[{code}m{text}\033[0m"

# Functions
# ============================================
# Calculate risk score
# ============================================
def analyse_risk(micro_df: pd.DataFrame, weather_df: pd.DataFrame, temp_shaping=1.0, light_shaping=1.0, rain_shaping=1.0):
    # This function takes in the microbit data and the weather data and returns the risk score and the recent rain amount

    # Handle empty microbit data
    if micro_df is None or micro_df.empty:
        return micro_df, 0.0
    micro = micro_df.copy().reset_index(drop=True)
    # Validate required columns
    if 'Temp' not in micro.columns or 'Light' not in micro.columns:
        raise ValueError(
            "Microbit data must contain 'Temp' and 'Light' columns.")
    
    # Apply input shaping as percentage directly to dataframe (for what if scenarios)
    micro['Temp'] = micro['Temp'] * temp_shaping
    micro['Light'] = micro['Light'] * light_shaping
    
    # get the rain data from the weather data
    weather = None
    if (weather_df is not None and not weather_df.empty and 'rain' in weather_df.columns):
        weather = weather_df.copy().reset_index(drop=True)
        weather['rain'] = pd.to_numeric(weather['rain'], errors='coerce').fillna(0)
        weather['rain'] = weather['rain'] * rain_shaping  # Apply rain shaping

    # ---- recent rain (last 5 overall rows/days) ----
    recent_rain = 0.0
    if weather is not None:
        recent_rain = float(weather.tail(len(micro))['rain'].sum())

    # ---- Compute rolling rain modifier per row ----
    risk_scores = []  # Store risk scores for each row
    offset = (len(weather) - len(micro)) if weather is not None else 0  # Align weather data with microbit data

    # Loop through each row in the microbit data, calculate the risk score for each row, and store it in the risk_scores list
    for i in range(len(micro)):
        rain_modifier = 0.0
        # tripple check if weather data is available
        if weather is not None and len(weather) > 0:

            # get location of 5 previous readings relative to index
            start_idx = max(offset + i - 4, 0)
            end_idx = min(offset + i + 1, len(weather))
            
            # get the 5 previous readings
            recent_weather = weather.iloc[start_idx:end_idx]
            # get the number of dry days
            dry_days = (recent_weather['rain'] < 0.5).sum()
            
            # weighted average rain, more recent = higher weight
            # I did this becasue rain 5 days ago is less relevant than rain yesterday
            rain_values = recent_weather['rain'].values
            if len(rain_values) > 0:  # Ensure there are values to calculate
                weights = list(range(1, len(rain_values) + 1))  # 1,2,3,4,5 (most recent highest)
                weighted_sum = sum(w * r for w, r in zip(weights, rain_values))  # weighted sum
                avg_rain = weighted_sum / sum(weights)  # weighted average
            else:
                avg_rain = 0.0 # fallback case     

            # Dry spell increase with an exponential curve as dry days is like a discrete variable
            if dry_days >= 5:
                rain_modifier += 20.0
            elif dry_days == 4:
                rain_modifier += 12.0
            elif dry_days == 3:
                rain_modifier += 5.0

            # Rain reduction, not using threshold here as rain is a continuous variable
            if avg_rain > 0:
                rain_modifier += (-0.025 * avg_rain**2 - 0.25 * avg_rain)

            # Debugging print statements
            #print(f"Row {i}: rain avg {avg_rain:.2f}, Rain mod {rain_modifier:.2f}, dry days {dry_days}")

        # Total risk calculation
        try:
            # Base risk score is calculated from temperature and light.
            # Temperature is multiplied by 2, so every 1° increase adds 2 points to risk.
            # Light is first scaled down by dividing by 230 (so values are between 0 and ~1), then raised to the power of 3. This means:
            # -> Low light levels add very little to risk
            # -> Medium light starts to increase risk more noticeably
            # -> Very high light increases risk sharply
            # The result is then multiplied by 67 to scale it into a meaningful range.
            # Overall:
            # Temperature increases risk in a linear way (steady increase),
            # while light increases risk in a curved way (small risk at low levels, increasing impact at high levels).
            base = float(micro.at[i, 'Temp'] * 2.0) + (67 * ((float(micro.at[i, 'Light']) / 230)**3)) # temp * 2 + (light/230)^3 * 67
        except (TypeError, ValueError):
            base = 0.0

        final = base + rain_modifier  # Add the rain modifier to the base risk score
        final = max(0.0, min(100.0, final))  # Ensure the final risk score is between 0 and 100

        risk_scores.append(final)  # Add the final risk score to the list

    micro['Risk_Score'] = risk_scores  # Add the risk scores to the microbit dataframe

    return micro, recent_rain


# ============================================
# Plot analysis graph
# ============================================
def plot_analysis(df: pd.DataFrame, rain_amount: float, title, file_name, text=""):
     # This function takes in the given data and the recent rain amount and plots the risk score, temperature, and light level over time

    plt.style.use('dark_background')  # Set the style of the plot to dark
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(df['Time'], df['Risk_Score'], linewidth=2, label='Risk Score', color='crimson') # Plot the risk score over time
    ax1.set_xlabel('Time (s)') 
    ax1.set_ylabel('Risk Index (0-100)')
    ax1.set_ylim(0, 101)  # Set the y-axis limits to 0-101 so a 100% risk is visible
    ax1.fill_between(df['Time'], df['Risk_Score'], alpha=0.07, color="crimson")  # Fill the area under the risk score line

    ax2 = ax1.twinx() # Create a second y-axis that shares the same x-axis
    ax2.plot(df['Time'], df['Temp'], linestyle='--', alpha=0.7, label='Temp', color="cornflowerblue") # Plot the temperature over time
    ax2.set_ylabel('Temp (°C)')

    ax3 = ax1.twinx()  # Create a third y-axis that shares the same x-axis
    ax3.spines["right"].set_position(("outward", 60))  # Move the third y-axis to the right
    ax3.plot(df['Time'], df['Light'], linestyle='-.', alpha=0.7, label='Light', color="yellow") # Plot the light level over time
    ax3.set_ylabel('Light Level')
    ax3.set_ylim(0, 230)


    avg_risk = df['Risk_Score'].mean()  # Calculate the average risk score
    ax1.axhline(avg_risk, linestyle=':', label='Avgerage Risk', color="darkred")  # Plot the average risk score as a horizontal line

    # Add text to the plot
    txt = f"""
    Recent Rainfall: {rain_amount:.2f} mm.
    Avgerage Risk: {avg_risk:.2f}%.
    Avgerage Temp: {df['Temp'].mean():.2f}°C.
    Avg Light Level: {df['Light'].mean():.2f}. {text}
    """
    plt.text(.1,.1,txt)

    # Set the title and show the plot, if no title is given, use the default title
    if not title:
        title = "Forest Fire Risk Analysis"
    plt.title(
        f"{title} (Recent rain: {rain_amount:.2f} mm)")
    fig.tight_layout()
    
    # Collect legend items from all axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper right')

    # Display or save the plot, i had many issues with this, so I just decided to ask the user if they want to save it
    # if the graph does not display (a system issue not code related) the user can save it as an image
    plt.show()
    print("Displaying graph...")
    choice = input(p_colour(">> Would you like to save the graph as an image? (Y/N) ", '33'))
    if choice.upper() == 'Y':
        if not file_name: # If no file name is given, use the default file name
            file_name = "risk_analysis.png"
        print("Display not supported – saving graph as image instead.")
        plt.savefig(file_name, dpi=150) # Save the plot as an image
        print("Saved as ", file_name)
    elif choice.upper() == 'N':
        print("Graph not saved.")
    else:
        print("Invalid input. Graph not saved.")


# ============================================
# Run what-if scenarios
# ============================================
def run_what_if(micro_df: pd.DataFrame, weather_df: pd.DataFrame):
    # This function takes in the microbit data and the weather data and runs the what if scenarios

    # menu for what if scenarios
    print("\n\n" + "="*40)
    print(p_colour("       POSSIBLE SCENARIOS", '1;37'))  # bold white
    print("="*40)
    print(p_colour("[1]", '36'), "Variable Heatwave Impact")
    print(p_colour("[2]", '36'), "Prolonged Rain Impact")
    choice = input(p_colour("\n>> ENTER OPTION: ", '33;'))  # yellow
    
    if choice == '1':
        severity = input(p_colour(">> ENTER HEATWAVE SEVERITY (1-3): ", '33')) # give the user a choice of severity
        print("\n" + "="*40 + "\n")

        if severity == '1':
            df, rain = analyse_risk(micro_df, weather_df, temp_shaping=1.1, light_shaping=1.2, rain_shaping=0.5)
            print(p_colour(">> Mild Heatwave Scenario", '32'))
            print("Temperature increase: 10%\night increase: 20%\nRain reduction: 50%\n")
            text = "T +10%, L +20%, R -50%"
        elif severity == '2':
            df, rain = analyse_risk(micro_df, weather_df, temp_shaping=1.2, light_shaping=1.3, rain_shaping=0.3)
            print(p_colour(">> Moderate Heatwave Scenario", '32'))
            print("Temperature increase: 20%\night increase: 30%\nRain reduction: 70%\n")
            text = "T +20%, L +30%, R -70%"
        elif severity == '3':
            df, rain = analyse_risk(micro_df, weather_df, temp_shaping=1.3, light_shaping=1.5, rain_shaping=0.1)
            print(p_colour(">> Extreme Heatwave Scenario", '32'))
            print("Temperature increase: 30%\nLight increase: 50%\nRain reduction: 90%\n")
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

# ============================================

def load_test():
    return(p_colour(">> SIMULATION MODULE CONNECTED...", '36'))
    