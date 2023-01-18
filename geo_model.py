import mesa
import mesa_geo as mg
import country
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gmean
import numba


class GeoModel(mesa.Model):
    def __init__(self):  # TODO need to add initial state parameters to arguments of this function
        # initialise global model parameters
        self.step_nr = 0
        self.schedule = mesa.time.RandomActivation(self)
        # ...
        self.average_welfare = 0

        # initialise grid
        self.grid = mg.GeoSpace()

        # add countries to grid
        ac = mg.AgentCreator(agent_class=country.Country, model=self)
        # self.agents = ac.from_GeoJSON(GeoJSON='eu_countries.geojson', unique_id="NAME")
        self.agents = ac.from_file("eu_countries.geojson", unique_id="NAME")
        # TODO test function
        # self.agents = self.agents[:3]

        self.grid.add_agents(self.agents)
        print(self.grid)

        # set agents initial state
        rng = np.random.default_rng()
        for agent in self.agents:
            self.schedule.add(agent)
            nums = rng.uniform(0, 1, size=4)
            agent.metabolism = {"energy": nums[0], "money": nums[1]}
            agent.wealth = {"energy": nums[2], "money": nums[3]}

            # agent.cost_dirty = self.cost_dirty
            # agent.cost_clean = self.cost_clean
            # set initial state of each agent here

        # initialise data collector
        self.data_collector = mesa.datacollection.DataCollector({"Welfare": 'average_welfare'})
        # ,agent_reporters={"perc_energy_met": "perc_energy_met"})  # add more here

        # self.init_test_pop()
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
        print(self.average_welfare)

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

        self.log_data()

        # # set agent states of next step
        # for agent in self.agents():
        #     agent.perc_energy_met = 0
        #     agent.pred_dirty -= agent.nr_dirty*2394 # !! placeholder value here !! #

        # self.do_trade()

        # do trading as until there are either no buying countries anymore or
        # they do not have any neighbors that sell anymore

    def trading_cycle(self):
        """Do full trading cycle.
        1. Find buying countries
        2. Find selling countries
        3. For each buying country: trade with neighbours until
            a. own energy need fulfilled
            b. neighbors are not selling energy anymore
            c. MRS ratio leads to no trade

        """
        buyers = self.find_buyers()
        sellers = self.find_sellers()

        for buyer in buyers:
            sell_neigh = set(sellers).intersection(self.model.grid.get_neighbors(self))
            # find intersection
            # TODO loop over neighbours until there is no trading anymore
            cur_neigh = random.choice(sell_neigh)
            sell_neigh.pop(cur_neigh)

            if buyer.MRS == cur_neigh.MRS:
                continue
            else:
                # Calculate Price
                price = gmean([buyer.MRS, cur_neigh.MRS])
                if price > 1:
                    money = price  # TODO figure out when this works
                    energy = 1
                else:
                    energy = 1 / price
                    money = 1

            # do trades
            if buyer.MRS > cur_neigh.MRS:
                if buyer.draft_trade(energy, money, cur_neigh):
                    buyer.wealth['energy'] += energy
                    buyer.wealth['money'] -= money
                    cur_neigh.wealth['money'] += money
                    cur_neigh.wealth['energy'] -= energy
                    # buyer.model.price_record[buyer.model.step_num].append(price)
                    buyer.calculate_welfare()
                    cur_neigh.calculate_welfare()
                    buyer.make_link(cur_neigh)



            else:
                if cur_neigh.draft_trade(energy, money, buyer):
                    buyer.wealth['energy'] -= energy
                    buyer.wealth['money'] += money
                    cur_neigh.wealth['money'] -= money
                    cur_neigh.wealth['energy'] += energy
                    buyer.calculate_welfare()
                    cur_neigh.calculate_welfare()
                    # buyer.model.price_record[buyer.model.step_num].append(price)
                    buyer.make_link(cur_neigh)  # TODO fix this

    def find_sellers(self):  # TODO in model
        """Return list of selling neighbours."""
        return [agent for agent in self.agents if agent.wealth['energy'] > 100]

    def find_buyers(self):  # TODO in model
        """Return list of buying neighbours."""
        buyers = list()
        for agent in self.agents:
            if agent.wealth['energy'] < 100 and agent.wealth['money'] > 0:
                buyers.append(agent)
        return buyers

    def if_trade(self, buying, energy, money, selling):
        """
        Decide on expected
        :param buying:
        :param energy:
        :param money:
        :param selling:
        :return:
        """

        mt_buying = buying.metabolism["energy"] + buying.metabolism["money"]
        mt_selling = selling.metabolism["energy"] + selling.metabolism["money"]

        # dont do trade if would reduce energy or money to 0 or lower

        if (buying.wealth["money"] - money) <= 0 \
                or (selling.wealth["energy"] - energy <= 0):
            return False

        money_buying = (buying.wealth["money"] - money)
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

        if selling.welfare < (money_gain_wel * energy_loss_wel) \
                and buying.welfare < (energy_gain_wel * money_loss_wel) \
                and (mrs_buying >= mrs_selling):
            return True
        else:
            return False

    @staticmethod
    @numba.njit(fastmath=True, nopython=True)
    def welfare_single(w1, m1, mt):
        """Welfare function of only one commodity for the What-if analysis."""
        return np.power(w1, m1 / mt)

    @staticmethod
    @numba.njit(fastmath=True, nopython=True)
    def mrs(w1, m1, w2, m2):
        """Welfare function of only one commodity for the What-if analysis."""
        return np.devide(np.multiply(w1, m2), np.multiply(w2, m1))

    @staticmethod
    def get_selling_neigh(buyer, sellers):  # TODO define sellers
        """
            Returns set of selling neighbours.
        """
        neighbours = set(buyer.grid.get_neighbors(buyer))
        selling_neigh = neighbours.intersection(set(sellers))
        return selling_neigh

    def init_test_pop(self):
        """Initial test population."""
        netherlands_metab = {"energy": 0.1, "money": 0.1}
        netherlands_wealth = {"energy": 0.5, "money": 0.6}

        poland_metab = {"energy": 0.1, "money": 0.1}
        poland_wealth = {"energy": 0.7, "money": 0.2}

        germany_metab = {"energy": 0.1, "money": 0.1}
        germany_wealth = {"energy": 0.4, "money": 0.7}

        NL = country.Country(metabolism=netherlands_metab, wealth=netherlands_wealth)
        PO = country.Country(metabolism=poland_metab, wealth=poland_wealth)
        GE = country.Country(metabolism=germany_metab, wealth=germany_wealth)

        # create germany, netherlands and poland
        # assign rand attributes


if __name__ == "__main__":
    new = GeoModel()
    new.run_model(5)
    data = new.data_collector.get_model_vars_dataframe()
    print(data)
    data.plot()
    plt.show()
