import unittest
import mesa_geo as mg
from country import Country
import geo_model


class TestCountry(unittest.TestCase):

    def setUp(self):
        self.model = geo_model.GeoModel()
        self.country = Country("test_country", self.model, None) # TODO change this to real country, same below.

    def test_init(self):
        self.assertEqual(self.country.unique_id, "test_country")
        self.assertEqual(self.country.money, 0)
        self.assertEqual(self.country.name, 'na')
        self.assertEqual(self.country.e_demand, 0)
        self.assertEqual(self.country.pred_dirty, 0)
        self.assertEqual(self.country.pred_clean, 0)
        self.assertEqual(self.country.nr_dirty, 0)
        self.assertEqual(self.country.nr_clean, 0)
        self.assertEqual(self.country.perc_energy_met, 0)

    def test_load_country(self):
        self.assertIsNone(self.country.load_country("test_country"))

    def test_step(self):
        self.country.step()
        self.assertIsNone(self.country.step())

    def test_calculate_welfare(self):
        self.assertIsNone(self.country.calculate_welfare())

    def test_evaluate_energy(self):
        self.assertIsNone(self.country.evaluate_energy())

    def test_build_plant(self):
        self.country.build_plant("dirty")
        self.assertEqual(self.country.nr_dirty, 1)
        self.assertEqual(self.country.money, -self.country.cost_dirty)
        self.country.build_plant("clean")
        self.assertEqual(self.country.nr_clean, 1)
        self.assertEqual(self.country.money, -(self.country.cost_clean + self.country.cost_dirty))

    def test_get_selling_neighbour(self):
        self.assertIsNone(self.country.get_selling_neighbour())

    def test_get_neighbor(self):
        self.assertIsNone(self.country.get_neighbor())

    def test_do_trade(self):
        self.assertIsNone(self.country.do_trade("test_neighbor"))

    def test_repr(self):
        self.assertEqual(self.country.__repr__(), "Country: test_country")
