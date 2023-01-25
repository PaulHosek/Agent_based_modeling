import os

os.environ['USE_PYGEOS'] = '0'
from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from geo_model import GeoModel
from mesa_geo.visualization import MapModule
import numpy as np

model_params = {
    "cost_dirty": UserSettableParameter(
        "slider", "cost dirty", 0.1, 0, 2, 0.01
    ),
    "cost_clean": UserSettableParameter(
        "slider", "cost clean", 0.1, 0, 1, 0.001
    ),
    "metabolism_scalar_energy": UserSettableParameter(
        "slider", "metabolism scalar energy", 1, 2., 0.2, 0.01
    ),
    "metabolism_scalar_money": UserSettableParameter(
        "slider", "metabolism scalar money", 1, 2, 0.2, 0.01
    ),# value, min, max, step
    "eta_global_trade": UserSettableParameter(
        "slider", "eta global trade", 0.1, 0, 1, 0.01
    ),
    "base_output_dirty": UserSettableParameter(
        "slider", "Base output dirty", 1, 0.8, 1.2, 0.001
    ),
    "base_output_clean": UserSettableParameter(
        "slider", "Base output clean", 1, 0.8, 1.2, 0.001
    ),
}


def welfare_draw(agent):
    portrayal = dict()
    # Define upper and lower limits for welfare
    upper_limit = max(agent.model.schedule.agents, key=lambda x: x.welfare).welfare
    lower_limit = min(agent.model.schedule.agents, key=lambda x: x.welfare).welfare
    # Calculate the welfare percentage
    welfare_percent = (agent.welfare - lower_limit) / (upper_limit - lower_limit)
    # Scale the welfare percentage to a value between 0 and 1 for the color scale
    welfare_percent = min(max(welfare_percent, 0), 1)
    # Interpolate the color between green and red
    portrayal["color"] = "rgb(%d,%d,0)" % (255 * (1 - welfare_percent), 255 * welfare_percent)
    return portrayal



map_element = MapModule(welfare_draw, [57, 12], 3.5, 600, 500)
avg_welfare = ChartModule([{"Label": 'var_price', "Color": "Green"},
                           {"Label": 'average_welfare', "Color": "Gold"}], 200, 500)

# type_chart = ChartModule([{"Label": 'other_count', "Color": "Tomato"},
#                           {"Label": 'member_count', "Color": "RoyalBlue"}], 200, 500)
#
# payoff_chart = ChartModule([{"Label": 'average_cooperativeness', "Color": "Gold"}], 200, 500)
#
# gini_chart = ChartModule([{"Label": 'gini_coefficient', "Color": "Green"}], 200, 500)

# wealth_chart = ChartModule([
#     {"Label": 'other_wealth', "Color": "Tomato"},
#     {"Label": 'total_wealth', "Color": "Gold"},
#     {"Label": 'member_wealth', "Color": "RoyalBlue"},
# ], 200, 500)
#
# eff_chart = ChartModule([
#     {"Label": 'other_eff', "Color": "Tomato"},
#     {"Label": 'total_eff', "Color": "Gold"},
#     {"Label": 'member_eff', "Color": "RoyalBlue"},
# ], 200, 500)

server = ModularServer(GeoModel, [map_element, avg_welfare], "EU Energy Model", model_params)

server.launch()
