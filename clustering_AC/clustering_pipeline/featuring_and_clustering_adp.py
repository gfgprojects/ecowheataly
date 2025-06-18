

import json
from tqdm import tqdm
from clustering_AC.clustering_pipeline.clustering import *
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

output_folder_path = 'clustering_pipeline/output'
if not os.path.exists(output_folder_path):
	os.makedirs(output_folder_path)

# Step 1: Load data
flat_df = pd.read_csv("DB_population/flat_df.csv")  # Load data into a DataFrame

year = 2016
# Filter data for the selected year
print(f"Filtering year for selected value: {year}")
flat_df = flat_df.query(f"year=={year}")

if flat_df.empty:
	raise Exception(
		f"Emtpy DataFram with year {year}. Please, select another value."
	)
#
# # Calculate farm yield as produced quantity per crop acreage
# flat_df = flat_df.assign(
# 	farm_yield=lambda x: x.produced_quantity / x.crop_acreage
# )
#
# # Normalize some vslues:
# flat_df["PLV_2_Qt"] = flat_df['PLV'] / flat_df['produced_quantity']
#
#
# flat_df["phyto_costs_2_Qt"] = flat_df['phyto_costs'] / flat_df['produced_quantity']
#
#
# flat_df["fert_costs_2_Qt"] = flat_df['fert_costs'] / flat_df['produced_quantity']
#
#
#
#
# # ======= PYTHO AGGREGATION and Normaliztion to acrage==============================
# # Step 2: Basic Feature Engineering
# # Identify all columns related to herbicides
# herbicide_cols = [elem for elem in flat_df.columns if "Herbicide_Qt" in elem]
# # Compute the herbicide ratio relative to crop acreage
# flat_df["herbicide_ratio"] = (
# 		flat_df[herbicide_cols].sum(axis=1) / flat_df["crop_acreage"]
# )
#
# insecticide_cols = [elem for elem in flat_df.columns if "Insecticide_Qt" in elem]
# # Compute the herbicide ratio relative to crop acreage
# flat_df["insecticide_ratio"] = (
# 		flat_df[insecticide_cols].sum(axis=1) / flat_df["crop_acreage"]
# )
#
# fungicide_cols = [elem for elem in flat_df.columns if "Fungicide_Qt" in elem]
# # Compute the herbicide ratio relative to crop acreage
# flat_df["fungicide_ratio"] = (
# 		flat_df[fungicide_cols].sum(axis=1) / flat_df["crop_acreage"]
# )
#
# # Step 3: Performance Ratios
# # Calculate the ratio of herbicide use relative to yield
# flat_df["herbicide_ratio_over_yield"] = flat_df["herbicide_ratio"] / flat_df["farm_yield"]
# flat_df["insecticide_ratio_over_yield"] = flat_df["insecticide_ratio"] / flat_df["farm_yield"]
# flat_df["fungicide_ratio_over_yield"] = flat_df["fungicide_ratio"] / flat_df["farm_yield"]
#
# phyto_cols = ["herbicide_ratio_over_yield","insecticide_ratio_over_yield","fungicide_ratio_over_yield"]
# flat_df["phyto_ratio_over_yield"] = (
# 		flat_df[phyto_cols].sum(axis=1)
# )
#
# # ======= Ferti AGGREGATION and Normaliztion to acrage==============================
# # Define columns representing essential elements for crop nutrition
# keywords = ['nitrogen_ha', 'phosphorus_ha', 'potassium_ha']
# new_cols = ['Nha_ratio','Pha_ratio','Kha_ratio']
# for k,c in zip(keywords,new_cols):
# 	x_cols = [elem for elem in flat_df.columns if k in elem]
# 	flat_df[c] = flat_df[x_cols].sum(axis=1)/ flat_df["farm_yield"]
#
#
# # Calculate total elements ratio over yield
# flat_df["ferti_ratio_over_yield"] = flat_df[new_cols].sum(axis=1)
#
# # Calculate hours of machinery use per hectare relative to yield
# flat_df["hours_of_machines_ha_over_yield"] = (
# 		flat_df["hours_of_machines_ha"] / flat_df["farm_yield"]
# )
#

# ======= INU FEATURES ==============================
# Step 4: Filter Relevant Columns
# List of clustering input features (some columns are commented out but kept for reference)


