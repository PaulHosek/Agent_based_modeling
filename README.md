# Green Energy Adoption in the European Union

![alt text](Eu%20energy%20adoption.png)

## Contributors:

* Paul Hosek
* Tijn Schickendantz
* Gaia Pantaleo
* Conor Gouraud
* Souvik Chakraborty


## Program Overview
This work tries to model the adoption of green energy in the EU with an agent based model. 
Each agent in the model represents a country in the EU. Each agent has a certain need for money and for energy
which together defines the welfare of a country. Every time step, a country has the opportunity to buy dirty or clean power plants
or to sell buy or sell energy to neighbouring countries. The agent decides which of these actions it executes based on which action
maximizes the agents welfare.


## Requirements
* Python 3.9+
* math
* numpy
* numba
* matplotlib
* pandas
* csv
* mesa
* mesa-geo
* scipy stats
* time
* network_analysis
* SAlib
* py-spy

## Running the code

To run the model, one needs to run the geo_model2.py file. At the bottom of this file, printing of output can be (un)hashed 
to print the desired output of the model. Alternatively, can the model be easily imported into any new python file and run from there.


## Repository structure


| File Name           | Description                                                                                                                                                                                          |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|geo_model2.py| python file which executes the model.|
|country2.py| Contains the country class. All action an agent can do are defined here.|
|Server.py| Contains the functions to simulate the spatial dynamics on a map.|
|Sobol_Run.py| Contains the code to run the First and total order sensitivity analysis.|
|list_of_borders.py| Contains a list with tuples for every country with its neighbours.|
|Experiments.ipynb|Notebook including all the code necessary to run the experiments.|
|final_eu_countries.geojson| Geojson holding the shapedata for the model.|
|network_analysis.py| Includes modules to construct the similarity network and evaluate the modularity.|
|TEST_Country2.py| Unit test for the country class.|
|TEST_GeoModel2.py| Unit test for the geo_model class.|
|profile.svg| Relative performance profile of the modules in our model.|
