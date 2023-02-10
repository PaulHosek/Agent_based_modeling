# Green Energy Adoption in the European Union


## Contributors:

* Paul Hosek
* Gaia Pantaleo
* Conor Gouraud
* Souvik Chakraborty
* Tijn Schickedantz

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
* matplotlib
* pandas
* csv
* mesa
* mesa-geo
* scipy stats
* time
* network_analysis
* SAlib
* itertools
* Sobol_input_generator
* server
* profile

## Running the code

To run the model, one needs to run the geo_model2.py file. At the bottom of this file, printing of output can be (un)hashed 
to print the desired output of the model.


## Repository structure


| File Name           | Description                                                                                                                                                                                          |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|geo_model2.py| python file which executes the model.|
|country2.py| Contains the country class. All action an agent can do are defined here.|
|Server.py| Contains the functions to simulate the spatial dynamics on a map.|
|Sobol_Run.py| Contains the code to run the First and total order sensitivity analysis.|
|list_of_borders.py| Contains a list with tuples for every country with its neighbours.|


