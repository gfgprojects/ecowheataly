"""
Regionalization Script for ReCiPe 2016 Methods

Purpose: this script adjusts characterization factors (CF) in ReCiPe 2016 methods to reflect region-specific values for Italy.

what the script does:

- Filters and selects ReCiPe 2016 methods relevant to the LCA.

- Loads and adjust CFs using conversion factors adapted for Italian conditions.

- Registers new methods with the suffix 'ecowheataly' for use in LCA.

- Copies the other methods that will be used in the project with native CF, also adding the 'ecowheataly' suffix.

Important Notes

Single-Use Only: Run once after importing ReCiPe methods to avoid duplication.

New Methods: Only methods with 'ecowheataly' in their name will be used for LCA.

Preconditions: Ensure biosphere3 and ReCiPe 2016 methods are pre-loaded.

"""

##
import bw2data as bd

# Load biosphere database
bs3 = bd.Database("biosphere3")

# Retrieve ReCiPe 2016 methods (version 20180117)
recipe=[m for m in bd.methods if 'ReCiPe 2016' in str(m) and '20180117' in str(m)]

selected_methods = [
#   Acidification
('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Terrestrial Acidification'),
('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Terrestrial ecosystems', 'Terrestrial Acidification', 'Egalitarian'),
# 	Ozone
('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Ozone Formation', 'Damage to Humans'),
('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Human health', 'Ozone Formation', 'Damage to Humans', 'Egalitarian'),
('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Ozone Formation', 'Damage to Ecosystems'),
('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Terrestrial ecosystems', 'Ozone Formation', 'Damage to Ecosystems', 'Egalitarian'),
# 	Freshwater
('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Freshwater Eutrophication'),
('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Freshwater ecosystems', 'Freshwater Eutrophication', 'Egalitarian'),
# 	Fine dust formatio
('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Particulate Matter Formation', 'Egalitarian'),
('ReCiPe 2016',  '1.1 (20180117)',  'Endpoint',  'Human health',  'Particulate Matter Formation', 'Egalitarian')
]



# Define conversion factors for different impact categories
conversion_factors = {
	"Terrestrial Acidification mid": {"Sul": 1.25 / 1, "Nit": 0.7 / 0.36, "Amm": 4.76 / 1.96},
	"Terrestrial Acidification end": {"Sul": 1.25 / 1, "Nit": 0.7 / 0.36, "Amm": 4.76 / 1.96},
	"Photochemical Ozone Formation - mid - human ": {"Nit": 1.13/1, "voc": 0.57/0.18},
	"Photochemical Ozone Formation - end - human ": {"Nit": 1.13 / 1, "voc": 0.57 / 0.18},
	"Photochemical Ozone Formation - mid - eco": { "Nit":2.6/1, "voc":1.41/0.29},
	"Photochemical Ozone Formation - end - eco": {"Nit": 2.6 / 1, "voc": 1.41 / 0.29},
	"Freshwater Eutrophication to water": {"Phospho": 0.46, "Phosphate": 0.15 / 0.33},
	"Freshwater Eutrophication to soil": {"Phospho": 0.46, "Phosphate": 0.15 / 0.33},
	"Fine Dust Formation mid": {"Sul": 0.28 / 0.29, "Nit": 0.22 / 0.11, "Amm": 0.65 / 0.24,"um":2.02/1},
	"Fine Dust Formation end": {"Sul": 0.28 / 0.29, "Nit": 0.22 / 0.11, "Amm": 0.65 / 0.24,"um":2.02/1}
}


# ----------------------------------------------------------------------------
# iterate throught methods to adjust the CFs and save the chnages
for met,c in zip(selected_methods,conversion_factors):
	print(f'adjusting method {met}')
	tmp_method = bd.Method(met)
	tmp_method_unit = tmp_method.metadata['unit']
	method_cfs = tmp_method.load()
	print(tmp_method_unit)

	adjcf = conversion_factors[c]
	new_CFs=[]
	for cf in method_cfs:
		# print(cf)
		element_name = bs3.get(cf[0][1])['name']
		# print(element_name)
		matching_keys = [key for key in adjcf.keys() if key.lower() in element_name.lower()]
		if matching_keys:
			print(f'adjusting {matching_keys} for {element_name} ' )
			new_CFs.append([cf[0], cf[1] * adjcf[matching_keys[0]] ])

	print(f'len di newCF: {len(new_CFs)}')
	# Register new regionalized method with a modified name
	new_method_name=met+('Italy','ecowheataly')
	new_met = bd.Method(new_method_name)
	new_met.validate(new_CFs)
	new_met.register(**{'unit':tmp_method_unit})
	new_met.write(new_CFs)



# ------------------------ copy other relevant methods
def safe_copy_method(source_key, destination_key, label=""):
	try:
		if destination_key in bd.methods:
			print(f"[SKIP] {label or destination_key} già presente.")
        else:
            bd.Method(source_key).copy(destination_key)
            print(f"[OK] Copiato {label or destination_key}")
    except Exception as e:
        print(f"[ERRORE] Durante la copia di {label or destination_key}: {e}")

safe_copy_method(
    ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Global Warming', '100 year timescale', 'Hierarchist'),
    ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Global Warming 100 year timescale', 'Humans and Ecoystems','Global','ecowheataly'),
    "Midpoint Global Warming 100a"
)

safe_copy_method(
    ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Carcinogenic', 'Hierarchist'),
    ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Humans - Carcinogenic','Global','ecowheataly'),
    "Midpoint Toxicity Humans - Carcinogenic"
)

safe_copy_method(
    ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Non-carcinogenic', 'Hierarchist'),
    ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Humans - Non-carcinogenic','Global','ecowheataly'),
    "Midpoint Toxicity Humans - Non-carcinogenic"
)

safe_copy_method(
    ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Ecotoxicity', 'Terrestrial', 'Hierarchist'),
    ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Ecosystems - Terrestrial','Global','ecowheataly'),
    "Midpoint Toxicity Ecosystems - Terrestrial"
)

safe_copy_method(
    ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Ecotoxicity', 'Freshwater', 'Hierarchist'),
    ('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Ecosystems - Freshwater','Global','ecowheataly'),
    "Midpoint Toxicity Ecosystems - Freshwater"
)

safe_copy_method(
    ('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Human health', 'Global Warming', '100 year timescale', 'Hierarchist'),
    ('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Global Warming 100 year timescale', 'Humans and Ecoystems','Global','ecowheataly'),
    "Endpoint Global Warming 100a"
)

safe_copy_method(
    ('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Human health', 'Toxicity', 'Carcinogenic', 'Hierarchist'),
    ('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Toxicity', 'Humans - Carcinogenic','Global','ecowheataly'),
    "Endpoint Toxicity Humans - Carcinogenic"
)

safe_copy_method(
    ('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Human health', 'Toxicity', 'Non-carcinogenic', 'Hierarchist'),
    ('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Toxicity', 'Humans - Non-carcinogenic','Global','ecowheataly'),
    "Endpoint Toxicity Humans - Non-carcinogenic"
)

safe_copy_method(
    ('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Terrestrial ecosystems', 'Ecotoxicity', 'Terrestrial', 'Hierarchist'),
    ('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Toxicity', 'Ecosystems - Terrestrial','Global','ecowheataly'),
    "Endpoint Toxicity Ecosystems - Terrestrial"
)

safe_copy_method(
    ('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Freshwater ecosystems', 'Ecotoxicity', 'Freshwater', 'Hierarchist'),
    ('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Toxicity', 'Ecosystems - Freshwater','Global','ecowheataly'),
    "Endpoint Toxicity Ecosystems - Freshwater"
)

