from itertools import combinations

import matplotlib.pyplot as plt
from IPython.display import clear_output
import SALib
from SALib.sample import saltelli, sobol
from SALib.analyze import sobol
import pandas as pd
import geo_model
from geo_model import *
import numpy as np
import time

now = time.time()

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
     'bounds': [[0.001,  1], [0.001,  1], [0.001,  1], [0.001,  1], [0.001, 2], [0.001, 2], [0.001, 1], [0.001, 1]]}

#replicates = 3
#max_steps = 100
distinct_samples = 256 #N    N(D+2) rows output


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


samples.to_csv("Sobol_256_new.csv")

# TODO slice your region here before removing the KeyboardIntterupt

raise KeyboardInterrupt

#just testing

print(samples)
avg_last_welfare = []
avg_last_price = []

for i in range(len(samples)):
    new = geo_model.GeoModel(cost_clean=samples.iloc[i][0],
                             cost_dirty=samples.iloc[i][1],
                             base_output_dirty=samples.iloc[i][2],
                             base_output_clean=samples.iloc[i][3],
                             metabolism_scalar_energy= samples.iloc[i][4],
                             metabolism_scalar_money= samples.iloc[i][5],
                             eta_global_trade= samples.iloc[i][6],
                             predisposition_decrease= samples.iloc[i][7])
    new.run_model(10)
    nw1 = new.datacollector.get_agent_vars_dataframe()
    # nw2 = new.datacollector.get_model_vars_dataframe()

    #nw2 = new.datacollector.get_model_vars_dataframe()
    df_by_country_welfare = nw1.pivot_table(values = 'Welfare', columns = 'AgentID', index = 'Step')
    #df_by_country_price = nw2.pivot_table(values = 'Price', columns = 'AgentID', index = 'Price')
    #print(df_by_country_price)
    #last_state = df_by_country.iloc[-1]
    avg_last_welfare.append(np.mean(df_by_country_welfare.iloc[-1]))
    # avg_last_price.append(nw2.iloc[-1][0])

    #print(np.mean(avg_last_welfare))
#print(len(avg_last_price))

outputs1 = pd.DataFrame(data = avg_last_welfare,
        columns = ['output_welfare'])

# outputs2 = pd.DataFrame(data = avg_last_price,
#         columns = ['output_price'])

print(outputs1)
# print(outputs2)

S_i_welfare = sobol.analyze(problem, outputs1['output_welfare'].values, print_to_console=True, calc_second_order=False)
#print(S_i_welfare)

# S_i_price = sobol.analyze(problem, outputs2['output_price'].values, print_to_console=True, calc_second_order=False)
#print(S_i_price)

def plot_index(s, params, i, title=''):
    """
    Creates a plot for Sobol sensitivity analysis that shows the contributions
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
plt.figure()
for Si in [S_i_welfare]:
    # First order
    plot_index(Si, problem['names'], '1', 'Welfare First order sensitivity')
    # plt.show()
    # Second order
    # plot_index(Si, problem['names'], '2', 'Second order sensitivity')
    #     plt.show()
    # Total order
    plot_index(Si, problem['names'], 'T', 'Welfare Total order sensitivity')
    #plt.show()


# for S in [S_i_price]:
#     # First order
#     plot_index(S, problem['names'], '1', 'Price First order sensitivity')
#     # plt.show()
#     # Second order
#     # plot_index(S, problem['names'], '2', 'Second order sensitivity')
#     #     plt.show()
#     # Total order
#     plot_index(S, problem['names'], 'T', 'Price Total order sensitivity')
print(time.time() - now)
plt.show()