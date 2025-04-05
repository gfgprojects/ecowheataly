# Clean LCA Script for EcoWheataly Using ReCiPe Methods and Multiple Databases
# Combines USDA and Bentrup databases for wheat production LCA.

import bw2data as bd
import bw2calc as bc
import numpy as np
import pandas as pd
from  task1_2.scripts.utils import get_pesticide_info


# Step 1: Provide inputs for 1 hectare
hours_of_tractor_use = 2.5
MJ = 100 / 0.2779 * hours_of_tractor_use  # Tractor energy calculation

kg_of_nitrogen = 50

# Step 1: Definizione delle variabili in un dizionario
fito_biosphere_exchanges = {
    "Fungicide_harmful": 0,
    "Herbicide_caution": 0,
    "Herbicide_irritating": 0,
    "Herbicide_harmful": 0,
    "GrowthRegulator_harmful": 0,
    "Insecticide_harmful": 0,
    "Insecticide_toxic": 0,
    "Molluscicide_irritating": 0
}

# Step 2: DAL DATO RICA (qui solo un esempio) estraggo le info associate a FITOGESG+
fito_info = get_pesticide_info("Anticrittogamico", 4)

chem_type = fito_info[0]['type'].capitalize()  # Prima lettera maiuscola
tox_level = fito_info[0]['tox_level'].lower()  # Minuscolo
key = f"{chem_type}_{tox_level}"  # Creazione della chiave (es. "Fungicide_irritating")

# Step 4: if the key correspond to a biosdphere exchanges:
if key in fito_biosphere_exchanges:
    value = float(fito_info[0]['active_ing_per_ha'].split()[0])
    fito_biosphere_exchanges[key] = fito_info[0]['active_ing_per_ha']



# Step 2: Create the EcoWheataly production activity (Invetory phase)
db_name = "ecowheataly"
ecowheatalydb = bd.Database(db_name)

# Remove any existing activity with the same code to avoid conflicts
for act in ecowheatalydb:
    if act['code'] == 'EcoWheataly production':
        act.delete()
        print("Previous 'EcoWheataly production' activity removed to prevent conflict.")

wheat_prod = ecowheatalydb.new_activity(code='EcoWheataly production', name='EcoWheataly production', unit='hectare')

# Add uses of machine
wheat_prod.new_exchange(input=('usda_item', 'work; ag. tractors for growing win wheat, 2014 fleet, all fuels; 100-175HP'),
                        amount=MJ, unit="megajoule", type='technosphere').save()

# Add uses of fertilizer
wheat_prod.new_exchange(input=('bentrup_item', 'application to N fertilizer use in winter wheat production systems'),
                        amount=kg_of_nitrogen, unit="kilogram", type='technosphere').save()

# Add biosphere  exchanges due to Fitosanitary
# ------- TO BE MODIFIED TO INSERT ONLY THOSE OBSERVED IN RICA
fito_fluxes_code = [
    ('a805071f-ce96-4d72-bdd5-4334d9aa3c23', fito_biosphere_exchanges['Fungicide_harmful']),
    ('3850d44e-8919-47bc-9c0a-51ccc4ec9d9f', fito_biosphere_exchanges['Herbicide_caution']),
    ('41a4e1fe-34ee-54d9-b049-3a60ada1ae3e', fito_biosphere_exchanges['Herbicide_irritating']),
    ('e5492922-eaf5-4409-aa49-7f2a35cd0336', fito_biosphere_exchanges['Herbicide_harmful']),
    ('51c7daf4-14e1-45e9-aa67-051c4ddcd9da', fito_biosphere_exchanges['GrowthRegulator_harmful']),
    ('282973e4-3c2d-4a9c-a3f2-d39a5b36aa76', fito_biosphere_exchanges['Insecticide_harmful']),
    ('1c0699e2-9be2-4c30-8328-fc0ad8caac58', fito_biosphere_exchanges['Insecticide_toxic']),
    ('597847df-518f-4bd6-ae50-1de01f2761a4', fito_biosphere_exchanges['Molluscicide_irritating'])
]

