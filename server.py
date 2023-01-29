import os

os.environ['USE_PYGEOS'] = '0'
from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import Slider
from geo_model import GeoModel
from mesa_geo.visualization import MapModule

import numpy as np

model_params = {
    "cost_dirty": Slider("cost dirty", 0.6, 0.01, 1, 0.01),
    "cost_clean": Slider("cost clean", 0.4, 0.01, 1, 0.001),
    "base_output_dirty": Slider("Base output dirty", 0.65, 0.001, 1, 0.001),
    "base_output_clean": Slider("Base output clean", 0.73, 0.001, 1, 0.001),
    "metabolism_scalar_energy": Slider("metabolism scalar energy", 4.5, 1, 10, 0.01),
    "metabolism_scalar_money": Slider("metabolism scalar money", 1, 1, 10, 0.01),
    "eta_global_trade": Slider("eta global trade", 0.1, 0, 1, 0.01),

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

def nr_plants_draw(agent):
    portrayal = dict()
    # Define upper and lower limits for the number of clean and dirty plants
    upper_limit_clean = max(agent.model.schedule.agents, key=lambda x: x.nr_clean).nr_clean
    lower_limit_clean = min(agent.model.schedule.agents, key=lambda x: x.nr_clean).nr_clean
    upper_limit_dirty = max(agent.model.schedule.agents, key=lambda x: x.nr_dirty).nr_dirty
    lower_limit_dirty = min(agent.model.schedule.agents, key=lambda x: x.nr_dirty).nr_dirty
    if upper_limit_clean == lower_limit_clean and upper_limit_dirty == lower_limit_dirty:
        portrayal["color"] = "rgb(0,0,0)"
    else:
        # Calculate the percentage of clean and dirty plants
        clean_percent = (agent.nr_clean - lower_limit_clean) / (upper_limit_clean - lower_limit_clean)
        dirty_percent = (agent.nr_dirty - lower_limit_dirty) / (upper_limit_dirty - lower_limit_dirty)

        # Scale the percentage to a value between 0 and 1 for the color scale
        clean_percent = min(max(clean_percent, 0), 1)
        dirty_percent = min(max(dirty_percent, 0), 1)

        # Check if agent has more clean plants than dirty plants
        if agent.nr_clean > agent.nr_dirty:
            portrayal["color"] = "rgb(%d,%d,0)" % (255 * (1 - clean_percent), 255 * clean_percent)
        else:
            portrayal["color"] = "rgb(%d,%d,0)" % (255 * (1 - dirty_percent), 255 * dirty_percent)
    return portrayal




map_width = 500
map_height = 400
# map_welfare = MapModule(welfare_draw, [57, 12], 3.5, map_width, map_height)
map_plants = MapModule(nr_plants_draw, [57, 12], 3.5, map_width, map_height)
avg_welfare = ChartModule([{"Label": 'var_price', "Color": "Green"},
                           {"Label": 'average_welfare', "Color": "Gold"}], 200, 500)

plant_chart = ChartModule([{"Label": 'avg_nr_dirty', "Color": "Tomato"},
                          {"Label": 'avg_nr_clean', "Color": "Green"}], 200, 500)
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

server = ModularServer(GeoModel, [map_plants, plant_chart, avg_welfare], "EU Energy Model", model_params)

server.launch()
