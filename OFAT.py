from itertools import combinations

import matplotlib.pyplot as plt
from IPython.display import clear_output
import SALib
from SALib.sample import saltelli, sobol
from SALib.analyze import sobol
import pandas as pd
import geo_model
import numpy as np


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
     'bounds': [[0, 1], [0, 1], [0, 1], [0,1], [0,1], [0,1], [0,1], [0,1]]}

#replicates = 3
#max_steps = 100
distinct_samples = 2 #N    N(D+2) rows output


param_values = saltelli.sample(problem, distinct_samples, calc_second_order= False)
#print(param_values)


#count = 0
samples = pd.DataFrame(data=param_values,
                       columns=['cost_clean',
                                'cost_dirty',
                                'base_output_dirty',
                                'base_output_clean',
                                'metabolism_scalar_energy',
                                'metabolism_scalar_money',
                                'eta_global_trade',
                                'predisposition_decrease'])

#just testing

print(samples)
avg_last_state = []
for i in range(len(samples)):
    new = geo_model.GeoModel(cost_clean=samples.iloc[i][0],
                             cost_dirty=samples.iloc[i][1],
                             base_output_dirty=samples.iloc[i][2],
                             base_output_clean=samples.iloc[i][3],
                             metabolism_scalar_energy= samples.iloc[i][4],
                             metabolism_scalar_money= samples.iloc[i][5],
                             eta_global_trade= samples.iloc[i][6],
                             predisposition_decrease= samples.iloc[i][7],)

    nw = new.datacollector.get_agent_vars_dataframe()
    df_by_country = nw.pivot_table(values = 'Welfare', columns = 'AgentID', index = 'Step')
    # print(df_by_country)
    #last_state = df_by_country.iloc[-1]

    avg_last_state.append(np.mean(df_by_country.iloc[-1]))

    #print(np.mean(last_state))

outputs = pd.DataFrame(data = avg_last_state,
        columns = ['output'])


S_i = sobol.analyze(problem, outputs['output'].values, print_to_console=True, calc_second_order=False)
print(S_i)

def plot_index(s, params, i, title=''):
    """
    Creates a plot for OFAT sensitivity analysis that shows the contributions
    of each parameter to the global sensitivity.

    Args:
        s (dict): dictionary {'S#': dict, 'S#_conf': dict} of dicts that hold
            the values for a set of parameters
        params (list): the parameters taken from s
        i (str): string that indicates what order the sensitivity is.
        title (str): title for the plot
    """

    if i == '2':
        p = len(params)
        params = list(combinations(params, 2))
        indices = s['S' + i].reshape((p ** 2))
        indices = indices[~np.isnan(indices)]
        errors = s['S' + i + '_conf'].reshape((p ** 2))
        errors = errors[~np.isnan(errors)]
    else:
        print('S' + i)
        indices = s['S' + i]
        errors = s['S' + i + '_conf']
        plt.figure()

    l = len(indices)

    plt.title(title)
    plt.ylim([-0.2, len(indices) - 1 + 0.2])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o')
    plt.axvline(0, c='k')

for Si in [S_i]:
    # First order
    plot_index(Si, problem['names'], '1', 'First order sensitivity')
    # plt.show()
    # Second order
    # plot_index(Si, problem['names'], '2', 'Second order sensitivity')
    #     plt.show()
    # Total order
    plot_index(Si, problem['names'], 'T', 'Total order sensitivity')
    plt.show()
# plt.figure()
# plt.plot(avg_last_state)
plt.show()