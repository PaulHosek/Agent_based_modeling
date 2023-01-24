import mesa
import mesa_geo as mg
import typing
import geo_model
import numpy as np
import numba as nb


class Country(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, crs,
                 metabolism={"energy": 1, "money": 1}, wealth={"energy": 1, "money": 1}):
        """

        :param unique_id: Name of country
        :param model:
        :param geometry:
        """
        super().__init__(unique_id, model, geometry, crs)
        # attributes
        self.name: str = 'na'
        self.metabolism: dict = metabolism
        self.wealth: dict = wealth
        self.welfare: float = 0.0
        self.mrs: float = 0.0
        self.produced_energy: float = 0.0
        self.influx_money: float = 0.0

        # for later
        self.pred_dirty: float = 0.0
        self.pred_clean: float = 0.0
        self.nr_dirty: int = 0
        self.nr_clean: int = 0

        # attributes set by model
        self.last_trade_success: bool = False
        self.last_trade_price_energy: float = 0.0001
        # base output of single plants as determined by the initialisation
        self.output_single_dirty: float = 0.0
        self.output_single_clean: float = 0.0
        self.cost_dirty: float = 0.0
        self.cost_clean: float = 0.0

    def __repr__(self):
        return f"Country: {self.unique_id}"

    def step(self) -> None:
        """
        Do agents actions in each step here.
        :return:
        """
        self.collect()
        self.invest()
        # self.eat()
        self.consume()  # consume energy
        self.calculate_welfare()  # TODO update this to the new welfare function
        self.calculate_mrs()
        self.reduce_pred()

    def collect(self) -> None:
        """Collect energy and money from power plants and gdp influx.
        """
        self.wealth["energy"] += self.nr_clean * self.pred_clean \
                                 + self.nr_dirty * self.pred_dirty
        self.wealth["money"] += self.influx_money

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
        if self.cost_clean > self.wealth["money"] - 0.3 and self.cost_dirty > self.wealth["money"] - 0.3:
            return

        build_d_welfare = self.would_be_welfare("dirty")
        build_c_welfare = self.would_be_welfare("clean")
        trade_d_welfare = self.would_be_welfare("trade_e")
        trade_c_welfare = self.would_be_welfare("trade_m")
        # TODO compare trade for energy or trade for money
        # TODO also include option of doing nothing
        # TODO clean this up

        options = [
            (build_d_welfare, self.cost_dirty, "dirty", "build"),
            (build_c_welfare, self.cost_clean, "clean", "build"),
            (trade_d_welfare, 0, "trade", "energy"),
            (trade_c_welfare, 0, "trade", "money"),
            (self.welfare, 0, "nothing", "nothing")
        ]
        # print(options)
        # print(self.nr_dirty,self.nr_clean)

        # sort options by welfare
        options.sort(reverse=True, key=lambda x: x[0])
        # choose first option we can afford
        best = next((x for x in options if x[1] < self.wealth["money"] - 0.3),
                    (trade_c_welfare, 0, "clean", "trade"))
        # print(self.nr_dirty,self.nr_clean)

        if best[3] == "build":
            self.build_plant(best[2])

        # if last trade was not successful, but the best option was trade. Try to build the best plant we can.
        elif best[3] == "trade" and not self.last_trade_success:
            # if there are any plants we can afford, build the one with the highest welfare
            best_build = sorted((x for x in options
                                 if x[3] == "build" and x[1] < self.wealth["money"] - 0.3),
                                reverse=True, key=lambda x: x[0])
            if best_build:
                self.build_plant(best_build[0][2])
        else:
            pass

        return

    import numpy as np

    def would_be_welfare(self, action: str) -> float:
        if action == "dirty":
            add_plant_energy = self.pred_dirty * self.output_single_dirty
            expected_market_cost = self.cost_dirty
        elif action == "clean":
            add_plant_energy = self.pred_clean * self.output_single_clean
            expected_market_cost = self.cost_clean
        elif action == "trade_e" or action == "trade_m":
            add_plant_energy = 0
            expected_market_cost = 0
        else:
            raise ValueError(
                f"Variable action is {action} but can only take values 'dirty', 'clean', 'trade_e' or 'trade_m'.")

        if action == "trade_e":
            expected_market_cost = 0.1 * self.last_trade_price_energy
            add_plant_energy = 0.1
        elif action == "trade_m":
            expected_market_energy = 0.1 / self.last_trade_price_energy
            add_plant_energy = -expected_market_energy

        mt = np.add(self.metabolism["energy"], self.metabolism["money"])
        return np.power(self.wealth["energy"] + self.produced_energy + add_plant_energy,
                           self.metabolism["energy"] / mt) * np.power(self.wealth["money"] - expected_market_cost,
                                                                      self.metabolism["money"] / mt)

    def would_be_welfare(self, action: str) -> float:
        """
        Calculate welfare that would be achieved by building a specific plant and trade.
        Assume that we trade for maximum trading volume of 0.1 Energy at the market price of last time.

        Note that the welfare functions are not adding self.influx_money, because this has happened already in this step.
        This means, the wealth["money"] was already updated

        :param action: What to do: Build a power plant with "dirty", "clean" or trade with "trade_e" or "trade_m".
        :return:
        """

        if action == "dirty":
            add_plant_energy = self.pred_dirty * self.output_single_dirty
        elif action == "clean":
            add_plant_energy = self.pred_clean * self.output_single_clean
        elif action == "trade_e" or action == "trade_m":
            pass
        else:
            raise ValueError(f"""Variable action is {action}
             but can only take values "dirty", "clean", "trade_e" or "trade_m".""")

        # build a plant
        if action == "dirty" or action == "clean":
            mt = np.add(self.metabolism["energy"], self.metabolism["money"])
            return (self.wealth["energy"] + self.produced_energy + add_plant_energy)\
                   ** (self.metabolism["energy"] / mt) \
                   * (self.wealth["money"] - self.cost_dirty)\
                   ** (self.metabolism["money"] / mt)  # no influx money, see Docstring

        # buy energy
        elif action == "trade_e":
            expected_market_cost = 0.1 * self.last_trade_price_energy  # * add_plant_energy
            mt = np.add(self.metabolism["energy"], self.metabolism["money"])
            return (self.wealth["energy"] + self.produced_energy + 0.1)\
                   ** (self.metabolism["energy"] / mt) \
                   * (self.wealth["money"] - expected_market_cost)\
                   ** (self.metabolism["money"] / mt)  # no influx money, see Docstring

        # sell energy
        elif action == "trade_m":
            expected_market_energy = 0.1 / self.last_trade_price_energy  # * add_plant_energy
            mt = np.add(self.metabolism["energy"], self.metabolism["money"])
            return (self.wealth["energy"] + self.produced_energy - expected_market_energy)\
                   ** (self.metabolism["energy"] / mt) \
                   * (self.wealth["money"] + self.influx_money + 0.1)\
                   ** (self.metabolism["money"] / mt)

    def consume(self) -> None:
        """Use up energy and money"""
        self.wealth['energy'] -= self.metabolism["energy"]
        self.wealth['money'] -= self.metabolism["money"]
        if self.wealth['energy'] < 0:
            self.wealth['energy'] = 0.01
        if self.wealth['money'] < 0:
            self.wealth['money'] = 0.01

    def calculate_welfare(self) -> None:
        """
        Calculate welfare according to Cobb-Douglas production formula.
        Include both influx of
        money and produced energy from plants in equation.
        m1 = demand of energy taken from energy consumption data of a country
        m2 = demand of money taken from public expenditure data of a country
        W(e,m) = (energy + production_from_plants) ^ (m1/mt) * (money + influx from gdp) ^ (m2/mt)
        """

        mt = np.add(self.wealth["energy"], self.wealth["money"])

        w_energy = np.power(np.add(self.wealth['energy'], self.produced_energy),
                            np.divide(self.metabolism["energy"], mt))
        w_money = np.power(np.add(self.wealth["money"], self.influx_money),
                           np.divide(self.metabolism["money"], mt))

        for i in [w_money, w_energy]:
            if isinstance(i, complex):
                i = 0

        self.welfare = np.multiply(w_money, w_energy)

    # @numba.jit(fastmath=True, nopython=True)
    def calculate_mrs(self) -> None:  # TODO adjust to new wealth function
        """Calculate Marginal Rate of Substitution (MRS)."""
        self.mrs = np.divide(np.multiply(self.wealth["energy"], self.metabolism["money"]),
                             np.multiply(self.wealth["money"], self.metabolism["energy"]))  # IS THIS CORRECT?

    def build_plant(self, type_plant: str):
        """
        Build some plant,
        :param: type_plant: The plant to build. Either "dirty" or "clean".
        :return:
        """
        if type_plant == "dirty":
            self.nr_dirty += 1
            self.wealth["money"] -= self.cost_dirty
        elif type_plant == 'clean':
            self.nr_clean += 1
            self.wealth["money"] -= self.cost_clean
        else:
            raise ValueError(f"""{type_plant} is not a valid plant. Use the tag "dirty" or "clean".""")

    ##########################################################################
    #
    #          Functions for later
    #
    #########################################################################

    # def decide_build(self) -> int:
    #     """
    #     Decide if build plant and which one.
    #     0 = build no plant
    #     1 = build dirty
    #     2 = build clean
    #     :return: 0,1,2
    #     """
    #     # calculate cost of only trading, based on last turn's average trade cost
    #     # calculate cost of buying a green plant and trading for the rest
    #     # calculate cost of buying a dirty plant and trading for the rest
    #     pass

    # def evaluate_energy(self):
    #     """
    #     Calculate the current energy percentage met based on nr plants and their output.
    #     :return:
    #     """
    #     pass
    def reduce_pred(self):
        """
        Reduce predisposition of ditry power based on how many power plants consume it.


        """
        self.pred_dirty -= self.nr_dirty * 0.005