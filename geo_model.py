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
import geopandas as gpd
from esda.moran import Moran
import libpysal


df = gpd.read_file("final_eu_countries.geojson")
# df['geometry'] = df['geometry'].boundary
# Create a spatial weights matrix based on Rook contiguity
weights_moran = libpysal.weights.Rook.from_dataframe(df)

class GeoModel(mesa.Model):
    def __init__(self, cost_clean=0.001, cost_dirty=0.001, base_output_dirty=0.11, base_output_clean=0.051,
                 metabolism_scalar_energy=10, metabolism_scalar_money=1, eta_global_trade=0.01, predisposition_decrease = 0.001):
        # initialise global model parameters
        self.step_nr = 0
        self.schedule = mesa.time.RandomActivation(self)
        self.average_welfare = 0.01
        self.average_price = 0
        self.var_price = 0
        self.avg_pred_dirty = 0.5
        self.avg_pred_clean = 0.5
        self.avg_nr_dirty = 0
        self.avg_nr_clean = 0
        self.gini = 0
        self.moran = 0
        # P(trade with everyone)
        self.eta_trading = eta_global_trade

        # initialise space
        self.space = mg.GeoSpace(crs="4326")


        # add countries to space
        ac = mg.AgentCreator(agent_class=country.Country, model=self)
        self.agents = ac.from_file("final_eu_countries.geojson", unique_id="NAME")
        self.space.add_agents(self.agents)
        self.space.add_agents(self.agents)

        # load countries and set model parameters
        self.metab_e_scalar: float = float(metabolism_scalar_energy)
        self.metab_m_scalar: float = float(metabolism_scalar_money)

        self.load_countries()

        # parameters equivalent to taxation, subsidies and sanktions
        for agent in self.agents:
            agent.cost_clean: float = float(cost_clean)
            agent.cost_clean: float = float(cost_dirty)
            agent.output_single_dirty: float = float(base_output_dirty)
            agent.output_single_clean: float = float(base_output_clean)
            agent.pred_decrease: float = float(predisposition_decrease)

        self.datacollector = mesa.datacollection.DataCollector(model_reporters={"Price": 'average_price',
                                                                                "Welfare": 'average_welfare',
                                                                                "Gini": 'gini',
                                                                                "Morans_i": 'moran',
                                                                                "avg_nr_dirty": 'avg_nr_dirty',
                                                                                "avg_nr_clean": 'avg_nr_clean',
                                                                                "var_price": 'var_price',
                                                                                "Pred_clean": 'avg_pred_clean',
                                                                                "Pred_dirty": 'avg_pred_dirty'},
                                                               agent_reporters={"Welfare": "welfare",
                                                                                "nr_dirty": "nr_dirty",
                                                                                "nr_clean": "nr_clean"})
        self.log_data()

    def load_countries(self):
        """
        Initialise the country and fill the attributes from csv.
        All values have been sourced from real data and scaled into [0,1] using min-max scaling.
        Only "Percentage_GDP_expenditure" was not altered.

        :return: None
        """

        data = pd.read_csv("energy_model_v2.csv", sep=",")
        for agent in self.agents:
            self.schedule.add(agent)
            agent_data = data.loc[data['Country'] == agent.unique_id].reset_index()

            # effective power plant output
            agent.pred_dirty = float(agent_data.at[0, "pred_dirty"])
            agent.pred_clean = float(agent_data.at[0, "pred_clean"])

            # energy
            agent.metabolism["energy"] = agent_data.at[0, "energy_demand"] * \
                                         self.metab_e_scalar
            # money
            agent.influx_money = agent_data.at[0, "gdp_influx"]

            agent.metabolism["money"] = agent_data.at[0, "Percentage_GDP_expenditure"] * \
                                        agent_data.at[0, "gdp_influx"] * self.metab_m_scalar

            if agent.metabolism['energy'] <= 0:
                agent.metabolism['energy'] = 0.001
            if agent.metabolism['money'] <= 0:
                agent.metabolism['money'] = 0.001
            for attr in ["pred_dirty", "pred_clean", "influx_money"]:
                if getattr(agent, attr) <= 0:
                    setattr(agent, attr, 0.001)
            # need to collect to initialise wealth
            agent.collect()
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

        def fast_choice(input_list):
            return input_list[np.random.randint(0, len(input_list))]

        all_countries = self.agents
        rng = np.random.default_rng()

        for cur_country in all_countries:

            # trade with everyone with probability eta
            if self.eta_trading > rng.random():
                all_neighs: list = self.space.get_neighbors(cur_country)
            else:
                all_neighs: list = self.agents

            # if country is an island, don't trade
            if not len(all_neighs):
                cur_country.last_trade_success = False
                cur_country.last_trade_price_energy = 0.0001
                continue

            cur_neigh = fast_choice(all_neighs)

            # determine price per energy if there will be a trade
            if cur_country.mrs == cur_neigh.mrs:
                cur_country.last_trade_success = False
                cur_neigh.last_trade_success = False
                cur_country.last_trade_price_energy = 0.0001
                cur_neigh.last_trade_price_energy = 0.0001

                continue
            else:
                price: float = float(gmean([cur_country.mrs, cur_neigh.mrs], dtype=float))
                if price == np.nan:
                    raise ValueError(f"{price} is nan.")
            # do trades
            if cur_neigh.mrs > cur_country.mrs:
                # calculate how much wealth exceeds the buffer
                # no trade if no buffer (0.3 energy)
                energy_left = cur_neigh.wealth['energy'] - (cur_neigh.wealth['energy']*0.3)
                money_left = cur_country.wealth['money'] - (cur_country.wealth['money']*0.3)
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
                energy_left = cur_country.wealth['energy'] - (cur_country.wealth['energy']*0.3)
                money_left = cur_neigh.wealth['money'] -(cur_neigh.wealth['money']*0.3)
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

            # cur_country.model.price_record[cur_country.model.step_num].append(price)
            # cur_country.make_link(cur_neigh)

    def log_data(self) -> None:
        """
        Compute average values, statistics etc. of the system and self in class attributes (e.g., self.avg_energy).
        Will feed to datacollector later.
        :return: None
        """

        def gini_coef(x, w=None):
            x = np.asarray(x)
            sorted_x = np.sort(x)
            n = len(x)
            cumx = np.cumsum(sorted_x, dtype=float)
            return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n

        # compute statistics of the step here
        nr_agents = len(self.agents)
        total_welfare = 0
        prices = np.empty(nr_agents)
        pred_dirty = 0
        total_nr_dirty = 0
        total_nr_clean = 0
        welfares_list = np.empty(nr_agents)
        for idx, agent in enumerate(self.agents):
            total_welfare += agent.welfare
            pred_dirty += agent.pred_dirty
            total_nr_clean += agent.nr_clean
            total_nr_dirty += agent.nr_dirty
            welfares_list[idx] = agent.welfare
            if agent.last_trade_price_energy != 0.0001:
                prices[idx] = agent.last_trade_price_energy
        self.gini = gini_coef(welfares_list)
        self.moran = Moran(welfares_list, weights_moran)


        self.average_welfare = total_welfare / nr_agents
        self.avg_pred_dirty = pred_dirty / nr_agents
        self.avg_nr_dirty = total_nr_dirty / nr_agents
        self.avg_nr_clean = total_nr_clean / nr_agents


        # print(self.average_welfare)

        self.average_price = np.mean(prices)
        self.var_price = np.var(prices)
        self.datacollector.collect(self)


if __name__ == "__main__":
    pd.options.display.max_columns = None
    now = time.time()
    new = GeoModel()
    new.run_model(10)
    print(time.time() - now)
    data = new.datacollector.get_model_vars_dataframe()
    print(data)
    a_data = new.datacollector.get_agent_vars_dataframe()
    print(a_data)
    # df_by_country = a_data.pivot_table(values = 'Price', columns = 'AgentID', index = 'Step')
    # print()

    # last_state = df_by_country.iloc[-1]
    #and
    plt.figure()
    # plt.plot(data["Pred_dirty"])
    # plt.plot(data["avg_nr_dirty"], color='brown')
    # plt.plot(data["avg_nr_clean"], color='green')
    plt.plot(data["Morans_i"], color='green')
    # plt.plot(data["Gini"], color='green')
    # plt.semilogy(data["Price"][10:])
    # plt.plot(data["Welfare"][10:])
    # plt.xlim([10,100])
    # plt.xlim([10,100])
    plt.show()

    # print(a_data)
