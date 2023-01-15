import mesa
import mesa_geo as mg
from country import Country

class GeoModel(mesa.Model):
    def __init__(self): # TODO need to add initial state parameters to arguments of this function
        # initialise global model parameters
        self.step_nr = 0
        self.schedule = mesa.time.RandomActivation()
        # ...

        # initialise grid
        self.grid = mg.GeoSpace()

        # add countries to grid
        ac = mg.AgentCreator(agent_class=Country.Country, model=self)
        raise NotImplementedError("Get EU countries geojson.")
        self.agents = ac.from_GeoJSON(GeoJSON=eu_countries, unique_id="NAME") # TODO get EU countries geojson
        self.grid.add_agents(self.agents)

        # set agents initial state
        for agent in self.agents:
            self.schedule.add(agent)
            agent.cost_dirty = self.cost_dirty
            agent.cost_clean = self.cost_clean
            # set initial state of each agent here

        # initialise data collector
        self.data_collector = mesa.datacollection.DataCollector(
            model_reporters={"Welfare": "welfare"},
            agent_reporters={"perc_energy_met": "perc_energy_met"}  # add more here

        self.log_data()

    def log_data(self):
        """
        Compute average values, statistics etc. of the system and self in class attributes (e.g., self.avg_energy).
        Will feed to data_collector later.
        :return: None
        """
        # compute statistics of the step here

        self.data_collector.collect(self)


    def step(self):
        """
        Do single model step.
        """
        self.step_nr += 1
        self.schedule.step()

        # do global actions here if any exist e.g., nuke random country idk
        # ...

        self.log_data()

        # set agent states of next step
        for agent in self.agents():
            agent.perc_energy_met = 0
            agent.pred_dirty -= agent.nr_dirty*2394 # !! placeholder value here !! #
