import unittest
import mesa
import mesa_geo as mg
from trash import country, geo_model


class TestGeoModel(unittest.TestCase):
    def test_init(self):
        model = geo_model.GeoModel()
        self.assertIsInstance(model.schedule, mesa.time.RandomActivation)
        self.assertIsInstance(model.grid, mg.GeoSpace)
        self.assertIsInstance(model.agents[0], country.Country)
        self.assertEqual(model.step_nr, 0)
        self.assertIsNotNone(model.data_collector)

    def test_log_data(self):
        model = geo_model.GeoModel()
        self.assertIsNone(model.log_data())

    def test_step(self):
        model = geo_model.GeoModel()
        model.step()
        self.assertEqual(model.step_nr, 1)
        self.assertEqual(model.agents[0].perc_energy_met, 0)
        # self.assertEqual(model.agents[0].pred_dirty, 2394)

    def test_add_agents(self):
        model = geo_model.GeoModel()
        self.assertEqual(len(model.grid.agents), len(model.agents))
