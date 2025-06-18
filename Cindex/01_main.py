# -*- coding: utf-8 -*-
"""
This script provides the recursive calculation used to identify the best C-index.

@author: Arianna Di Paola


NOTE: the script was build on Spyder Environment.
        In non-interactive mode (e.g., running the script from terminal),
        each figure (and the script as well) will be block until the figure have been closed;

# -------------------------------------------------------
Python 3.7.7
    requirments:
    - numpy 1.19.5
    - matplotlib 3.3.4
# -----------------------------------------------------

MANDATORY:
Input features must be expressed as Z-score (mean=0, one standard deviation =1).
In the example inputs data (text data in CSV format) are already standardized in Z-scores.


"""

import numpy as np
import pandas  as pd
from matplotlib import pyplot as plt
from scipy.stats import gamma, norm

# PUT HERE THE PATH OF THE DIRECTORY WITH DATA

from Cindex.utils import Cindex

# ------------------------------------------------------------------------------
# Load the test data:
# Input features must be expressed as Z-score (mean=0, one standard deviation =1).
# In the example inputs data (text data in CSV format) are already standardized in Z-scores.


# Step 1: Load data
flat_df = pd.read_csv("clustering_AC/clustering_pipeline/data/flat_df.csv")  # Load data into a DataFrame

year = 2016
# Filter data for the selected year
print(f"Filtering year for selected value: {year}")
flat_df = flat_df.query(f"year=={year}")

if flat_df.empty:
	raise Exception(
		f"Emtpy DataFram with year {year}. Please, select another value."
	)

# Calculate farm yield as produced quantity per crop acreage
flat_df = flat_df.assign(
	crop_yield=lambda x: x.produced_quantity / x.crop_acreage
)


flat_df["phyto_costs_ha"] = flat_df['phyto_costs'] / flat_df['crop_acreage']


flat_df["fert_costs_ha"] = flat_df['fert_costs'] / flat_df['crop_acreage']




# ======= PYTHO AGGREGATION and Normaliztion to acrage==============================
# Step 2: Basic Feature Engineering
# Identify all columns related to herbicides
herbicide_cols = [elem for elem in flat_df.columns if "Herbicide_Qt" in elem]
# Compute the herbicide ratio relative to crop acreage
flat_df["herbicide_ha"] = (
		flat_df[herbicide_cols].sum(axis=1) / flat_df["crop_acreage"]
)

insecticide_cols = [elem for elem in flat_df.columns if "Insecticide_Qt" in elem]
# Compute the herbicide ratio relative to crop acreage
flat_df["insecticide_ha"] = (
		flat_df[insecticide_cols].sum(axis=1) / flat_df["crop_acreage"]
)

fungicide_cols = [elem for elem in flat_df.columns if "Fungicide_Qt" in elem]
# Compute the herbicide ratio relative to crop acreage
flat_df["fungicide_ha"] = (
		flat_df[fungicide_cols].sum(axis=1) / flat_df["crop_acreage"]
)

# Step 3: Performance Ratios
# Calculate the ratio of herbicide use relative to yield
flat_df["herbicide_efficiency"] = flat_df["herbicide_ha"]/ flat_df["crop_yield"]
flat_df["insecticide_efficiency"] =  flat_df["insecticide_ha"]/ flat_df["crop_yield"]
flat_df["fungicide_efficiency"] = flat_df["fungicide_ha"]/ flat_df["crop_yield"]

phyto_cols = ["herbicide_efficiency","insecticide_efficiency","fungicide_efficiency"]
flat_df["phyto_efficiency"] = (
		flat_df[phyto_cols].sum(axis=1)
)

# ======= Ferti AGGREGATION and Normaliztion to acrage==============================
# Define columns representing essential elements for crop nutrition
keywords = ['nitrogen_ha', 'phosphorus_ha', 'potassium_ha']
new_cols = ['Nha_efficiency','Pha_efficiency','Kha_efficiency']
for k,c in zip(keywords,new_cols):
	x_cols = [elem for elem in flat_df.columns if k in elem]
	flat_df[c] =  flat_df[x_cols].sum(axis=1)/ flat_df["crop_yield"]

# Calculate total elements ratio over yield
flat_df["ferti_efficiency"] = flat_df[new_cols].sum(axis=1)

# Calculate hours of machinery use per hectare relative to yield
flat_df["hr_machines_efficiency"] =  flat_df["hours_of_machines_ha"]/flat_df["crop_yield"]


# Cost efficiency
flat_df["fert_cost_ha"] = flat_df["fert_costs"] / flat_df["crop_acreage"]

flat_df["phyto_cost_ha"] = flat_df["phyto_costs"] / flat_df["crop_acreage"]


flat_df["human_costs_ha"] = flat_df["human_costs"] / flat_df["crop_acreage"]


