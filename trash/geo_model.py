import math

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


class GeoModel(mesa.Model):
    def __init__(self, cost_clean=0.3, cost_dirty=0.1, base_output_dirty=0.7, base_output_clean=0.2,
                 metabolism_scalar_energy=1, metabolism_scalar_money=.2, eta_global_trade=0.01, predisposition_decrease= 0.0000001):
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
        self.trading_volume = 0
        self.gini = 0
        self.prop_clean = 0
        self.more_clean = 0
        self.more_dirty = 0
        self.timestep = 0
        self.dom = ''
        self.clean_overtake = 0
        self.var_welfare = 0
        # P(trade with everyone)
        self.eta_trading = eta_global_trade

        # initialise space
        self.space = mg.GeoSpace(crs="4326")

        # add countries to space
        ac = mg.AgentCreator(agent_class=country.Country, model=self)
        self.agents = ac.from_file("final_eu_countries.geojson", unique_id="NAME")
        self.space.add_agents(self.agents)

        # load countries and set model parameters
        self.metab_e_scalar: float = float(metabolism_scalar_energy)
        self.metab_m_scalar: float = float(metabolism_scalar_money)

        # parameters equivalent to taxation, subsidies and sanktions
        for agent in self.agents:
            agent.cost_clean: float = float(cost_clean)
            agent.cost_dirty: float = float(cost_dirty)
            agent.output_single_dirty: float = float(base_output_dirty)
            agent.output_single_clean: float = float(base_output_clean)
            agent.predisposition_decrease = predisposition_decrease

        self.datacollector = mesa.datacollection.DataCollector(model_reporters={"Price": 'average_price',
                                                                                "Welfare": 'average_welfare',
                                                                                "Gini": 'gini',

                                                                                "avg_nr_dirty": 'avg_nr_dirty',
                                                                                "avg_nr_clean": 'avg_nr_clean',

                                                                                "nr_dirty": 'avg_nr_dirty',
                                                                                "nr_clean": 'avg_nr_clean',

                                                                                "var_price": 'var_price',
                                                                                "Pred_clean": 'avg_pred_clean',
                                                                                "Trading_volume": 'trading_volume',
                                                                                "proportion_clean": "prop_clean",
                                                                                "clean_overtake": "clean_overtake",
                                                                                "more_clean": "more_clean",
                                                                                "more_dirty": "more_dirty",
                                                                                "dominating_type": "dom",
                                                                                "var_welfare": "var_welfare",
                                                                                "Pred_dirty": 'avg_pred_dirty'},
                                                               agent_reporters={"Welfare": "welfare",
                                                                                "nr_dirty": "nr_dirty",
                                                                                "nr_clean": "nr_clean",
                                                                                "w_energy": "w_energy",
                                                                                "w_money": "w_money"})
        # self.load_countries()
        self.init_random()

        self.log_data()

    def load_countries(self):
        """
        Initialise the country and fill the attributes from csv.
        All values have been sourced from real data and scaled into [0,1] using min-max scaling.
        Only "Percentage_GDP_expenditure" was not altered.

        :return: None
        """
        pred_dirties = np.empty(len(self.agents))
        pred_cleans = np.empty(len(self.agents))

        # print(rands)
        rands1 = np.random.uniform(low=0.01, size=len(self.agents))
        rands2 = np.random.uniform(low=0.01, size=len(self.agents))

        data = pd.read_csv("../energy_model_v2.csv", sep=",")
        for i, agent in enumerate(self.agents):
            self.schedule.add(agent)
            agent_data = data.loc[data['Country'] == agent.unique_id].reset_index()

            # effective power plant output
            agent.pred_dirty = float(agent_data.at[0, "pred_dirty"])
            agent.pred_clean = float(agent_data.at[0, "pred_clean"])

            pred_dirties[i] = float(agent_data.at[0, "pred_dirty"]) * 10
            pred_cleans[i] = float(agent_data.at[0, "pred_clean"]) * 10
            # energy
            agent.m_energy = agent_data.at[0, "energy_demand"] * \
                             self.metab_e_scalar
            # money
            agent.influx_money = agent_data.at[0, "gdp_influx"]

            agent.m_money = agent_data.at[0, "Percentage_GDP_expenditure"] * \
                            agent_data.at[0, "gdp_influx"] * self.metab_m_scalar

            agent.w_money = np.random.uniform(low=0.01, high=agent.influx_money)
            agent.w_energy = np.random.uniform(low=0.01, high=agent.influx_money)

            # new
            # agent.w_energy = rands[i]

            if agent.m_energy <= 0:
                agent.m_energy = 0.001
            if agent.m_money <= 0:
                agent.m_money = 0.001
            for attr in ["pred_dirty", "pred_clean", "influx_money"]:
                if getattr(agent, attr) <= 0:
                    setattr(agent, attr, 0.001)
            # need to collect to initialise wealth
            agent.collect()
            agent.calculate_welfare()
            agent.calculate_mrs()

        # plt.figure()
        # # Plot a histogram of the values
        # plt.hist(pred_dirties, bins=50, edgecolor='black',alpha = 0.5,label = 'dirty')
        # plt.hist(pred_cleans, bins=50, edgecolor='black',alpha = 0.5,label = 'clean')
        #
        # # Add labels and title
        # plt.xlabel('Values')
        # plt.ylabel('Frequency')
        # plt.legend()
        # plt.title('Distribution of Values')

        # Show plot
        # plt.show()

    def init_random(self):
        rng = np.random.default_rng()
        rands = np.random.uniform(low=0.01, size=len(self.agents)*8)
        rands = rands.reshape((8, len(self.agents)))
        for i, agent in enumerate(self.agents):
            self.schedule.add(agent)
            rands1 = rands[:, i]
            agent.w_energy = rands1[0]
            agent.w_money = rands1[1]
            agent.m_energy = rands1[2] * self.metab_e_scalar
            agent.m_money = rands1[3] * self.metab_m_scalar
            agent.pred_dirty = rands1[4]
            agent.pred_clean = rands1[5]
            agent.influx_money = rands1[6]
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

        # def min_max(vals):
        #     min_val = min(vals)
        #     max_val = max(vals)
        #     return [(x - min_val) / (max_val - min_val) for x in vals]

        # scaled = min_max([a.welfare for a in self.agents])
        # for i, a in enumerate(self.agents):
        #     a.welfare = scaled[i]
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
                if math.isnan(price):
                    raise ValueError(f"Price {price} is nan.")

            # do trades
            if cur_neigh.mrs < cur_country.mrs:

                # calculate how much wealth exceeds the buffer
                # no trade if no buffer (0.3 energy)
                energy_left = cur_neigh.w_energy - (cur_neigh.w_energy * 0.3)
                money_left = cur_country.w_money - (cur_country.w_money * 0.3)
                # if money_left < 0 or energy_left < 0: # TODO this os false, needs to be bigger than trade volume
                #     cur_country.last_trade_success = False
                #     cur_neigh.last_trade_success = False
                #     cur_country.last_trade_price_energy = 0.0001
                #     cur_neigh.last_trade_price_energy = 0.0001
                #     continue

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
                        money = 0.1 * price
                    else:
                        energy = 0.1 / price
                        money = 0.1

                if energy_left < energy or money_left < money:
                    cur_country.last_trade_success = False
                    cur_neigh.last_trade_success = False
                    cur_country.last_trade_price_energy = 0.0001
                    cur_neigh.last_trade_price_energy = 0.0001
                    continue

                # do transaction
                cur_country.w_energy += energy
                cur_country.w_money -= money
                cur_neigh.w_money += money
                cur_neigh.w_energy -= energy
                cur_country.calculate_welfare()
                cur_country.calculate_mrs()
                cur_neigh.calculate_welfare()
                cur_neigh.calculate_mrs()
                self.trading_volume += 1


            else:
                # calculate how much wealth exceeds the buffer
                # no trade if no buffer (0.3 energy)
                energy_left = cur_country.w_energy - (cur_country.w_energy * 0.3)
                money_left = cur_neigh.w_money - (cur_neigh.w_money * 0.3)
                # if money_left < 0 or energy_left < 0:
                #     cur_country.last_trade_success = False
                #     cur_neigh.last_trade_success = False
                #     continue

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
                        money = 0.1 * price
                    else:
                        energy = 0.1 / price
                        money = 0.1

                if energy_left < energy or money_left < money:
                    cur_country.last_trade_success = False
                    cur_neigh.last_trade_success = False
                    cur_country.last_trade_price_energy = 0.0001
                    cur_neigh.last_trade_price_energy = 0.0001
                    continue

                # do transaction
                cur_country.w_energy -= energy
                cur_country.w_money += money
                cur_neigh.w_money -= money
                cur_neigh.w_energy += energy
                cur_country.calculate_welfare()
                cur_country.calculate_mrs()
                cur_neigh.calculate_welfare()
                cur_neigh.calculate_mrs()
                self.trading_volume += 1

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

        if total_nr_clean != 0 and total_nr_dirty != 0:
            self.prop_clean = total_nr_clean/(total_nr_dirty+total_nr_clean)

        self.timestep += 1
        if total_nr_clean > total_nr_dirty:
            if self.dom == 'dirty':
                self.clean_overtake = self.timestep
            self.more_clean += 1
            self.dom = 'clean'
        elif total_nr_clean < total_nr_dirty:
            if self.dom == 'clean':
                self.clean_overtake = self.timestep
            self.more_dirty += 1
            self.dom = 'dirty'

        self.average_welfare = total_welfare / nr_agents
        self.avg_pred_dirty = pred_dirty / nr_agents
        self.avg_nr_dirty = total_nr_dirty / nr_agents
        self.avg_nr_clean = total_nr_clean / nr_agents

        # print(self.average_welfare)

        self.average_price = np.mean(prices)
        self.var_price = np.var(prices)
        self.var_welfare = np.var(welfares_list)
        self.datacollector.collect(self)
        self.trading_volume = 0


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)

    now = time.time()
    new = GeoModel()
    new.run_model(3000)
    print(time.time() - now)
    data = new.datacollector.get_model_vars_dataframe()
    # print(data)
    a_data = new.datacollector.get_agent_vars_dataframe()
    df_by_country_m = a_data.pivot_table(values='w_energy', columns='AgentID', index='Step')
    df_by_country_e = a_data.pivot_table(values='w_money', columns='AgentID', index='Step')
    # df_by_country_e = a_data.pivot_table(values = 'w_money', columns = 'AgentID', index = 'Step')
    # print("Welfare")
    # print(a_data.pivot_table(values='Welfare', columns='AgentID', index='Step'))
    # print("w_energy")
    # print(df_by_country_e)
    plt.figure()
    # plt.plot(df_by_country_m, color='green')
    plt.plot(df_by_country_e, color='red')
    plt.show()

    plt.figure()
    # plt.plot(df_by_country_m, color='green')
    plt.title("var welfare")
    plt.plot(data["var_welfare"])
    plt.show()

    plt.figure()
    plt.title("trading volume")
    # plt.plot(df_by_country_m, color='green')
    plt.plot(data["Trading_volume"])
    plt.show()

    # print()
    # print("Welfare by country\n")
    # print(df_by_country[:30])

    # plt.figure()
    # plt.title("wealth")
    # plt.plot(a_data.pivot_table(values='w_energy', columns='AgentID', index='Step'), color='red', label='energy')
    # plt.plot(a_data.pivot_table(values='w_money', columns='AgentID', index='Step'), color='green', label='money')
    # plt.show()
    print("WELFARE MAX")
    my_pivot = a_data.pivot_table(values='Welfare', columns='AgentID', index='Step')
    print(my_pivot.max())

    plt.figure()
    plt.title("welfare per country")
    plt.plot(a_data.pivot_table(values='Welfare', columns='AgentID', index='Step'))

    plt.show()

    # last_state = df_by_country.iloc[-1]
    # and

    # plt.title("nr dirty per country")
    # plt.plot(data["Pred_dirty"])
    # plt.plot(df_by_country)
    plt.figure()
    plt.plot(data["nr_dirty"], color='brown')
    plt.plot(data["nr_clean"], color='green')
    plt.show()
    # plt.semilogy(data["Price"][10:])
    # plt.plot(data["Welfare"][10:])
    # plt.xlim([10,100])
    # plt.xlim([10,100])

    # plt.figure()
    # plt.title("nr dirty avg")
    # plt.plot(data["nr_dirty"], color='brown')
    # plt.plot(data["nr_clean"], color='green')
    # plt.show()

    # print(a_data)