for code, amount in fito_fluxes_code:
    wheat_prod.new_exchange(input=('biosphere3', code), amount=amount, unit="kilogram", type='biosphere').save()
wheat_prod.save()

# ------------ USING OBSERVATION TO PERFORM LCA:
# Step 3: Perform LCA
functional_unit = {wheat_prod: 1}
recipe = [m for m in bd.methods if 'ReCiPe 2016' in str(m) and '20180117' in str(m)]
recipe_ecow_mid = [m for m in recipe if 'ecowheataly' in str(m) and 'Midpoint' in str(m)]
recipe_ecow_end = [m for m in recipe if 'ecowheataly' in str(m) and 'Endpoint' in str(m)]



lca = bc.LCA(functional_unit, recipe_ecow_mid[0])
lca.lci()# # Builds matrices, solves the system, generates an LCI matrix
# Explain LCI Inventory Matrix Columns based on Brightway2 documentation reference
lca.lcia()## Characterization, i.e. the multiplication of the elements of the LCI matrix
# with characterization factors from the chosen method

#  REMINDER__________________
# Technology Matrix (A)	>>> lca.technosphere_matrix
# Intervention Matrix (B)>>>> 	lca.biosphere_matrix
# Unità funzionale (f)	>>> lca.demand
# LCI (flussi aggregati)	>>> lca.inventory

# Reference: Brightway2 Documentation - LCA Object Structure
# if hasattr(lca, 'inventory'):
#     print("LCI Inventory Matrix Shape:", lca.inventory.shape)
#     print("Explanation of LCI Inventory Matrix Columns (based on Brightway2 docs):")
#     print("1. Rows: Biosphere flows (e.g., emissions, resource use)")
#     print("2. Columns: Activities contributing to the technosphere (input processes) (i.e., Machinery, Fertilizer and Fito.")
#     print("3. Values: Amount of exchanges quantified in inventory")
#     print("LCI Inventory Matrix Sample (First 5 rows and columns):")
#     print(lca.inventory.toarray()[:5, :5])
# else:
#     print("LCI Inventory Matrix not found.")
mid_scores = {}
for method in recipe_ecow_mid:
    try:
        lca.switch_method(method)
        lca.lcia()
        mid_scores[method] = {
            'score': np.round(lca.score, 4),
            'unit': bd.Method(method).metadata.get('unit', 'N/A')
        }
        print(f"{method}: {mid_scores[method]['score']} {mid_scores[method]['unit']}")
    except Exception as e:
        print(f"Error with method {method}: {e}")

# Display the results:
print("\nLCA Results for EcoWheataly Production: MIDPOINT")
for method, result in mid_scores.items():
    # print(method)
    print(f"{method[3]}: {result['score']} {result['unit']}")

end_scores = {}
for method in recipe_ecow_end:
    try:
        lca.switch_method(method)
        lca.lcia()
        end_scores[method] = {
            'score': np.round(lca.score, 4),
            'unit': bd.Method(method).metadata.get('unit', 'N/A')
        }
        print(f"{method}: {end_scores[method]['score']} {end_scores[method]['unit']}")
    except Exception as e:
        print(f"Error with method {method}: {e}")


# Step 5: Display results
print("\nLCA Results for EcoWheataly Production: ENDPOINT" )
cnt=0
for method, result in end_scores.items():
    cnt = cnt+1
    if cnt<=5:
        print(f"{cnt} {method[4]}:  --- Damage to {method[3]}  ---  {result['score']} {result['unit']}")
    else:
        print(f"{cnt}{method[3]}:  --- Damage to {method[4]}  ---  {result['score']} {result['unit']}")


# Concatenatre and Convert results into a structured DataFrame with desired columns
all_scores = {**mid_scores, **end_scores}
df = pd.DataFrame.from_records(
    [(method, result['score'], result['unit']) for method, result in all_scores.items()],
    columns=['method', 'score', 'unit']
)

# Reset the index to ensure rows are numbered from 0 to N
df.reset_index(drop=True, inplace=True)

# Notes:
# - Uses USDA and Bentrup databases via EcoWheataly LCI.
# - Evaluates multiple ReCiPe 2016 impact categories.
# - Simplifies the LCA process using a single LCA instance.
