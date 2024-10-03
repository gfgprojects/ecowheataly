# ECOWHEATALY Task 1.2

Life Cycle Assessment (LCA) setup for wheat production

see: https://ecowheataly.it/attivita-di-progetto/

Folder Task1_2/scripts holds the Python script to perform the activities of Task1.2

## Requirments

- Brightway (https://docs.brightway.dev/en/latest/)
- numpy
- json
- pandas

## How to

### Setup

The setup needed to perform ECOWHEATALY LCA is as follows:

- Install Brightway;
- install the `bw-recipe-2016` package

		`pip install bw-recipe-2016`

- Start Python and add the ReCiPe 2016 methods with the following commands:

		`from bw_recipe_2016 import add_recipe_2016`
		
		`add_recipe_2016()`
- run the `setup_recipe_2016_ecowheataly_customization.py` script found in the src folder.

		The script creates the set of methods used in ECOWHEATALY, starting from the ReCiPe 2016 ones.
- run the `setup_register_processes.py` script found in the src folder.

		The script registers the processes for tractors and the nitrogen fertilizer use.

\end{itemize}

### Use

Once the setups have been made, the `ecowheataly_lca_with_brightway.py` (also found in the src folder) makes calculations and shows the results.

The user can now go through the usual workflow: edit the `ecowheataly_lca_with_brightway.py` script, go to the inputs section, change the input values, execute the script, and analyze the results.


...
## Contributions

PyAria
Prof
