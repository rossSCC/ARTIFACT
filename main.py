#!/usr/bin/env python3
import sys
import time
import data_manager
import simulation
import os

def p_colour(text, code):
    return f"\033[{code}m{text}\033[0m"

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

def main_menu():
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


        if choice == '1':
            df = data_manager.get_microbit_data()
            if not df.empty:
                print(df)
                data_manager.display_microbit_summary(df)
                
            input("\nPress Enter to return to menu...")
            os.system("clear||cls")

        elif choice == '2':
            weather = data_manager.get_weather_data()
            micro = data_manager.get_microbit_data()
            if micro.empty:
                input("Missing micro:bit data. Press Enter...")
                continue
            global processed, rain = simulation.analyse_risk(micro, weather)

            print("\n\n" + "="*40)
            print(p_colour("       VIEW RISK LEVEL", '1;37'))  # bold white
            print("="*40)
            print(p_colour("[1]", '36'), "Load & View Data Numericaly")
            print(p_colour("[2]", '36'), "Process Data Graphically")
            print(p_colour("[3]", '36'), "Export Data")
            choice = input(p_colour("\n>> ENTER OPTION: ", '33;'))  # yellow
            if choice == '1':
                print("\n" + str(processed))
                print(f"Recent Rainfall: {rain} mm")
            elif choice == '2':
                simulation.plot_analysis(processed, rain, "Current Risk Analysis", "risk_analysis.png")
            elif choice == '3':
                report = processed.copy()
                report['Recent_Rain'] = weather['rain'].tail(len(processed)).values
                report['Risk_Score'] = report['Risk_Score'].round(2)
                report.to_csv("risk_report.csv", index=False)
            else:
                print(">> Invalid Command.")
            input("\nPress Enter to return to menu...")
            os.system("clear||cls")

        elif choice == '3':
            weather = data_manager.get_weather_data()
            micro = data_manager.get_microbit_data()
            if micro.empty:
                input("Missing micro:bit data. Press Enter...")
                continue
            simulation.run_what_if(micro, weather)
            input("\nPress Enter to return to menu...")
            os.system("clear||cls")

        elif choice == '4':


        elif choice.upper() == 'X':
            print(p_colour(">> SHUTTING DOWN SYSTEM...", '31'))
            time.sleep(1)
            sys.exit(0)
        else:
            print(">> Invalid Command.")

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
