import unittest
import numpy as np
import mesa_geo as mg
from country2 import Country

class TestCountry(unittest.TestCase):
    def setUp(self):
        self.model = mg.GeoModel()
        self.geometry = mg.Point(0, 0)
        self.crs = 'EPSG:4326'
        self.country = Country('Germay', self.model, self.geometry, self.crs)

    def test_init(self):
        self.assertEqual(self.country.unique_id, 'Test')
        self.assertEqual(self.country.model, self.model)
        self.assertEqual(self.country.geometry, self.geometry)
        self.assertEqual(self.country.crs, self.crs)
        self.assertEqual(self.country.welfare, 0.001)
        self.assertEqual(self.country.mrs, 0.001)
        self.assertEqual(self.country.produced_energy, 0.001)
        self.assertEqual(self.country.influx_money, 0.001)
        self.assertEqual(self.country.w_money, 0.01)
        self.assertEqual(self.country.w_energy, 0.01)
        self.assertEqual(self.country.m_money, 0.1)
        self.assertEqual(self.country.m_energy, 0.1)
        self.assertEqual(self.country.pred_dirty, 0.001)
        self.assertEqual(self.country.pred_clean, 0.001)
        self.assertEqual(self.country.nr_dirty, 0)
        self.assertEqual(self.country.nr_clean, 0)
        self.assertEqual(self.country.predisposition_decrease, 0.0001)
        self.assertEqual(self.country.clean_adoption, 0)
        self.assertEqual(self.country.last_trade_success, False)
        self.assertEqual(self.country.last_trade_price_energy, 100_000_000)
        self.assertEqual(self.country.prob_neigh_influence, self.model.prob_neigh_influence)
        self.assertEqual(self.country.output_single_dirty, 0.001)
        self.assertEqual(self.country.output_single_clean, 0.001)
        self.assertEqual(self.country.cost_dirty, 0.001)
        self.assertEqual(self.country.cost_clean, 0.001)
        self.assertEqual(self.country.seed, self.model.seed)

    def test_repr(self):
        self.assertEqual(self.country.__repr__(), "Country: Germany")

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
