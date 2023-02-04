import geo_model2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

value_params = [0.5,0.2,0.6,0.1,1.5,1,0.01,0.0001]

label_params = ['cost_clean',
                'cost_dirty',
                'base_output_dirty',
                'base_output_clean',
                'metabolism_scalar_energy',
                'metabolism_scalar_money',
                'eta_global_trade',
                'predisposition_decrease']

params = pd.DataFrame(data=[value_params],columns=label_params)


ni = 100 # number of samples of each of the 10
total_runs= ni*10

def vary_params(var):

    '''Function that varies parameter: var '''

    df = pd.DataFrame()
    list_params= []
    for i in np.linspace(0.01,0.3,10):
        pars = i
        for n in range(ni):
            list_params.append(pars)
    df[var] = list_params
    return df



def keep_same_values(func,df, var):
    '''Keeps same value for fixed parameters and puts
    them in dataframe with changing params'''
    new_df = pd.DataFrame()
    old_df = df.copy()
    old_df = old_df.drop(var, axis=1)
    for el in old_df:
        list_single = []
        element = old_df[el][0]
        for val in range(total_runs):
            list_single.append(element)
        new_df[el] = list_single
    df1 = func[var]
    new_df[var] = df1
    return new_df

df_new_params = keep_same_values(vary_params('eta_global_trade'),params, 'eta_global_trade')

t = 0
i = ni
mean_list = []
ci_list = []
for r in range(10):
    print(i)
    avg_last_welfare = []
    indexed_df = df_new_params[t:i]
    for ind in range(len(indexed_df)):
        new = geo_model2.GeoModel(cost_clean=indexed_df.iloc[ind][0],
                                  cost_dirty=indexed_df.iloc[ind][1],
                                  base_output_dirty=indexed_df.iloc[ind][2],
                                  base_output_clean=indexed_df.iloc[ind][3],
                                  metabolism_scalar_energy=indexed_df.iloc[ind][4],
                                  metabolism_scalar_money=indexed_df.iloc[ind][5],
                                  eta_global_trade=indexed_df.iloc[ind][6],
                                  predisposition_decrease=indexed_df.iloc[ind][7])
        new.run_model(1200)
        nw1 = new.datacollector.get_agent_vars_dataframe()
        nw2 = new.datacollector.get_model_vars_dataframe()

        df_by_country_welfare = nw1.pivot_table(values='Welfare', columns='AgentID', index='Step')
        avg_last_welfare.append(np.mean(df_by_country_welfare.iloc[-1]))

    mean_avg_last_welfare = np.mean(avg_last_welfare)
    ci = 1.96 * np.std(avg_last_welfare) / np.sqrt(len(avg_last_welfare))
    mean_list.append(mean_avg_last_welfare)
    ci_list.append(ci)

    t+=ni
    i+=ni


outputs1 = pd.DataFrame(data = mean_list,
        columns = ['output_welfare'])

outputs2 = pd.DataFrame(data = ci_list,
        columns = ['ci'])

upperci = outputs1['output_welfare'] + outputs2['ci']
print(upperci)
lowerci = outputs1['output_welfare'] - outputs2['ci']
plt.plot(np.linspace(0.01,1,10), mean_list)
plt.fill_between(np.linspace(0.01,1,10), lowerci, upperci, alpha=0.5)

plt.title('OFAT welfare, parameter changing: eta')
plt.show()
