"""
============================================================
PROGRAM OVERVIEW
============================================================

Project Title:
Leaving Cery Forest Fire Risk Artifact

Purpose:
This program integrates micro:bit sensor readings 
(temperature and light intensity) with rainfall 
data retrieved from Met Éireann weather API.

System Workflow:
1. Import auxiliary modules (data_manager, simulation)
2. Display main menu with options:
   - Load micro:bit data
   - Run fire risk simulation
   - View what-if scenarios
   - View risk analytics
3. On user input load micro:bit sensor data from CSV file
4. Retrieve rainfall data from weather API
5. Validate that both datasets contain usable data
6. Extract the most recent readings (rain)
7. Do weighted risk calculation algorithm
8. Display or graph the calculated risk score

THIS FILE CONTAINS:
- Main menu interface
- Program entry point
- Numerical data display (NOT graphical)

============================================================
"""

# Imports
import sys # for exit()
import time # for sleep(), technically used as a cosmetic delay
import data_manager # for loading and processing data
import simulation # for calculating risk, graphing results
import os # for clearing the screen

# Global variable to store processed data, reduces need for repeated calculations
data = None

# Helper function for coloured text
def p_colour(text, code):
    return f"\033[{code}m{text}\033[0m"

# ASCII art header
def print_header():
    print(p_colour("""
⠀⠀⠀⠀⠀⠀⢱⣆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⣿⣷⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣧⠀⠀⠀    > FOREST FIRE RISK SYSTEM
⠀⠀⠀⠀⡀⢠⣿⡟⣿⣿⣿⡇⠀⠀  
⠀⠀⠀⠀⣳⣼⣿⡏⢸⣿⣿⣿⢀⠀    > LC 2026 COMPUTER SCI
⠀⠀⠀⣰⣿⣿⡿⠁⢸⣿⣿⡟⣼⡆    > #357528
⢰⢀⣾⣿⣿⠟⠀⠀⣾⢿⣿⣿⣿⣿
⢸⣿⣿⣿⡏⠀⠀⠀⠃⠸⣿⣿⣿⡿
⢳⣿⣿⣿⠀⠀⠀⠀⠀⠀⢹⣿⡿⡁
⠀⠹⣿⣿⡄⠀⠀⠀⠀⠀⢠⣿⡞⠁
⠀⠀⠈⠛⢿⣄⠀⠀⠀⣠⠞⠋⠀⠀
⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀\n""", '1;31'))