input_l = [
	'phyto_inefficiency',
	 'ferti_inefficiency',
	'hours_of_machines_inefficiency'
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
is_finite = ~np.isinf(flat_df[input_l]).any(axis=1)
flat_df = flat_df[is_finite]
infinite_rows = flat_df[np.isinf(flat_df.filter(input_l)).any(axis=1)]



# # Save any remaining rows with infinite values to an Excel file for further inspection
# if not infinite_rows.empty:
# 	infinite_rows.to_excel(
# 		os.path.join(
# 			output_folder_path,
# 			f"{datetime.now().strftime('%Y%m%d_%H_%M')}_Inf rows.xlsx"
# 		), index=False
# 	)

# Step 6: Clustering Analysis


result_l = []  # List to store clustering results
input_df = flat_df.filter(input_l + ['farm code']).dropna()
flat_df = flat_df.loc[input_df.index]
print(f"Rows retained after dropping NA in input features: {len(input_df)} / {len(flat_df)}")

# for k in tqdm(range(5, 150, 1)):  # Iterate over a range of cluster sizes
#
# 	# Analyze clusters for the current number of clusters (k)
# 	_, _, silhouette_score, inertia =  analyze_clusters(
# 		df=input_df,
# 		remove_outliers=True,
# 		y_col_to_plot="herbicide_ratio_over_yield",
# 		k=k,
# 		plot_clusters=False
# 	)
#
# 	# Append clustering performance metrics
# 	result_l.append({
# 		"silhouette_score": silhouette_score,
# 		"inertia": inertia,
# 		"k": k
# 	})
#
# result_df = pd.DataFrame(result_l)  # Convert results list to DataFrame
#
# # Determine optimal number of clusters using silhouette and inertia scores
# optimal_k = compute_optimal_k(result_df)
#
# # Step 7: Visualization
# # Plot Inertia vs. Number of Clusters
# plt.figure(figsize=(10, 6))
# plt.plot(result_df.k, result_df.inertia, marker='o', linestyle='-', color='blue', label='Inertia')
# plt.axvline(x=optimal_k, color='red', linestyle='--', linewidth=1.5, label=f'Optimal k = {optimal_k}')
# plt.xlabel("Number of Clusters (k)", fontsize=14, weight='bold')
# plt.ylabel("Inertia", fontsize=14, weight='bold')
# plt.title(f"Inertia vs. Number of Clusters (k; optimality is at {optimal_k})", fontsize=16, weight='bold', pad=15)
# plt.legend(fontsize=12, frameon=False, loc='upper right')
# plt.grid(True, linestyle='--', alpha=0.6)
# plt.xticks(fontsize=12)
# plt.yticks(fontsize=12)
# plt.tight_layout()
# plt.show()


optimal_k = 6
# Step 8: Final Clustering with Optimal k
clustered_df, unique_labels, silhouette_score, inertia = analyze_clusters(
	df=input_df,
	remove_outliers=True,
	y_col_to_plot="herbicide_ratio_over_yield",
	k=optimal_k,
	plot_clusters=False,
	index_col="farm code"
)

# Generate statistics for each cluster
stats_dict = get_cluster_stats(clustered_df)
#ORDERING: # Ordinamento delle chiavi in base al mean di 'ferti_inefficiency'
sorted_keys = sorted(stats_dict.keys(), key=lambda k:stats_dict[k]['phyto_inefficiency']['mean'])

# # Export Json
# # Save the dictionary as a JSON file in the output folder
# export_path = os.path.join(
# 	output_folder_path,
# 	f"{datetime.now().strftime('%Y%m%d_%H_%M')}_cluster_kpi.json"
# )
#
# with open(export_path, 'w') as json_file:
# 	json.dump(stats_dict, json_file, indent=4)

# Assign cluster labels to the main DataFrame


flat_df = flat_df.merge(clustered_df['cluster'], on=['farm code'], how='left')


print(sorted_keys)
cols_to_plot = [
	'PLV_2_Qt','crop_yield',
	'crop_acreage', 'hours_of_machines_ha',
	'fert_costs_2_Qt', 'phyto_costs_2_Qt',
	'N_ha', 'P_ha', 'K_ha'
]

cols_to_plot = input_l

# Visualize each cluster against specified columns
for y_col_to_plot in cols_to_plot:
	visualize_clusters(
		df=flat_df,
		x='cluster',
		y=y_col_to_plot,
		export_locally=True
	)