flat_df["machinery_costs_ha"] = flat_df["machinery_costs"] / flat_df["crop_acreage"]


flat_df["fert_cost_efficiency"] = flat_df["fert_costs_ha"]/flat_df["crop_yield"]

flat_df["phyto_cost_efficiency"] =flat_df["phyto_cost_ha"]/flat_df["crop_yield"]

flat_df["human_costs_efficiency"] = flat_df["human_costs_ha"]/flat_df["crop_yield"]

flat_df["machinery_costs_efficiency"] = flat_df["machinery_costs_ha"]/flat_df["crop_yield"]

flat_df["energy_costs_efficiency"] = (flat_df["energy_costs"]/flat_df["crop_acreage"])/flat_df["crop_yield"]

flat_df["thirdy_costs_efficiency"] = (flat_df["thirdy_costs"]/flat_df["crop_acreage"])/flat_df["crop_yield"]

# ======= INU FEATURES ==============================
# Step 4: Filter Relevant Columns
# List of clustering input features (some columns are commented out but kept for reference)


input_l = [
	'PLV',
	# 'crop_acreage',
	# 'farm_acreage',
	# 'produced_quantity',
	"energy_costs_efficiency",
	"thirdy_costs_efficiency",
	'crop_yield',
	'fert_cost_efficiency',
	'phyto_cost_efficiency',
	'human_costs_efficiency',
	'machinery_costs_efficiency',
	# 'phyto_efficiency',
	# 'ferti_efficiency',
	# 'hr_machines_efficiency'
]

# input_l = [
# 	'herbicide_ratio_over_yield',
# 	'insecticide_ratio_over_yield',
# 	'fungicide_ratio_over_yield',
# 	'Nha_ratio', 'Pha_ratio',
# 	'Kha_ratio',
# 	'hours_of_machines_ha_over_yield']
# ]

# Step 5: Handle Infinite Values
# Remove rows containing infinite values in the specified input columns
data = flat_df[input_l]
np.shape(data)
data = data.dropna()

data = data[data['PLV'] >= 0]


# plt.boxplot(data)
for i in range(1,np.shape(data)[1]):
	x = data.iloc[:,i]
	y = data.iloc[:,0]
	plt.subplot(3,3,i)
	plt.plot(x,y,'o')
	plt.ylabel('plv')
	plt.xlabel(data.columns[i])
plt.tight_layout()

##
from clustering_AC.clustering_pipeline.flat_utils import clean_and_plot

df = clean_and_plot(data,data.columns, plot=True, title_prefix="DB")


# I= np.log1p(data.iloc[:,1::])  # log(1 + x), gestisce anche zeri
# print(np.isinf(I).sum())   # Conta quanti sono inf
# print(np.isnan(I).sum())   # Conta quanti sono NaN

I = []
for i,var in enumerate(df):
	x = df.iloc[:,i].to_numpy()
	alpha, loc, beta = gamma.fit(x[x > 0], floc=0)
	# Use the gamma distribution
	Gx = gamma.cdf(x, a=alpha, loc=loc, scale=beta)
	# Calculate the proportion of zero values
	qq = len(np.where(x == 0)[0]) / len(x)
	Hx = qq + (1 - qq) * Gx
	I.append(np.round(norm.ppf(Hx),4))

I = np.array(I).T

# scaler = StandardScaler()
# I = scaler.fit_transform(I)
# scaler = StandardScaler()
# cond_var = scaler.fit_transform(np.log1p(cond_var[:,None]))
# plt.boxplot(cond_var)


plt.boxplot(I)

features = data.columns[2::]
cond_var =  I[:,0].copy()
I = I[:,2::].copy()

pos_flag = np.where(cond_var > 0.75)[0]
neg_flag = np.where(cond_var < -0.75)[0]

print('data have %s variables with %s observations each' % (np.shape(I)[1], np.shape(data)[0]))
print(f'(cond var <-1) : {len(pos_flag)}; (cond var >1) : {len(neg_flag)} ')
# ---------------------------------------------------
# Call the Cindex function
#  see help(Cindex) for details
D, components, var, operator = Cindex(I, features, pos_flag, neg_flag, plot=True, verbose=True)

# select the best result
d = []
for i in range(len(features)):
	n = len(components[i])
	d.append(D[i][n - 1])

print('the best C-index reached a distaance (D) of %s' % (np.max(d)))

#  let's see the components and their stress directions
# ("negative stress direction": data in neg_flag occurr at relatively lover values of the components),
# while the opposite is true in case of "positive stress direction" (i.e., data in neg_flag at trlatively higher values)))

best = np.argmax(d)
n = len(components[best])
F = var[best][0:n]
O = operator[best][0:n]

print('the components of the best C-index are:')
for f, o in zip(F, O):
	print(o + f)
