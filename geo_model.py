import mesa
import mesa_geo as mg
import pandas as pd

import country
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.mstats import gmean
import numba
import time
import random


class GeoModel(mesa.Model):
    def __init__(self):  # TODO need to add initial state parameters to arguments of this function
        # initialise global model parameters
        self.step_nr = 0
        self.schedule = mesa.time.RandomActivation(self)
        # ...
        self.average_welfare = 0.01

        # initialise grid
        self.grid = mg.GeoSpace(crs="4326")

        # add countries to grid
        ac = mg.AgentCreator(agent_class=country.Country, model=self)
        self.agents = ac.from_file("europe_countries.geojson", unique_id="NAME")
        # TODO remove countries not in EU
        self.grid.add_agents(self.agents)

        df = pd.read_csv("Normalised_data.csv", sep=",")
        print(df)

        # set agents initial state
        rng = np.random.default_rng(1)
        for agent in self.agents: # TODO use load country instead
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

        self.data_collector = mesa.datacollection.DataCollector(model_reporters={"Welfare": 'average_welfare'},
                                                                agent_reporters={"Welfare": "welfare"})
        self.log_data()

    def load_country(self, unique_id):
        """
        Initialise the country and fill the attributes from csv.
        :return: None
        """
        pass

    def log_data(self) -> None:
        """
        Compute average values, statistics etc. of the system and self in class attributes (e.g., self.avg_energy).
        Will feed to data_collector later.
        :return: None
        """
        # compute statistics of the step here
        total_welfare = 0
        for agent in self.agents:
            total_welfare += agent.welfare

        self.average_welfare = total_welfare / len(self.agents)
        self.data_collector.collect(self)

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

        # # set agent states of next step
        # for agent in self.agents():
        #     agent.perc_energy_met = 0
        #     agent.pred_dirty -= agent.nr_dirty*2394 # !! placeholder value here !! #

    # def trading_cycle(self) -> None:
    #     """Do full trading cycle.
    #     1. Find buying countries
    #     2. Find selling countries
    #     3. For each buying country: trade with neighbours until
    #         a. own energy need fulfilled
    #         b. neighbors are not selling energy anymore
    #         c. MRS ratio leads to no trade
    #
    #     """
    #     all_buyers = self.find_buyers()
    #
    #
    #     print(f"{len(all_buyers)}/{len(self.agents)} countries are buying.")
    #     all_sellers = self.find_sellers()
    #
    #     for buyer in all_buyers:
    #         print([a.wealth['energy'] for a in all_buyers])
    #         sell_neigh: list = self.get_selling_neigh(buyer, all_sellers)
    #         # loop over neighbours until there is no trading anymore
    #
    #
    #         test = 0
    #         while sell_neigh and buyer.wealth["energy"] < 1 and buyer.wealth["energy"] > 0:
    #             # print(buyer, sell_neigh)
    #
    #
    #             if test == 2:
    #                 raise KeyboardInterrupt
    #             test += 1
    #
    #             rand_idx = np.random.randint(0, len(sell_neigh))
    #             cur_neigh: country.Country = sell_neigh[rand_idx] # dont use numpy here!
    #             if np.isnan(cur_neigh.mrs):
    #                 print("hallo",[a.wealth['energy'] for a in all_buyers])
    #                 print(cur_neigh.wealth["energy"])
    #                 raise KeyboardInterrupt
    #
    #             if buyer.mrs == cur_neigh.mrs:
    #                 del sell_neigh[rand_idx]
    #                 continue
    #
    #             # determine price
    #
    #             else:
    #                 print('mrs', buyer.mrs, cur_neigh.mrs)
    #                 price: float = gmean([buyer.mrs, cur_neigh.mrs], dtype=float, nan_policy = "raise")
    #                 print(type(price), price)
    #                 if price > 1:
    #                     money: float = price
    #                     energy: float = 1
    #                     print(energy,energy)
    #                 else:
    #                     energy: float = 1 / price
    #                     money: float = 1
    #                     print(energy,energy)
    #
    #             # do trades
    #             # if self.isbeneficial(buyer, energy, energy, cur_neigh):
    #             if True:
    #
    #                 if buyer.mrs < 0:
    #                     print("---"*10)
    #                     print(buyer.wealth['energy'], buyer.metabolism['energy'])
    #                     print(buyer.wealth['money'], buyer.metabolism['money'])
    #                 elif cur_neigh.mrs < 0:
    #                     print("---" * 10)
    #                     print(cur_neigh.wealth['energy'], cur_neigh.metabolism['energy'])
    #                     print(cur_neigh.wealth['money'], cur_neigh.metabolism['money'])
    #                 buyer.wealth['energy'] += energy
    #                 buyer.wealth['money'] -= money
    #                 cur_neigh.wealth['money'] += money
    #                 cur_neigh.wealth['energy'] -= energy
    #                 buyer.calculate_welfare()
    #                 buyer.calculate_mrs()
    #                 cur_neigh.calculate_welfare()
    #                 cur_neigh.calculate_mrs()
    #                 # buyer.model.price_record[buyer.model.step_num].append(price)
    #                 # buyer.make_link(cur_neigh)
    #             # elif self.isbeneficial(cur_neigh, energy, energy, buyer):
    #             #     buyer.wealth['energy'] -= energy
    #             #     buyer.wealth['money'] += money
    #             #     cur_neigh.wealth['money'] -= money
    #             #     cur_neigh.wealth['energy'] += energy
    #             #     buyer.calculate_welfare()
    #             #     buyer.calculate_mrs()
    #             #     cur_neigh.calculate_welfare()
    #             #     cur_neigh.calculate_mrs()
    #                 # buyer.model.price_record[buyer.model.step_num].append(price)
    #                 # buyer.make_link(cur_neigh)
    #             else:
    #                 del sell_neigh[rand_idx]
    #                 print('not beneficial')
    #
    #             print(f"price Energy {energy}, price energy {energy} \n"
    #                   f"{buyer} buys from {cur_neigh}\n"
    #                   f"{buyer} has neighbours {sell_neigh}")

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

            all_neighs: list = self.grid.get_neighbors(cur_country)

            # if country is an island, don't trade
            if not len(all_neighs):
                cur_country.last_trade_success = False
                continue

            cur_neigh = np.random.choice(all_neighs)

            # determine price per energy if there will be a trade
            if cur_country.mrs == cur_neigh.mrs:
                cur_country.last_trade_success = False
                cur_neigh.last_trade_success = False
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

            # cur_country.model.price_record[cur_country.model.step_num].append(price)
            # cur_country.make_link(cur_neigh)

if __name__ == "__main__":
    new = GeoModel()
    now = time.time()
    new.run_model(1000)
    # print(time.time()-now)
    data = new.data_collector.get_model_vars_dataframe()
    # a_data = new.data_collector.get_agent_vars_dataframe()
    # df_by_country = a_data.pivot_table(values = 'Welfare', columns = 'AgentID', index = 'Step')
    # plt.figure()
    # plt.semilogy(df_by_country)
    # plt.show()
