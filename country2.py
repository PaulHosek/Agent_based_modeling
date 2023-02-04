import mesa
import mesa_geo as mg
import typing
import geo_model
import numpy as np
import math


class Country(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, crs,
                 m_energy=0.1, m_money=0.1, w_energy=0.01, w_money=0.01, predisposition_decrease=0.0001):

        """
        :param unique_id: Name of country
        :param model:
        :param geometry:
        """
        super().__init__(unique_id, model, geometry, crs)
        # attributes
        self.name: str = 'na'
        # self.metabolism: dict = metabolism
        # self.wealth: dict = wealth
        self.welfare: float = 0.001
        self.mrs: float = 0.001
        self.produced_energy: float = 0.001
        self.influx_money: float = 0.001
        self.w_money = w_money
        self.w_energy = w_energy
        self.m_money = m_money
        self.m_energy = m_energy

        # for later
        self.pred_dirty: float = 0.001
        self.pred_clean: float = 0.001
        self.nr_dirty: int = 0
        self.nr_clean: int = 0
        self.predisposition_decrease = predisposition_decrease

        # attributes set by model
        self.last_trade_success: bool = False
        self.last_trade_price_energy: float = 0.0001  # TODO this should probs not be this
        # base output of single plants as determined by the initialisation
        self.output_single_dirty: float = 0.001
        self.output_single_clean: float = 0.001
        self.cost_dirty: float = 0.001
        self.cost_clean: float = 0.001
        np.random.seed = self.model.seed
        self.seed = self.model.seed

    def __repr__(self):
        return f"Country: {self.unique_id}"

    def step(self) -> None:
        """
        Do agents actions in each step here.
        :return:
        """
        self.collect()
        self.invest()
        self.consume()
        self.calculate_welfare()
        self.calculate_mrs()
        self.reduce_pred()
        self.kill_plant()
        if self.w_energy > 100:
            self.w_energy = 100


    def collect(self) -> None:
        """Collect energy and money from power plants and gdp influx.
        """
        self.w_energy += self.nr_clean * self.pred_clean * self.output_single_clean \
                         + self.nr_dirty * self.pred_dirty * self.output_single_dirty
        self.w_money += self.influx_money

    def invest(self) -> None:
        """
        Decide if we should build a power plant or rely on trading.
        1. Decide if can afford power plant
        2. Do what-if analysis on welfare increase with power plant for both power plants.
        3. Choose power plant that maximises welfare.
        4. Build power plant
        5. Compute new wealth for energy and money.
        """
        # if cant afford any plant

        # if self.cost_clean > self.w_money - 0.1 and self.cost_dirty > self.w_money - 0.1:
        #     return

        if self.cost_clean > self.w_money - (self.w_money * 0.3) \
                and self.cost_dirty > self.w_money - (self.w_money * 0.3):
            return

        if self.build_neighbour_plant():
            return

        # print("COST", self.cost_clean, self.w_money)

        build_d_welfare = self.would_be_welfare("dirty")
        build_c_welfare = self.would_be_welfare("clean")
        trade_d_welfare = self.would_be_welfare("trade_e")
        trade_c_welfare = self.would_be_welfare("trade_m")

        options = [
            [build_d_welfare, self.cost_dirty, "dirty"],
            [build_c_welfare, self.cost_clean, "clean"],
            [trade_d_welfare, 0, "trade"],
            [trade_c_welfare, 0, "trade"]
        ]
        options = [x for x in options if not math.isnan(x[1])]

        # sort options by welfare

        options.sort(reverse=True, key=lambda x: x[0])
        options = sorted(options, reverse=True, key=lambda x: x[0])




        # build their plant
        # skip the rest of the decisio

        # print("Options", options)
        # choose first option we can afford
        best = next((x for x in options if x[1] < self.w_money - (self.w_money * 0.3) and not math.isnan(x[1])),
                    (trade_c_welfare, 0, "trade"))
        if best[2] == "dirty" or best[2] == "clean":
            # print(best[2])
            self.build_plant(best[2])

        # if last trade was not successful, but the best option was trade. Try to build the best plant we can.
        # elif best[2] == "trade" and not self.last_trade_success:
        #     # if there are any plants we can afford, build the one with the highest welfare
        #     best_build = sorted((x for x in options
        #                          if (x[2] == "dirty" or x[2] == "clean") and x[1] < self.w_money - (self.w_money * 0.3)),
        #                         reverse=True, key=lambda x: x[0])
        #     if best_build:
        #         self.build_plant(best_build[0][2])
        # else:
        #     pass
    def build_neighbour_plant(self):
        influence, their_plant = self.neighbour_influence()
        if influence > np.random.default_rng(self.seed+21).uniform():
            if their_plant == "clean" and self.cost_clean > self.w_money - (self.w_money * 0.3):
                self.build_plant("clean")
                return True
            elif their_plant == "dirty" and self.cost_dirty > self.w_money - (self.w_money * 0.3):
                self.build_plant("dirty")
                return True
        return False

    def neighbour_influence(self):

        all_neigh = sorted(self.model.space.get_neighbors(self), key=lambda x: x.welfare, reverse=True)
        if not all_neigh:
            return 0, ""
        best_neigh = all_neigh[0]

        influence = 1-(self.welfare/best_neigh.welfare) if best_neigh.welfare != 0 else 0
        if influence < 0:
            influence = 0
        if best_neigh.nr_dirty > best_neigh.nr_clean:
            plant = "dirty"
        elif best_neigh.nr_dirty < best_neigh.nr_clean:
            plant = "clean"

        # if equal then try to make own plants equal too
        else:
            if self.nr_clean < self.nr_dirty:
                plant = "clean"
            elif self.nr_dirty < self.nr_clean:
                plant = "dirty"
            else:
                return 0, ""

        return influence, plant


        # calculate dominant plant
        # calculate 1-my_welfare/their_welfare => influence factor
        # return influence_factor, plant

    # if influnce_factor > np.random.uniform() and if can afford:
            # build their plant
            # skip the rest of the decision





        # test if my is larger then break or sth

    def would_be_welfare(self, action: str, trading_quantity = 0.1) -> float:
        if action == "dirty":
            add_energy = self.pred_dirty * self.output_single_dirty
            expected_market_cost = self.cost_dirty
        elif action == "clean":
            add_energy = self.pred_clean * self.output_single_clean
            expected_market_cost = self.cost_clean
        elif action == "trade_e":  # TODO make sure right operations
            # sell energy
            add_energy = -trading_quantity
            expected_market_cost = trading_quantity * self.last_trade_price_energy
        elif action == "trade_m":
            # sell money
            add_energy = trading_quantity / self.last_trade_price_energy
            expected_market_cost = - trading_quantity
        else:
            raise ValueError(
                f"Variable action is {action} but can only take values 'dirty', 'clean', 'trade_e' or 'trade_m'.")

        mt = np.add(self.m_energy, self.m_money)

        return np.power(self.w_energy + self.produced_energy + add_energy, self.m_energy / mt) \
               * np.power(self.w_money + expected_market_cost, self.m_money / mt)

    def consume(self) -> None:
        """Use up energy and money"""
        self.w_energy -= self.m_energy
        self.w_money -= self.m_money * self.w_money
        if self.w_energy < 0:
            self.w_energy = 0.01
        if self.w_money < 0:
            self.w_money = 0.01

    def calculate_welfare(self) -> None:
        """
        Calculate welfare according to Cobb-Douglas production formula.
        Include both influx of
        money and produced energy from plants in equation.
        m1 = demand of energy taken from energy consumption data of a country
        m2 = demand of money taken from public expenditure data of a country
        W(e,m) = (energy + production_from_plants) ^ (m1/mt) * (money + influx from gdp) ^ (m2/mt)
        """

        mt = np.add(self.m_energy, self.m_money)

        w_energy = np.power(np.add(self.w_energy, self.produced_energy),
                            np.divide(self.m_energy, mt))
        w_money = np.power(np.add(self.w_money, self.influx_money),
                           np.divide(self.m_money, mt))

        for i in [w_money, w_energy]:
            if isinstance(i, complex):
                i = 0

        self.welfare = np.multiply(w_money, w_energy)

    def calculate_mrs(self) -> None:
        """Calculate Marginal Rate of Substitution (MRS)."""
        self.mrs = np.divide(np.multiply(np.add(self.w_energy, self.produced_energy), self.m_money),
                             np.multiply(np.add(self.w_money, self.influx_money), self.m_energy))

    def build_plant(self, type_plant: str):
        """
        Build some plant,
        :param: type_plant: The plant to build. Either "dirty" or "clean".
        :return:
        """
        if type_plant == "dirty":
            self.nr_dirty += 1
            self.w_money -= self.cost_dirty
        elif type_plant == 'clean':
            self.nr_clean += 1
            self.w_money -= self.cost_clean
        else:
            raise ValueError(f"""{type_plant} is not a valid plant. Use the tag "dirty" or "clean".""")

    def kill_plant(self):
        # for plant in [self.nr_dirty, self.nr_clean]:
        if 0.2 > np.random.default_rng(self.seed+22).random() and self.nr_dirty > 0:
            self.nr_dirty -= 1
        if 0.2 > np.random.default_rng(self.seed+23).random() and self.nr_clean > 0:
            self.nr_clean -= 1

    def reduce_pred(self):
        """
        Reduce predisposition of dirty power based on how many power plants consume it.
        """
        self.pred_dirty -= self.nr_dirty * self.predisposition_decrease
        if self.pred_dirty < 0:
            self.pred_dirty = 0
