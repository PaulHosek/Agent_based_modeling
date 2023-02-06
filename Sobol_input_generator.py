from SALib.sample import saltelli
import pandas as pd

problem = {
    'num_vars': 8,
    'names': [
     'cost_clean',
     'cost_dirty',
     'base_output_dirty',
     'base_output_clean',
     'metabolism_scalar_energy',
     'metabolism_scalar_money',
     'eta_global_trade',
    'predisposition_decrease'],
     'bounds': [[0.001,  1], [0.001,  1], [0.001,  1], [0.001,  1], [0.8, 1.2], [0.8, 1.2], [0.001, 1], [0.001, 1]]}

distinct_samples = 1024   #N  --> N(D+2) rows output

param_values = saltelli.sample(problem, distinct_samples, calc_second_order= False)
#print(param_values)

samples = pd.DataFrame(data=param_values,
                       columns=['cost_clean',
                                'cost_dirty',
                                'base_output_dirty',
                                'base_output_clean',
                                'metabolism_scalar_energy',
                                'metabolism_scalar_money',
                                'eta_global_trade',
                                'predisposition_decrease'])


samples.to_csv("Sobol_inputs.csv")