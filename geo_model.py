import mesa
import os
os.environ['USE_PYGEOS'] = '0'
import mesa_geo as mg
import pandas as pd

import country
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.mstats import gmean
import time
import segregation


class GeoModel(mesa.Model):
    def __init__(self, cost_clean=0, cost_dirty=0, base_output_dirty=0, base_output_clean=0,
                metabolism_scalar_energy=1, metabolism_scalar_money=1, eta_global_trade=0):  # TODO need to add initial state parameters to arguments of this function
        # initialise global model parameters
        self.step_nr = 0
        self.schedule = mesa.time.RandomActivation(self)
        # ...
        self.average_welfare = 0.01
        self.average_price = 0
        self.var_price = 0
        # P(trade with everyone)
        self.eta_trading = eta_global_trade

        # initialise grid
        self.grid = mg.GeoSpace(crs="4326")

        # add countries to grid
        ac = mg.AgentCreator(agent_class=country.Country, model=self)
        self.agents = ac.from_file("new_eu_countries.geojson", unique_id="NAME")
        # TODO remove countries not in EU
        self.grid.add_agents(self.agents)

        df = pd.read_csv("Normalised_data_v2.csv", sep=",", index_col=0)

        # set agents initial state
        # TODO use load countries instead
        ########################################################
        rng = np.random.default_rng(1)
        for agent in self.agents:
            self.schedule.add(agent)
            nums = rng.uniform(0.01, 1, size=4)
            metabs = rng.uniform(0.01, 0.1, size=2)
            agent.metabolism = {"energy": metabs[0], "money": metabs[1]}
            agent.wealth = {"energy": nums[2], "money": nums[3]}
            agent.influx_money = 0.2
            agent.pred_clean = 0.9
            agent.pred_dirty = 0.3
            agent.output_single_clean = 0.8
            agent.output_single_dirty = 0.8
            agent.cost_clean = 0.01
            agent.cost_dirty = 0.01
            agent.calculate_welfare()
            agent.calculate_mrs()
        ##########################################

        for agent in self.agents:
            agent.cost_clean = cost_clean
            agent.cost_clean = cost_dirty
            agent.output_single_dirty = base_output_dirty
            agent.output_single_clean = base_output_clean
        self.metab_e_scalar = metabolism_scalar_energy
        self.metab_m_scalar = metabolism_scalar_money

        self.data_collector = mesa.datacollection.DataCollector(model_reporters={"Welfare": 'average_welfare'},
                                                                agent_reporters={"Welfare": "welfare"})
        self.log_data()

    def load_countries(self):
        """
        Initialise the country and fill the attributes from csv.
        :return: None
        """

        data = pd.read_csv("Normalised_data_v2.csv", sep=",")
        for agent in self.agents:
            self.schedule.add(agent)
            agent_data = data.loc[data['name'] == agent.unique_id]
            agent.pred_dirty = agent_data["pred_dirty"]
            agent.pred_clean = agent_data["pred_clean"]
            agent.metabolism["energy"] = agent_data["energy_demand"] * self.metab_e_scalar
            agent.gpd_influx = agent_data["gpd_influx"]
            agent.metabolism["money"] = agent_data["gov_expenditure"] * self.metab_m_scalar
            agent.calculate_welfare()
            agent.calculate_mrs()

    def run_model(self, nr_steps) -> None:
        """Run model for n steps."""
        for i in range(nr_steps):
            self.step()

    def step(self) -> None:
        """
        Do single model step.
        """
        self.step_nr += 1
        self.schedule.step()
        self.trading_cycle()
        self.log_data()
    def trading_cycle(self) -> None:
        """Do full trading cycle.
        1. Find buying countries
        2. Find selling countries
        3. For each country:
            a. Pick a random neighbour to trade with
            b. trade according to MRS ratio between countries
            c. trade maximally 0.1 of a resource and leave 0.3 as a buffer
                - no trade is made if the country has <0.3 of the resource of interest
        """
        all_countries = self.agents
        rng = np.random.default_rng()

        for cur_country in all_countries:

            # trade with everyone with probability eta
            if self.eta_trading > rng.random():
                all_neighs: list = self.grid.get_neighbors(cur_country)
            else:
                all_neighs: list = self.agents

            # if country is an island, don't trade
            if not len(all_neighs):
                cur_country.last_trade_success = False
                cur_country.last_trade_price_energy = 0.0001
                continue

            cur_neigh = np.random.choice(all_neighs)

            # determine price per energy if there will be a trade
            if cur_country.mrs == cur_neigh.mrs:
                cur_country.last_trade_success = False
                cur_neigh.last_trade_success = False
                cur_country.last_trade_price_energy = 0.0001
                cur_neigh.last_trade_price_energy = 0.0001

                continue
            else:
                price: float = float(gmean([cur_country.mrs, cur_neigh.mrs], dtype=float, nan_policy="raise"))

            # do trades
            if cur_neigh.mrs > cur_country.mrs:
                # calculate how much wealth exceeds the buffer
                # no trade if no buffer (0.3 energy)
                energy_left = cur_neigh.wealth['energy'] - 0.3
                money_left = cur_country.wealth['money'] - 0.3
                if money_left < 0 or energy_left < 0:
                    cur_country.last_trade_success = False
                    cur_neigh.last_trade_success = False
                    cur_country.last_trade_price_energy = 0.0001
                    cur_neigh.last_trade_price_energy = 0.0001
                    continue

                # determine how much is being traded
                # 0.1 is the max energy allowed to be traded
                # 0.3 the min level money and energy allowed

                # if have less than 0.1 energy/money more than the buffer, trade everything up to buffer
                if 0.1 > energy_left and energy_left < money_left:
                    energy = energy_left
                    money = price * energy_left
                elif 0.1 > money_left and money_left < energy_left:
                    energy = price * money_left
                    money = 1 * money_left

                # else trade 0.1 energy
                else:
                    if price > 1:
                        energy = 0.1
                        money = 0.1 / price
                    else:
                        energy = 0.1 * price
                        money = 0.1

                # do transaction
                cur_country.wealth['energy'] += energy
                cur_country.wealth['money'] -= money
                cur_neigh.wealth['money'] += money
                cur_neigh.wealth['energy'] -= energy
                cur_country.calculate_welfare()
                cur_country.calculate_mrs()
                cur_neigh.calculate_welfare()
                cur_neigh.calculate_mrs()

            else:
                # calculate how much wealth exceeds the buffer
                # no trade if no buffer (0.3 energy)
                energy_left = cur_country.wealth['energy'] - 0.3
                money_left = cur_neigh.wealth['money'] - 0.3
                if money_left < 0 or energy_left < 0:
                    cur_country.last_trade_success = False
                    cur_neigh.last_trade_success = False
                    continue

                # determine how much is being traded
                # 0.1 is the max energy allowed to be traded
                # 0.3 the min level money and energy allowed

                # if have less than 0.1 energy/money more than the buffer, trade everything up to buffer
                if 0.1 > energy_left and energy_left < money_left:
                    energy = energy_left
                    money = price * energy_left
                elif 0.1 > money_left and money_left < energy_left:
                    energy = price * money_left
                    money = 1 * money_left

                # else trade 0.1 energy
                else:
                    if price > 1:
                        energy = 0.1
                        money = 0.1 / price
                    else:
                        energy = 0.1 * price
                        money = 0.1
                # do transaction
                cur_country.wealth['energy'] -= energy
                cur_country.wealth['money'] += money
                cur_neigh.wealth['money'] -= money
                cur_neigh.wealth['energy'] += energy
                cur_country.calculate_welfare()
                cur_country.calculate_mrs()
                cur_neigh.calculate_welfare()
                cur_neigh.calculate_mrs()

            # pass information about trade to decision function in the next step
            cur_country.last_trade_price_energy = price
            cur_country.last_trade_success = True
            cur_neigh.last_trade_price_energy = price
            cur_neigh.last_trade_success = True

        def make_link(self, partner):
            if self.model.ml.net.has_edge(cur_country, cur_neigh):
                self.model.ml.net[cur_country][cur_neigh]["trades"] += 1
            else:
                self.model.ml.net.add_edge(cur_country, cur_neigh, trades=1)

            # cur_country.model.price_record[cur_country.model.step_num].append(price)
            # cur_country.make_link(cur_neigh)

    def log_data(self) -> None:
        """
        Compute average values, statistics etc. of the system and self in class attributes (e.g., self.avg_energy).
        Will feed to data_collector later.
        :return: None
        """
        # compute statistics of the step here
        nr_agents = len(self.agents)
        total_welfare = 0
        prices = np.empty(nr_agents)
        for idx, agent in enumerate(self.agents):
            total_welfare += agent.welfare
            if agent.last_trade_price_energy != 0.0001:
                prices[idx] = agent.last_trade_price_energy
        self.average_welfare = total_welfare / nr_agents

        self.average_price = np.mean(prices)
        self.var_price = np.var(prices)
        self.data_collector.collect(self)


# if __name__ == "__main__":
#     new = GeoModel()
#     now = time.time()
#     new.run_model(1000)
#     # print(time.time()-now)
#     # data = new.data_collector.get_model_vars_dataframe()
#     a_data = new.data_collector.get_agent_vars_dataframe()
#     df_by_country = a_data.pivot_table(values = 'Welfare', columns = 'AgentID', index = 'Step')
#     # print()
#     last_state = df_by_country.iloc[-1]
#
#     plt.figure()
#     plt.semilogy(df_by_country)
#     plt.show()
#     # print(a_data)
