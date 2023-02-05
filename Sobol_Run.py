from itertools import combinations
import matplotlib.pyplot as plt
from IPython.display import clear_output
import SALib
from SALib.sample import saltelli, sobol
from SALib.analyze import sobol
import pandas as pd
import geo_model2
from geo_model2 import *
from Sobol_input_generator import *
import numpy as np
import time

samples = pd.read_csv("Sobol_inputs.csv", index_col=0)
# samples = samples[:51]      # PAUL
# samples = samples[51:102]   # SOUVIK
# samples = samples[102:153]  # TIJN
# samples = samples[153:159]  # CONOR #204
# samples = samples[204:]     # GAIA

# print(samples)

# TODO slice your region here before removing the KeyboardIntterupt

#raise KeyboardInterrupt

avg_last_welfare = []
gini_list = []
modularity_list = []

for i in range(len(samples)):
    new = geo_model2.GeoModel(cost_clean=samples.iloc[i][0],
                             cost_dirty=samples.iloc[i][1],
                             base_output_dirty=samples.iloc[i][2],
                             base_output_clean=samples.iloc[i][3],
                             metabolism_scalar_energy= samples.iloc[i][4],
                             metabolism_scalar_money= samples.iloc[i][5],
                             eta_global_trade= samples.iloc[i][6],
                             predisposition_decrease= samples.iloc[i][7])

    steps = 5
    new.run_model(steps)

    nw1 = new.datacollector.get_agent_vars_dataframe()
    nw2 = new.datacollector.get_model_vars_dataframe()

    last_gini = nw2["Gini_welfare"][steps]
    gini_list.append(last_gini)

    last_modularity = nw2["modularity_ga"][steps]
    modularity_list.append(last_modularity)

    df_by_country_welfare = nw1.pivot_table(values = 'Welfare', columns = 'AgentID', index = 'Step')
    df_by_country_gini = nw1.pivot_table(values='Welfare', columns='AgentID', index='Step')
    df_by_country_mod = nw1.pivot_table(values='Welfare', columns='AgentID', index='Step')

    avg_last_welfare.append(np.mean(df_by_country_welfare.iloc[-1]))

output_welfare = pd.DataFrame(data = avg_last_welfare,
        columns = ['output_welfare'])

output_gini = pd.DataFrame(data = gini_list,
        columns = ['gini'])

output_modularity = pd.DataFrame(data = modularity_list,
        columns = ['modularity'])


# TODO SAVE MY DATA BITTE

#raise KeyboardInterrupt

S_i_welfare = sobol.analyze(problem, output_welfare['output_welfare'].values, print_to_console=True, calc_second_order=False)
#print(S_i_welfare)

S_i_gini = sobol.analyze(problem, output_gini['gini'].values, print_to_console=True, calc_second_order=False)
#print(S_i_price)

S_i_modularity = sobol.analyze(problem, output_modularity['modularity'].values, print_to_console=True, calc_second_order=False)
#print(S_i_modularity)

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
    plt.errorbar(indices, range(l), color = 'k', ecolor = 'b', xerr=errors, linestyle='None', marker='o', capsize = 3, linewidth = 1)
    plt.axvline(0, c='k')
plt.figure()

for Si in [S_i_welfare]:
    # First order
    plot_index(Si, problem['names'], '1', 'Welfare First order sensitivity')
    # Second order
    # plot_index(Si, problem['names'], '2', 'Second order sensitivity')
    # Total order
    plot_index(Si, problem['names'], 'T', 'Welfare Total order sensitivity')
plt.show()

for Si in [S_i_gini]:
    # First order
    plot_index(Si, problem['names'], '1', 'Gini First order sensitivity')
    # Second order
    # plot_index(Si, problem['names'], '2', 'Second order sensitivity')
    # Total order
    plot_index(Si, problem['names'], 'T', 'Gini Total order sensitivity')
plt.show()

for Si in [S_i_modularity]:
    # First order
    plot_index(Si, problem['names'], '1', 'Modularity First order sensitivity')
    # Second order
    # plot_index(Si, problem['names'], '2', 'Second order sensitivity')
    # Total order
    plot_index(Si, problem['names'], 'T', 'Modularity Total order sensitivity')
plt.show()