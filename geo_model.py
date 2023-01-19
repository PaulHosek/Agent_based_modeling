import mesa
import mesa_geo as mg
import country
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.mstats import gmean
import numba
import random


class GeoModel(mesa.Model):
    def __init__(self):  # TODO need to add initial state parameters to arguments of this function
        # initialise global model parameters
        self.step_nr = 0
        self.schedule = mesa.time.RandomActivation(self)
        # ...
        self.average_welfare = 0

        # initialise grid
        self.grid = mg.GeoSpace(crs="4326")

        # add countries to grid
        ac = mg.AgentCreator(agent_class=country.Country, model=self)
        # self.agents = ac.from_GeoJSON(GeoJSON='europe_countries.geojson', unique_id="NAME")
        self.agents = ac.from_file("europe_countries.geojson", unique_id="NAME")
        # TODO remove countries not in EU
        self.grid.add_agents(self.agents)

        # set agents initial state
        rng = np.random.default_rng()
        for agent in self.agents:
            self.schedule.add(agent)
            nums = rng.uniform(0.5, 1, size=4)
            agent.metabolism = {"energy": 0.02, "money": 0.02}
            agent.wealth = {"energy": nums[2]+0.2, "money": nums[3]+0.2}

            if agent == self.agents[0]:
                agent.metabolism = {"energy": 0.02, "money": 0.02}
                agent.wealth = {"energy": .8, "money": 0.5}
            elif agent == self.agents[1]:
                agent.metabolism = {"energy": 0.02, "money": 0.02}
                agent.wealth = {"energy": 0.5, "money": .8}


        # initialise data collector # TODO fix s.t. it can collect agent reports properly (agent_reporters)
        self.data_collector = mesa.datacollection.DataCollector(model_reporters={"Welfare": 'average_welfare'},
                                                                ) # agent_reporters={"Welfare": "welfare"}
        self.log_data()

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

        # do global actions here if any exist e.g., nuke random country idk
        # ...

        self.trading_cycle()
        self.log_data()

        # # set agent states of next step
        # for agent in self.agents():
        #     agent.perc_energy_met = 0
        #     agent.pred_dirty -= agent.nr_dirty*2394 # !! placeholder value here !! #

        # self.do_trade()

        # do trading as until there are either no buying countries anymore or
        # they do not have any neighbors that sell anymore

    def trading_cycle(self) -> None:
        """Do full trading cycle.
        1. Find buying countries
        2. Find selling countries
        3. For each buying country: trade with neighbours until
            a. own energy need fulfilled
            b. neighbors are not selling energy anymore
            c. MRS ratio leads to no trade

        """
        all_buyers = self.find_buyers()


        print(f"{len(all_buyers)}/{len(self.agents)} countries are buying.")
        all_sellers = self.find_sellers()

        for buyer in all_buyers:
            print([a.wealth['energy'] for a in all_buyers])
            sell_neigh: list = self.get_selling_neigh(buyer, all_sellers)
            # loop over neighbours until there is no trading anymore


            test = 0
            while sell_neigh and buyer.wealth["energy"] < 1 and buyer.wealth["money"] > 0:
                # print(buyer, sell_neigh)


                if test == 2:
                    raise KeyboardInterrupt
                test += 1

                rand_idx = np.random.randint(0, len(sell_neigh))
                cur_neigh: country.Country = sell_neigh[rand_idx] # dont use numpy here!
                if np.isnan(cur_neigh.mrs):
                    print("hallo",[a.wealth['energy'] for a in all_buyers])
                    print(cur_neigh.wealth["energy"])
                    raise KeyboardInterrupt
                if buyer.mrs == cur_neigh.mrs:
                    del sell_neigh[rand_idx]
                    continue

                # determine price

                else:
                    print('mrs', buyer.mrs, cur_neigh.mrs)
                    price: float = gmean([buyer.mrs, cur_neigh.mrs], dtype=float, nan_policy = "raise")
                    print(type(price), price)
                    if price > 1:
                        money: float = price
                        energy: float = 1
                        print(money,energy)
                    else:
                        energy: float = 1 / price
                        money: float = 1
                        print(money,energy)

                # do trades
                # if self.isbeneficial(buyer, energy, money, cur_neigh):
                if True:

                    if np.isnan(buyer.mrs):
                        print("---"*10)
                        print(buyer.wealth['energy'], buyer.metabolism['energy'])
                        print(buyer.wealth['money'], buyer.metabolism['money'])
                    elif np.isnan(cur_neigh.mrs):
                        print("---" * 10)
                        print(cur_neigh.wealth['energy'], cur_neigh.metabolism['energy'])
                        print(cur_neigh.wealth['money'], cur_neigh.metabolism['money'])
                    buyer.wealth['energy'] += energy
                    buyer.wealth['money'] -= money
                    cur_neigh.wealth['money'] += money
                    cur_neigh.wealth['energy'] -= energy
                    buyer.calculate_welfare()
                    buyer.calculate_mrs()
                    cur_neigh.calculate_welfare()
                    cur_neigh.calculate_mrs()
                    # buyer.model.price_record[buyer.model.step_num].append(price)
                    # buyer.make_link(cur_neigh)
                # elif self.isbeneficial(cur_neigh, energy, money, buyer):
                #     buyer.wealth['energy'] -= energy
                #     buyer.wealth['money'] += money
                #     cur_neigh.wealth['money'] -= money
                #     cur_neigh.wealth['energy'] += energy
                #     buyer.calculate_welfare()
                #     buyer.calculate_mrs()
                #     cur_neigh.calculate_welfare()
                #     cur_neigh.calculate_mrs()
                    # buyer.model.price_record[buyer.model.step_num].append(price)
                    # buyer.make_link(cur_neigh)
                else:
                    del sell_neigh[rand_idx]
                    print('not beneficial')

                print(f"price Energy {energy}, price money {money} \n"
                      f"{buyer} buys from {cur_neigh}\n"
                      f"{buyer} has neighbours {sell_neigh}")


    def find_sellers(self):
        """Return list of selling neighbours."""
        return [agent for agent in self.agents if agent.wealth['energy'] > 1]

    def find_buyers(self):
        """Return list of buying neighbours."""
        buyers = list()
        for agent in self.agents:
            if agent.wealth['energy'] < 1 and agent.wealth['money'] > 0:
                buyers.append(agent)
        return buyers

    def get_selling_neigh(self,buyer, sellers: list) -> np.array:  # TODO define sellers
        """
            Returns set of selling neighbours for a buying country
        """
        neighbours = set(self.grid.get_neighbors(buyer))
        selling_neigh = neighbours.intersection(set(sellers))
        # dynamic list faster than np.array or set
        return list(selling_neigh)

    def isbeneficial(self, buying, energy, money, selling):
        """
        Test if trade will result in increased welfare for both agents.
        :param buying:
        :param energy:
        :param money:
        :param selling:
        :return:
        """

        mt_buying = buying.metabolism["energy"] + buying.metabolism["money"]
        mt_selling = selling.metabolism["energy"] + selling.metabolism["money"]

        # don't do trade if it would reduce energy or money to 0 or lower
        print(f"""REduced money buyer {buying.wealth["money"] - money}""")
        print(f"""REduced energy seller{selling.wealth["energy"] - energy}""")
        if (buying.wealth["money"] - money) <= 0 \
                or (selling.wealth["energy"] - energy <= 0):
            return False

        money_buying = buying.wealth["money"] - money
        energy_buying = buying.wealth["energy"] + energy
        money_loss_wel = self.welfare_single(money_buying, buying.metabolism["money"], mt_buying)
        energy_gain_wel = self.welfare_single(energy_buying, buying.metabolism["energy"], mt_buying)
        mrs_buying = self.mrs(money_buying, buying.metabolism["money"],
                              energy_buying, buying.metabolism["energy"])

        money_selling = selling.wealth["money"] + money
        energy_selling = selling.wealth["energy"] - energy
        money_gain_wel = self.welfare_single(money_selling, selling.metabolism["money"], mt_selling)
        energy_loss_wel = self.welfare_single(energy_selling, selling.metabolism["energy"], mt_selling)
        mrs_selling = self.mrs(money_selling, selling.metabolism["money"],
                               energy_selling, selling.metabolism["energy"])
        print(f"Selling welfare {selling.welfare} < {money_gain_wel * energy_loss_wel} ")
        print(f"Buying welfare {buying.welfare} < {energy_gain_wel * money_loss_wel} ")
        if selling.welfare < (money_gain_wel * energy_loss_wel) \
                and buying.welfare < (energy_gain_wel * money_loss_wel) \
                and (mrs_buying >= mrs_selling):
            print("Trade beneficial")
            return True
        else:
            return False

    @staticmethod
    @numba.jit(fastmath=True,nopython=True)
    def welfare_single(w1, m1, mt):
        """Welfare function of only one commodity for the What-if analysis."""
        return np.power(w1, np.divide(m1, mt))

    @staticmethod
    @numba.jit(fastmath=True,nopython=True)
    def mrs(w1, m1, w2, m2):
        """Calculate Marginal Rate of Substitution for specific parameters. Needed for what-if analysis."""
        return np.divide(np.multiply(w1, m2), np.multiply(w2, m1))


if __name__ == "__main__":
    new = GeoModel()
    new.run_model(1)
    data = new.data_collector.get_model_vars_dataframe()
    data.plot()
    plt.show()
