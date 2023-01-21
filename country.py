import mesa
import mesa_geo as mg
import typing
import geo_model
import numpy as np
import numba


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
        self.cost_dirty: float = 0.0
        self.cost_clean: float = 0.0
        self.output_dirty: float = 0.0
        self.output_clean: float = 0.0

        self.load_country(id)

    def __repr__(self):
        return f"Country: {self.unique_id}"

    def load_country(self, unique_id):
        """
        Initialise the country and fill the attributes from csv.
        :return: None
        """
        pass

    def step(self) -> None:
        """
        Do agents actions in each step here.
        :return:
        """
        # self.collect()
        # self.build()
        self.eat()
        self.consume()  # consume energy
        self.calculate_welfare()
        self.calculate_mrs()

    def collect(self) -> None:
        """Collect energy and money from power plants and gdp influx.
        """
        self.produced_energy = self.nr_clean * self.pred_clean \
                               + self.nr_dirty * self.pred_dirty
        self.wealth["energy"] += self.produced_energy

        self.wealth["money"] += self.influx_money

    def build(self) -> None:
        """
        1. Decide if can afford power plant
        2. Do what-if analysis on welfare increase with power plant for both power plants.
        3. Choose power plant that maximises welfare.
        4. Build power plant
        5. Compute new wealth for energy and money.
        """
        if self.cost_clean < self.wealth["money"] or self.cost_dirty < self.wealth["money"]:
            return None
        dirty_welfare = self.would_be_welfare("dirty")
        clean_welfare = self.would_be_welfare("clean")

        if dirty_welfare > self.welfare and dirty_welfare > self.welfare:
            # choose the one that maximises welfare
            pass
        elif dirty_welfare > self.welfare:
            # build dirty
            pass
        elif clean_welfare > self.welfare:
            # build clean
            pass
        else:
            return None

    def would_be_welfare(self, plant_type: str):
        """
        Calculate welfare that would be achieved by building a specific plant and trade.

        :param plant_type: either "dirty" or "clean"
        :return:
        """





    # def calc_effective_welfare(self) -> None:
    #     """
    #     Calculate welfare. Include both influx of
    #     money and produced energy from plants in equation.
    #     """
    #     m_energy = self.metabolism["energy"] - self.produced_energy
    #     m_money = self.metabolism["money"] - self.influx_money
    #     mt = np.add(m_energy, m_money)
    #     # print(self.wealth['energy'], self.metabolism["energy"], mt)
    #
    #     w_energy = np.power(self.wealth['energy'], np.divide(m_energy, mt))
    #     w_money = np.power(self.wealth['money'], np.divide(m_money, mt))
    #
    #     for i in [w_money, w_energy]:
    #         if isinstance(i, complex):
    #             i = 0
    #
    #     self.welfare = np.multiply(w_money, w_energy)



    def eat(self) -> None:
        """Generate energy and money."""
        self.wealth['energy'] += self.metabolism["energy"]
        self.wealth['money'] += self.metabolism["money"]

    def consume(self) -> None:
        """Use up energy and money"""
        self.wealth['energy'] -= self.metabolism["energy"]
        self.wealth['money'] -= self.metabolism["money"]
        if self.wealth['energy'] < 0:
            self.wealth['energy'] = 0.01
        if self.wealth['money'] < 0:
            self.wealth['money'] = 0.01

    # @numba.jit(fastmath=True, nopython=False)
    def calculate_welfare(self) -> None:
        """Calculate what action to take based on predispositions,
         energy level, money and last step's outcome.
        """
        mt = np.add(self.metabolism["money"], self.metabolism["energy"])
        # print(self.wealth['energy'], self.metabolism["energy"], mt)

        w_energy = np.power(self.wealth['energy'], np.divide(self.metabolism["energy"], mt))
        w_money = np.power(self.wealth['money'], np.divide(self.metabolism["money"], mt))

        for i in [w_money, w_energy]:
            if isinstance(i, complex):
                i = 0

        self.welfare = np.multiply(w_money, w_energy)


    # @numba.jit(fastmath=True, nopython=True)
    def calculate_mrs(self) -> None:
        """Calculate Marginal Rate of Substitution (MRS)."""
        self.mrs = np.divide(np.multiply(self.wealth["energy"], self.metabolism["money"]),
                             np.multiply(self.wealth["money"], self.metabolism["energy"]))  # IS THIS CORRECT?

    def build_plant(self, type_plant="dirty"):
        """
        Build some plant,
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
