import mesa
import mesa_geo as mg
import typing

import geo_model


class Country(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry):
        """

        :param unique_id: Name of country
        :param model:
        :param geometry:
        """
        super().__init__(unique_id, model, geometry)
        self.money: float = 0
        self.name: str = 'na'
        self.e_demand: float = 0
        self.pred_dirty: float = 0
        self.pred_clean: float = 0
        self.nr_dirty: int = 0
        self.nr_clean: int = 0
        self.perc_energy_met: float = 0

        # attributes set by model
        self.cost_dirty: float = 0
        self.cost_clean: float = 0

        self.load_country(id)

    def __repr__(self):
        return f"Country: {self.unique_id}"

    def load_country(self, unique_id):
        """
        Initialise the country and fill the attributes from csv.
        :return: None
        """
        pass

    def step(self):
        """
        Do agents actions in each step here.
        :return:
        """
        # decide if build plant or not
        # do trading

        pass

    def calculate_welfare(self):
        """Calculate what action to take based on predispositions,
         energy level, money and last step's outcome.
        """
        pass

    def evaluate_energy(self):
        """
        Calculate the current energy percentage met based on nr plants and their output.
        :return:
        """
        pass

    def build_plant(self,type_plant="dirty"):
        """
        Build some plant,
        :return:
        """
        if type_plant=="dirty":
            self.nr_dirty += 1
            self.money -= self.cost_dirty
        elif type_plant == 'clean':
            self.nr_clean += 1
            self.money -= self.cost_clean
        else:
            raise ValueError(f"""{type_plant} is not a valid plant. Use the tag "dirty" or "clean".""")
        self.perc_energy_met = self.evaluate_energy()


    def get_selling_neighbour(self):
        """
        Get a neighbour that sells.
        :return:
        """
        pass

    def do_trade(self, neighbor_id):
        """
        Do trade for energy with selling neighbor.

        """
        pass





