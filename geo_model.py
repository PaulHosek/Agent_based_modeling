import mesa
import mesa_geo as mg
import country
import numpy as np

class GeoModel(mesa.Model):
    def __init__(self): # TODO need to add initial state parameters to arguments of this function
        # initialise global model parameters
        self.step_nr = 0
        self.schedule = mesa.time.RandomActivation(self)
        # ...

        # initialise grid
        self.grid = mg.GeoSpace()

        # add countries to grid
        ac = mg.AgentCreator(agent_class=country.Country, model=self)
        print(ac)
        # self.agents = ac.from_GeoJSON(GeoJSON='eu_countries.geojson', unique_id="NAME")
        self.agents = ac.from_file("nuts_rg_60M_2013_lvl_2.geojson")
        print(self.agents)
        # TODO test function
        self.agents.remove()

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
            agent_reporters={"perc_energy_met": "perc_energy_met"})  # add more here


        self.init_test_pop()
        self.log_data()

    def log_data(self)->None:
        """
        Compute average values, statistics etc. of the system and self in class attributes (e.g., self.avg_energy).
        Will feed to data_collector later.
        :return: None
        """
        # compute statistics of the step here

        self.data_collector.collect(self)

    def run_model(self, nr_steps) -> None:
        """Run model for n steps."""
        for i in range(nr_steps):
            self.step()


    def step(self)->None:
        """
        Do single model step.
        """
        self.step_nr += 1
        self.schedule.step()

        # do global actions here if any exist e.g., nuke random country idk
        # ...

        self.log_data()

        # # set agent states of next step
        # for agent in self.agents():
        #     agent.perc_energy_met = 0
        #     agent.pred_dirty -= agent.nr_dirty*2394 # !! placeholder value here !! #

    def init_test_pop(self):
        """Initial test population."""
        netherlands_metab  = {"energy":0.1,"money":0.1}
        netherlands_wealth = {"energy":0.5,"money":0.6}

        poland_metab  = {"energy":0.1,"money":0.1}
        poland_wealth = {"energy":0.7,"money":0.2}

        germany_metab  = {"energy":0.1,"money":0.1}
        germany_wealth = {"energy":0.4,"money":0.7}

        NL = country.Country(metabolism=netherlands_metab, wealth=netherlands_wealth)
        PO = country.Country(metabolism=poland_metab, wealth=poland_wealth)
        GE = country.Country(metabolism=germany_metab, wealth=germany_wealth)




        # create germany, netherlands and poland
        # assign rand attributes


if __name__ == "__main__":
    new = GeoModel()
    new.run_model(1)