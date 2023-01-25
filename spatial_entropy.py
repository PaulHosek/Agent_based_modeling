import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from sklearn.neighbors import KernelDensity
import pandas as pd
import numpy as np
from pysal.explore import esda
import pysal.lib


eu_countries = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"]
welfare_values = np.random.random(size=len(eu_countries))
# print(pd.DataFrame({'name': eu_countries, 'welfare': welfare_values}))
gdf = gpd.read_file('legacy/europe_countries.geojson')
gdf.crs = {'init': 'epsg:4326'}
gdf = gdf[gdf['NAME'].isin(eu_countries)]

data = gdf.merge(pd.DataFrame({'name': eu_countries, 'welfare': welfare_values}), left_on='NAME', right_on='name')


# USING KERNEL DENSITY ESTIMATION

# Perform KDE on the location data
kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(data[['LON', 'LAT']])
# Calculate the log probability density of the location data
log_pdf = kde.score_samples(data[['LON', 'LAT']])
# Estimate the probability of each welfare value
welfare_prob = data.groupby('welfare').size() / data.shape[0]
# Calculate the spatial entropy of the welfare distribution
spatial_entropy = -1 * (log_pdf * welfare_prob).sum()
print("spatial entropy with KDE", spatial_entropy)

# MORANS I
# Load the geojson data
# gdf = gpd.read_file('europe_countries.geojson')
# gdf.crs = {'init': 'epsg:4326'}
# print(gdf.columns)
# convert the MultiPolygon object to a dataframe
# data = pd.DataFrame(columns=["NAME","LON","LAT","geometry"])
# for i,row in gdf.iterrows():
#     data = data.append({"NAME":row["NAME"],"LON":row["geometry"].centroid.x,"LAT":row["geometry"].centroid.y}, ignore_index=True)

# Merge the geojson data with the list of country names
# data = data.merge(pd.DataFrame({'name': eu_countries, 'welfare': welfare_values}), left_on='NAME', right_on='name')
print(data)
# Create a W object that defines the spatial weights matrix
w = pysal.lib.weights.Queen.from_dataframe(data)

moran = pysal.explore.esda.Moran(data['welfare'], w)

# Extract the spatial autocorrelation coefficient
spatial_autocorrelation = moran.I

# Calculate the entropy of the spatial autocorrelation coefficient
spatial_entropy = -1 * (spatial_autocorrelation * np.log2(spatial_autocorrelation)
                        + (1 - spatial_autocorrelation) * np.log2(1 - spatial_autocorrelation))

print(spatial_entropy)

# GINI Coefficient