#============================
# Main menu function loop
#============================
def main_menu():

    # remind python that we are taking about global data vairable, py var internal thing
    global data
    
    while True:
        print("\n\n" + "="*40)
        print(p_colour("       MAIN MENU", '1;37'))  # bold white
        print("="*40)
        print(p_colour("[1]", '36'), "Load & View Micro:bit Data")
        print(p_colour("[2]", '36'), "Run Fire Risk Simulation (Weather)")
        print(p_colour("[3]", '36'), "View 'What-If' Disaster Scenarios")
        print(p_colour("[4]", '36'), "View Risk Analytics")
        print(p_colour("[X]", '31'), "EXIT")

        choice = input(p_colour("\n>> ENTER OPTION: ", '33'))  # yellow
        print("\n" + "="*40 + "\n")

        # Option 1: Load and display micro:bit data
        if choice == '1':
            #get data from data_manager
            df = data_manager.get_microbit_data()
            #chech there is actually data from the microbit to summarise
            if not df.empty:
                print(df)
                data_manager.display_microbit_summary(df)
                
            input("\nPress Enter to return to menu...")
            os.system("clear||cls")

        # Option 2: Run fire risk simulation
        elif choice == '2':
            #get data from data_manager
            weather = data_manager.get_weather_data()
            micro = data_manager.get_microbit_data()
            if micro.empty:
                input("Missing micro:bit data. Press Enter...")
                continue
            # call analyse_risk from simulation.py with the data we got from data_manager
            processed, rain = simulation.analyse_risk(micro, weather)
            # store the processed data in the global variable
            data = processed

            print("\n\n" + "="*40)
            print(p_colour("       VIEW RISK LEVEL", '1;37'))  # bold white
            print("="*40)
            print(p_colour("[1]", '36'), "Load & View Data Numericaly")
            print(p_colour("[2]", '36'), "Process Data Graphically")
            print(p_colour("[3]", '36'), "Export Data")
            choice = input(p_colour("\n>> ENTER OPTION: ", '33;'))  # yellow
            # option 1: just print the processed data
            if choice == '1':
                print("\n" + str(processed))
                print(f"Recent Rainfall: {rain} mm")
            # option 2: plot the processed data
            elif choice == '2':
                simulation.plot_analysis(processed, rain, "Current Risk Analysis", "risk_analysis.png")
            # option 3: export the processed data to a csv file
            elif choice == '3':
                report = processed.copy()
                report['Recent_Rain'] = weather['rain'].tail(len(processed)).values
                report['Risk_Score'] = report['Risk_Score'].round(2)
                report.to_csv("risk_report.csv", index=False)
            # error handling
            else:
                print(">> Invalid Command.")
            input("\nPress Enter to return to menu...")
            os.system("clear||cls")

        # Option 3: View what-if scenarios
        elif choice == '3':
            weather = data_manager.get_weather_data()
            micro = data_manager.get_microbit_data()
            if micro.empty:
                input("Missing micro:bit data. Press Enter...")
                continue
            # hand off to simulation.py for what if scenarios
            simulation.run_what_if(micro, weather)
            
            input("\nPress Enter to return to menu...")
            os.system("clear||cls")

        # Option 4: View detailed analytics
        elif choice == '4':
            # get the data we previously stored in the global variable
            if data is not None and not data.empty:
                micro = data
            else:
                # could make this get the data if its not already loaded
                # but i like the idea of making the user to run the simulation first
                print(p_colour(">> [ERROR] NO DATA AVAILABLE.", '31'))
                print(p_colour(">> Please run simulation first. (Option 2)", '31'))
                input("\nPress Enter to return to menu...")
                os.system("clear||cls")
                continue

            # call analytics from data_manager
            distribution, max_streak, current, trend, volatility, latest_ma, corr_temp, corr_light, critical_days = data_manager.analytics(micro)

            print("\n\n" + "="*40)
            print(p_colour("       DATA ANALYSIS ", '1;37'))  # bold white
            print("="*40 + "\n")
            # risk is categorized into 5 levels -> Categorical analysis
            print(p_colour(">> RISK LEVEL DISTRIBUTION", '32'))
            print("Catagory   : Count")
            total = len(micro)
            # Define levels and their colours
            levels = [
                ("Extreme", '31'),
                ("High", '33'),
                ("Moderate", '33'),
                ("Low", '32'),
                ("Negligible", '36')
            ]
            # Loop through levels
            for name, color in levels:
                count = distribution.get(name, 0)
                percent = (count / total) * 100 if total > 0 else 0
                bar_length = int((percent / 100) * 20)
                # Create a bar graph for the percentage of total days
                bar = '█' * bar_length + '-' * (20 - bar_length)
                print(p_colour(f"{name:<10} : {count:>3}  ({percent:5.1f}%) {bar}", color))

            # Sequential analysis
            print("\n" + p_colour(">> RISK STREAK", '32'))
            print(f"Current High Risk Streak: {current} days")
            print(f"Longest High Risk Streak: {max_streak} days")
            print(p_colour(f"Total High Risk Days (>70%): {critical_days} days", '1;31'))

            # Trend analysis
            print("\n" + p_colour(">> RISK TREND", '32'))
            print(f"Overall Risk Trend: {trend}")
            print(f"3-Day Moving Average: {latest_ma:.2f}%")
            print(f"Risk Volatility (Std Dev): {volatility:.2f}%")

            # Correlation analysis using Pearson's correlation coefficient (its a built in function ¯⁠\⁠_⁠(⁠ツ⁠)⁠_⁠/⁠¯ )
            print("\n" + p_colour(">> CORRELATIONS", '32'))
            print("How strongly risk relates to other factors")
            print("Measured on a scale of -1 to 1 (-1 = no correlation, 1 = perfectly correlated)")
            print(f"Temperature Correlation: {corr_temp:.2f}")
            print(f"Light Level Correlation: {corr_light:.2f}")

            input("\nPress Enter to return to menu...")
            os.system("clear||cls")

        # Option X: Exit program
        elif choice.upper() == 'X':
            print(p_colour(">> SHUTTING DOWN SYSTEM...", '31'))
            time.sleep(1)
            sys.exit(0)
        # Error handling
        else:
            os.system("clear||cls")
            print(p_colour(">> INVALID COMMAND.", '31'))

#============================
# Program entry point
#============================
if __name__ == '__main__':
    print(p_colour(">> INITIALIZING MODULES...", '33'))
    time.sleep(0.5)
    print(data_manager.load_test())
    time.sleep(0.3)
    print(simulation.load_test())
    time.sleep(0.8)
    print(p_colour(">> SYSTEM ONLINE.", '32'))
    time.sleep(1)
    os.system("clear||cls")
    print_header()
    main_menu()
