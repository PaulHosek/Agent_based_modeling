from IPython.display import clear_output
import SALib
from SALib.sample import saltelli
import pandas as pd
import geo_model

problem = {
    'num_vars': 5,
    'names': [
     'cost_dirty',
     'cost_clean',
     'param_for_global_trade',
     'Metabolism_energy',
     'Metabolism_money'],
    'bounds': [[0, 1], [0, 1], [0, 1], [0,1], [0,1]]}

#replicates = 3
#max_steps = 100
distinct_samples = 8 #N    N(D+2) rows output


param_values = saltelli.sample(problem, distinct_samples, calc_second_order= False)
#print(param_values)


#count = 0
samples = pd.DataFrame(data=param_values,
                       columns=['cost_dirty',
                                 'cost_clean',
                                 'param_for_global_trade',
                                 'Metabolism_energy',
                                 'Metabolism_money'])


print(samples)
ppp = samples.iloc[0]

new = geo_model.GeoModel(cost_dirty=samples.iloc[0][0],
                         cost_clean=samples.iloc[0][1],
                         metabolism_scalar_energy=samples.iloc[0][3],
                         metabolism_scalar_money=samples.iloc[0][4],
                         eta_global_trade= samples.iloc[0][2])
nw = new.data_collector.get_agent_vars_dataframe()
df_by_country = nw.pivot_table(values = 'Welfare', columns = 'AgentID', index = 'Step')
# print(df_by_country)
last_state = df_by_country.iloc[-1]
# print(np.mean(last_state))