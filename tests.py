"""
============================================================
AUTOMATED TESTS FOR FOREST FIRE PROJECT
============================================================

File: tests.py
Purpose: Unit tests for data_manager and simulation modules,
         plus utility functions for API backup and formula visualization.

============================================================
"""

import pandas as pd
import io

# Import your modules
import data_manager
import simulation
import matplotlib.pyplot as plt

#============================================================
# TEST DATA
#============================================================

MICROBIT_CSV = """time,light,temp
0.20338,65,20
0.49595,52,15
1,47,18
"""

WEATHER_CSV = """date,rain
2026-02-16,0.0
2026-02-17,0.5
2026-02-18,0.2
"""

#============================================================
# HELPER FUNCTIONS FOR TESTING
#============================================================

def make_microbit_df():
    return pd.read_csv(io.StringIO(MICROBIT_CSV))

def make_weather_df():
    return pd.read_csv(io.StringIO(WEATHER_CSV))

#============================================================
# TEST CASES
#============================================================

#============================================================
# NON-TEST UTILITY FUNCTIONS
#============================================================



def plot_risk_formulas():
    """
    Plot risk formula as function of Temperature, Light, and Rain individually.
    Related variables (e.g., Temp+Light) on same figure.
    """
    import numpy as np

    temps = np.linspace(0, 50, 50)
    lights = np.linspace(0, 230, 50)
    rains = np.linspace(0, 5, 50)

    fig, ax = plt.subplots(figsize=(10,6))

    # Risk vs Temperature (light=50, rain=0)
    risk_temp = temps*2 + 67*(50/230)**3
    ax.plot(temps, risk_temp, label="Risk vs Temp", color="red")

    # Risk vs Light (temp=20, rain=0)
    risk_light = 20*2 + 67*(lights/230)**3
    ax.plot(lights, risk_light, label="Risk vs Light", color="yellow")

    # Risk vs Rain (temp=20, light=50), using rain_modifier simplified: -0.025*r^2 - 0.25*r
    risk_rain = 20*2 + 67*(50/230)**3 + (-0.025*rains**2 - 0.25*rains)
    ax.plot(rains, risk_rain, label="Risk vs Rain", color="blue")

    ax.set_xlabel("Variable Value")
    ax.set_ylabel("Risk Score")
    ax.set_title("Forest Fire Risk Formula Variations")
    ax.legend()
    plt.tight_layout()
    plt.savefig("risk_formula_plot.png")
    plt.close()
    print("Risk formula plot saved as 'risk_formula_plot.png'")

#============================================================
# RUN TESTS
#============================================================