#!/usr/bin/env python3
import sys
import time
import data_manager
import simulation

def _color(text, code):
    return f"\033[{code}m{text}\033[0m"

def print_header():
    print(_color(r"""
                      .,,uod8B8bou,,..
              ..,uod8BBBBBBBBBBBBBBBBRPFT?l!i:.
         ,=m8BBBBBBBBBBBBBBBRPFT?!||||||||||||||
         !...:!TVBBBRPFT||||||||||!!^^""'   ||||
         !.......:!?|||||!!^^""'            ||||
         !.........||||                     ||||
         !.........||||  > LC 2026          ||||
         !.........||||  > COMPUTER SCI     ||||
         !.........||||  >                  ||||
         !.........||||  > #357528          ||||
         !.........||||                     ||||
         `.........||||                    ,||||
          .;.......||||               _.-!!|||||
   .,uodWBBBBb.....||||       _.-!!|||||||||!:'
!YBBBBBBBBBBBBBBb..!|||:..-!!|||||||!iof68BBBBBb....
!..YBBBBBBBBBBBBBBb!!||||||||!iof68BBBBBBRPFT?!::   `.
!....YBBBBBBBBBBBBBBbaaitf68BBBBBBRPFT?!:::::::::     `.
!......YBBBBBBBBBBBBBBBBBBBRPFT?!::::::;:!^"`;:::       `.
!........YBBBBBBBBBBRPFT?!::::::::::^''...::::::;         iBBbo.
`..........YBRPFT?!::::::::::::::::::::::::;iof68bo.      WBBBBbo.
  `..........:::::::::::::::::::::::;iof688888888888b.     `YBBBP^'
    `........::::::::::::::::;iof688888888888888888888b.     `
      `......:::::::::;iof688888888888888888888888888888b.
        `....:::;iof688888888888888888888888888888888899fT!
          `..::!8888888888888888888888888888888899fT|!^"'
            `' !!988888888888888888888888899fT|!^"'
                `!!8888888888888888899fT|!^"'
                  `!988888888899fT|!^"'
                    `!9899fT|!^"'
                      `!^"'
                      """, '32'))  # green

def main_menu():
    while True:
        print("\n" + "="*40)
        print(_color("       MAIN MENU", '1;37'))  # bold white
        print("="*40)
        print(_color("[1]", '36'), "Load & View Micro:bit Data")
        print(_color("[2]", '36'), "Run Fire Risk Simulation (Weather)")
        print(_color("[3]", '36'), "View 'What-If' Disaster Scenarios")
        print(_color("[4]", '36'), "Export Daily Safety Report")
        print(_color("[5]", '31'), "EXIT")

        choice = input(_color("\n>> ENTER OPTION: ", '33'))  # yellow

        if choice == '1':
            df = data_manager.get_microbit_data()
            if not df.empty:
                print(df)
            input("\nPress Enter to return to menu...")

        elif choice == '2':
            weather = data_manager.get_weather_data()
            micro = data_manager.get_microbit_data()
            if micro.empty:
                input("Missing micro:bit data. Press Enter...")
                continue
            processed, rain = simulation.analyse_risk(micro, weather)
            simulation.plot_analysis(processed, rain)
            input("\nPress Enter to return to menu...")

        elif choice == '3':
            weather = data_manager.get_weather_data()
            micro = data_manager.get_microbit_data()
            if micro.empty:
                input("Missing micro:bit data. Press Enter...")
                continue
            simulation.run_what_if(micro, weather)
            input("\nPress Enter to return to menu...")

        elif choice == '4':
            weather = data_manager.get_weather_data()
            if weather.empty:
                print(_color(">> No weather data to report on.", '31'))
                continue
            df = simulation.calculate_fire_risk_weather(weather)
            simulation.generate_report(df)
            print(_color(">> REPORT GENERATED SUCCESSFULLY.", '32'))

        elif choice == '5':
            print(_color(">> SHUTTING DOWN SYSTEM...", '31'))
            time.sleep(1)
            sys.exit(0)
        else:
            print("Invalid Command.")

if __name__ == '__main__':
    print_header()
    print(_color(">> INITIALIZING MODULES...", '33'))
    time.sleep(0.8)
    print(_color(">> SYSTEM ONLINE.", '32'))
    main_menu()
