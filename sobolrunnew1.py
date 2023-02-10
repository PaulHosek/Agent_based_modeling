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
import pandas as pd


# Gaia0Paul_Output_Welfare = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia0Paul_Output_Welfare.csv')
# gaia_tijn_Output_Welfare = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\gaia_tijn_Output_Welfare.csv')
# Gaia_2_Output_Welfare = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia_2_Output_Welfare.csv')
# Gaia3_Output_Welfare = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia3_Output_Welfare.csv')
# Gaia_output_welfare = pd.concat([Gaia0Paul_Output_Welfare, gaia_tijn_Output_Welfare, Gaia_2_Output_Welfare, Gaia3_Output_Welfare], ignore_index=True)
# Gaia_output_welfare.to_csv("Gaia_output_welfare.csv")
#
#
#
#
# Gaia0Paul_Output_Gini = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia0Paul_Output_Gini.csv')
# gaia_tijn_Output_Gini = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\gaia_tijn_Output_Gini.csv')
# Gaia_2_Output_Gini = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia_2_Output_Gini.csv')
# Gaia3_Output_Gini = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia3_Output_Gini.csv')
# Gaia_output_gini = pd.concat([Gaia0Paul_Output_Gini, gaia_tijn_Output_Gini, Gaia_2_Output_Gini, Gaia3_Output_Gini], ignore_index=True)
# Gaia_output_gini.to_csv("Gaia_output_gini.csv")
#
#
# Gaia0Paul_Output_Modularity = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia0Paul_Output_Modularity.csv')
# gaia_tijn_Output_Modularity = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\gaia_tijn_Output_Modularity.csv')
# Gaia_2_Output_Modularity = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia_2_Output_Modularity.csv')
# Gaia3_Output_Modularity = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia3_Output_Modularity.csv')
# Gaia_output_modularity = pd.concat([Gaia0Paul_Output_Modularity, gaia_tijn_Output_Modularity, Gaia_2_Output_Modularity, Gaia3_Output_Modularity], ignore_index=True)
# Gaia_output_modularity.to_csv("Gaia_output_modularity.csv")


############################################################


# Souvik_Output_Welfare = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Souvik_Output_Welfare.csv')
# Tijn_Output_Welfare = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Tijn_Output_Welfare.csv')
# Conor_Output_Welfare = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Conor_Output_Welfare.csv')
# Gaia_output_welfare = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia_output_welfare.csv')
# output_welfare = pd.concat([Souvik_Output_Welfare, Tijn_Output_Welfare, Conor_Output_Welfare, Gaia_output_welfare], ignore_index=True)
# output_welfare.to_csv("output_welfare.csv")
#
#
# Souvik_Output_Gini = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Souvik_Output_Gini.csv')
# Tijn_Output_Gini = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Tijn_Output_Gini.csv')
# Conor_Output_Gini = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Conor_Output_Gini.csv')
# Gaia_output_gini = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia_output_gini.csv')
# output_gini = pd.concat([Souvik_Output_Gini, Tijn_Output_Gini, Conor_Output_Gini, Gaia_output_gini], ignore_index=True)
# output_gini.to_csv("output_gini.csv")
#
#
# Souvik_Output_Modularity = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Souvik_Output_Modularity.csv')
# Tijn_Output_Modularity = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Tijn_Output_Modularity.csv')
# Conor_Output_Modularity = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Conor_Output_Modularity.csv')
# Gaia_output_modularity = pd.read_csv(r'C:\Users\Souvik Chakraborty\Agent_based_modeling\Gaia_output_modularity.csv')
# output_modularity = pd.concat([Souvik_Output_Modularity, Tijn_Output_Modularity, Conor_Output_Modularity, Gaia_output_modularity], ignore_index=True)
# output_modularity.to_csv("output_modularity.csv")


output_welfare = pd.read_csv('output_welfare.csv', usecols=['output_welfare'])
output_gini = pd.read_csv('output_gini.csv', usecols=['gini'])
output_modularity = pd.read_csv('output_modularity.csv', usecols=['modularity'])






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