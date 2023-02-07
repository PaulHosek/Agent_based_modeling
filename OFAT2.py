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

parameter = 'eta_global_trade'  #This is the varied parameter
steps = 100 # amount of steps per run

ni = 10 # number of samples of each of the 10
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

df_new_params = keep_same_values(vary_params(parameter),params, parameter)

t = 0
i = ni
mean_welfare_list = []
mean_gini_list = []
mean_modularity_list = []
ci_welfare_list = []
ci_gini_list = []
ci_modularity_list = []
for r in range(10):
    print(i)
    avg_last_welfare = []
    gini_list = []
    modularity_list = []
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
        new.run_model(steps)
        nw1 = new.datacollector.get_agent_vars_dataframe()
        nw2 = new.datacollector.get_model_vars_dataframe()

        df_by_country_welfare = nw1.pivot_table(values='Welfare', columns='AgentID', index='Step')
        avg_last_welfare.append(np.mean(df_by_country_welfare.iloc[-1]))

        last_gini = nw2["Gini_welfare"][steps]
        gini_list.append(last_gini)

        last_modularity = nw2["modularity_ga"][steps]
        modularity_list.append(last_modularity)

    #calculating the mean and ci of 'ni' samples (happens 10 times)
    mean_gini = np.mean(gini_list)
    mean_modularity = np.mean(modularity_list)
    mean_avg_last_welfare = np.mean(avg_last_welfare)

    ci_welfare = 1.96 * np.std(avg_last_welfare) / np.sqrt(len(avg_last_welfare))
    ci_gini = 1.96 * np.std(gini_list) / np.sqrt(len(gini_list))
    ci_modularity = 1.96 * np.std(modularity_list) / np.sqrt(len(modularity_list))

    #appending the 10 values for each
    mean_welfare_list.append(mean_avg_last_welfare)
    ci_welfare_list.append(ci_welfare)
    mean_gini_list.append(mean_gini)
    ci_gini_list.append(ci_gini)
    mean_modularity_list.append(mean_modularity)
    ci_modularity_list.append(ci_modularity)

    t+=ni
    i+=ni

#dunno if i need this part
outputs_welfare1 = pd.DataFrame(data = mean_welfare_list,
        columns = ['welfare_mean'])
outputs_welfare2 = pd.DataFrame(data = ci_welfare_list,
        columns = ['welfare_ci'])

outputs_gini1 = pd.DataFrame(data = mean_gini_list,
        columns = ['gini_mean'])
outputs_gini2 = pd.DataFrame(data = ci_gini_list,
        columns = ['gini_ci'])

outputs_modularity1 = pd.DataFrame(data = mean_modularity_list,
        columns = ['modularity_mean'])
outputs_modularity2 = pd.DataFrame(data = ci_modularity_list,
        columns = ['modularity_ci'])

#Plotting
welfare_upperci = outputs_welfare1['welfare_mean'] + outputs_welfare2['welfare_ci']
welfare_lowerci = outputs_welfare1['welfare_mean'] - outputs_welfare2['welfare_ci']
plt.plot(np.linspace(0.01,1,10), mean_welfare_list, color = 'k')
plt.fill_between(np.linspace(0.01,1,10), welfare_lowerci, welfare_upperci, alpha=0.25, color = 'b')
plt.title(f'OFAT welfare, parameter changing: {parameter}')
plt.show()

gini_upperci = outputs_gini1['gini_mean'] + outputs_gini2['gini_ci']
gini_lowerci = outputs_gini1['gini_mean'] - outputs_gini2['gini_ci']
plt.plot(np.linspace(0.01,1,10), mean_gini_list, color = 'k')
plt.fill_between(np.linspace(0.01,1,10), gini_lowerci, gini_upperci, alpha=0.25, color = 'r')
plt.title(f'OFAT GINI, parameter changing: {parameter}')
plt.show()

modularity_upperci = outputs_modularity1['modularity_mean'] + outputs_modularity2['modularity_ci']
modularity_lowerci = outputs_modularity1['modularity_mean'] - outputs_modularity2['modularity_ci']
plt.plot(np.linspace(0.01,1,10), mean_modularity_list, color = 'k')
plt.fill_between(np.linspace(0.01,1,10), modularity_lowerci, modularity_upperci, alpha=0.25, color = 'g')
plt.title(f'OFAT modularity, parameter changing: {parameter}')
plt.show()
