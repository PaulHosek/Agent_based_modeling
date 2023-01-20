import mesa
import mesa_geo as mg
import typing
import geo_model
import numpy as np
import numba

class Country(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, crs,
                 metabolism = {"energy":1,"money":1}, wealth = {"energy":1,"money":1}):
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
        self.calculate_welfare()
        self.calculate_mrs()


        # for later
        self.pred_dirty: float = 0.0
        self.pred_clean: float = 0.0
        self.nr_dirty: int = 0
        self.nr_clean: int = 0

        # attributes set by model
        self.cost_dirty: float = 0.0
        self.cost_clean: float = 0.0

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
        self.eat() # get energy and money for the time step
        self.consume() # consume energy
        self.calculate_welfare()
        self.calculate_mrs()


    def eat(self)->None:
        """Generate energy and money."""
        self.wealth['energy'] += self.metabolism["energy"]
        self.wealth['money'] += self.metabolism["money"]

    def consume(self)->None:
        """Use up energy and money"""
        self.wealth['energy'] -= self.metabolism["energy"]
        self.wealth['money'] -= self.metabolism["money"]
        if self.wealth['energy'] < 0:
            self.wealth['energy'] = 0
        if self.wealth['money'] < 0:
            self.wealth['money'] = 0

    # @numba.jit(fastmath=True, nopython=False)
    def calculate_welfare(self) -> None:
        """Calculate what action to take based on predispositions,
         energy level, money and last step's outcome.
        """
        mt = np.add(self.metabolism["money"], self.metabolism["energy"])
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
                         np.multiply(self.wealth["money"], self.metabolism["energy"])) # IS THIS CORRECT?



    def build_plant(self, type_plant="dirty"):
        """
        Build some plant,
        :return:
        """
        if type_plant == "dirty":
            self.nr_dirty += 1
            self.money -= self.cost_dirty
        elif type_plant == 'clean':
            self.nr_clean += 1
            self.money -= self.cost_clean
        else:
            raise ValueError(f"""{type_plant} is not a valid plant. Use the tag "dirty" or "clean".""")

    def get_selling_neighbour(self):
        """
        Get a neighbour that sells.
        :return:
        """
        pass

    def get_neighbor(self):
        """
        Get a list of neighbours.
        :return:
        """

    def do_trade(self, neighbor_id):
        """
        Do trade for energy with selling neighbor.

        """
        pass

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