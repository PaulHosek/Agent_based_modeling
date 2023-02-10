import unittest
from geo_model2 import GeoModel

class TestModel(unittest.TestCase):
    def test_init(self):
        cost_clean = 0.02
        cost_dirty = 0.02
        base_output_dirty = 0.8
        base_output_clean = 0.4
        metabolism_scalar_energy = 1
        metabolism_scalar_money = 1
        eta_global_trade = 0.01
        predisposition_decrease = 0.0001
        pareto_optimal = False
        seed = 18775
        prob_neigh_influence = 0
        tax = False

        model = GeoModel(cost_clean, cost_dirty, base_output_dirty, base_output_clean,
                         metabolism_scalar_energy, metabolism_scalar_money, eta_global_trade,
                         predisposition_decrease, pareto_optimal, seed, prob_neigh_influence, tax)

        self.assertEqual(model.cost_clean, cost_clean)
        self.assertEqual(model.cost_dirty, cost_dirty)
        self.assertEqual(model.base_output_dirty, base_output_dirty)
        self.assertEqual(model.base_output_clean, base_output_clean)
        self.assertEqual(model.metabolism_scalar_energy, metabolism_scalar_energy)
        self.assertEqual(model.metabolism_scalar_money, metabolism_scalar_money)
        self.assertEqual(model.eta_global_trade, eta_global_trade)
        self.assertEqual(model.predisposition_decrease, predisposition_decrease)
        self.assertEqual(model.pareto_optimal, pareto_optimal)
        self.assertEqual(model.seed, seed)
        self.assertEqual(model.prob_neigh_influence, prob_neigh_influence)
        self.assertEqual(model.tax, tax)

    def setUp(self):
        pass

    def test_step(self):
        model = GeoModel()

        model.step()
        self.assertEqual(model.step_nr, 1)
        model.step()
        self.assertEqual(model.step_nr, 2)

        with unittest.mock.patch.object(model, 'schedule') as mock_schedule, \
             unittest.mock.patch.object(model, 'trading_cycle') as mock_trading_cycle, \
             unittest.mock.patch.object(model, 'tax_dirty') as mock_tax_dirty, \
             unittest.mock.patch.object(model, 'log_data') as mock_log_data:
            model.step()
            mock_schedule.assert_called_once()
            mock_trading_cycle.assert_called_once()
            if model.tax:
                mock_tax_dirty.assert_called_once()
            mock_log_data.assert_called_once()

    def test_trading_cycle(self):
        model = Geomodel()

        with unittest.mock.patch('random.choice') as mock_choice, \
             unittest.mock.patch('random.random') as mock_random, \
             unittest.mock.patch('math.isnan') as mock_isnan, \
             unittest.mock.patch.object(model.space, 'get_neighbors') as mock_get_neighbors:
            mock_random.return_value = model.eta_trading + 0.1
            mock_choice.return_value = model.agents[0]
            mock_isnan.return_value = False
            mock_get_neighbors.return_value = model.agents

            model.trading_cycle()
            mock_random.assert_called_once()
            mock_choice.assert_called_once()
            mock_isnan.assert_called_once()
            mock_get_neighbors.assert_called_once()

if __name__ == '__main__':
    unittest.main()
