#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 16:08:19 2024

@author: alessandro
"""

import os
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.svm import OneClassSVM
from sklearn.cluster import DBSCAN, KMeans
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from typing import Tuple

np.random.seed(42)


def detect_outliers_w_gmm(df: pd.DataFrame, components: int = 2, threshold_quantile: float = 0.01) -> pd.DataFrame:
	"""
	Detect and filter outliers using a Gaussian Mixture Model.

	Args:
		df (pd.DataFrame): Input data frame.
		components (int): Number of components for Gaussian Mixture Model.
		threshold_quantile (float): Threshold quantile to filter outliers.

	Returns:
		pd.DataFrame: Filtered DataFrame after removing outliers.
	"""

	gmm = GaussianMixture(components)
	df['gmm_score'] = gmm.fit(df).score_samples(df)

	return (df
		[df['gmm_score'] >= np.quantile(df['gmm_score'], threshold_quantile)]
		.drop("gmm_score", axis=1)
		)


def detect_outliers(df: pd.DataFrame, method: str = "isolation_forest") -> pd.DataFrame:
	"""
	Detect and filter outliers using Isolation Forest.

	Args:
		df (pd.DataFrame): Input data frame.
		components (int): Number of components for Gaussian Mixture Model.
		threshold_quantile (float): Threshold quantile to filter outliers.

	Returns:
		pd.DataFrame: Filtered DataFrame after removing outliers.
	"""

	if method == "isolation_forest":

		print("Using Isolation Forest...")

		df['is_anomaly'] = IsolationForest(random_state=0).fit_predict(df)

	else:

		print("Using One Class SVM ...")

		df['is_anomaly'] = OneClassSVM(gamma='auto').fit_predict(df)

	return df.query("is_anomaly != -1").drop("is_anomaly", axis=1), df


def perform_clustering(df: pd.DataFrame, method: str, k: int) -> Tuple[pd.DataFrame, np.ndarray]:
	"""
	Apply DBSCAN clustering on standardized features of the DataFrame.

	Args:
		df (pd.DataFrame): DataFrame to cluster.
		eps (float): The maximum distance between two samples for one to be considered as in the neighborhood of the other.
		min_samples (int): The number of samples in a neighborhood for a point to be considered as a core point.

	Returns:
		Tuple[pd.DataFrame, np.ndarray]: Tuple containing DataFrame with cluster labels and array of unique cluster labels.
	"""

	scaler = StandardScaler()
	scaled_features = scaler.fit_transform(df)

	if method == "dbscan":
		print(f"Method is {method}...")
		dbscan = DBSCAN()
		df['cluster'] = dbscan.fit_predict(scaled_features)
		inertia = -1  # or np.nan
	else:
		target_k = k if k is not None else 4
		print(f"Method is kmeans with k equal to {target_k}...")
		kmeans = KMeans(n_clusters=target_k, random_state=0)
		df['cluster'] = kmeans.fit_predict(scaled_features)
		inertia = kmeans.inertia_

	return df, df['cluster'].unique(), inertia


def visualize_clusters(df: pd.DataFrame, x: str, y: str, export_locally: bool = False) -> None:
	"""
	Visualize clusters using a boxplot with observation counts and percentages annotated.

	Args:
		df (pd.DataFrame): DataFrame containing cluster data.
		x (str): Name of the column to be used as x-axis in the boxplot.
		y (str): Name of the column to be used as y-axis in the boxplot.
		export_locally (bool): Whether to save the plot locally.
	"""
 
	# Create output directory if it doesn't exist and export_locally is True
	base_export_path = "clustering_AC/clustering_pipeline/output"
	if export_locally and (not os.path.exists(base_export_path)):
		os.makedirs(base_export_path)

	plt.figure(figsize=(8, 6))

	# Calculate interquartile range (IQR) for y-axis values
	Q1 = df[y].quantile(0.25)
	Q3 = df[y].quantile(0.75)
	IQR = Q3 - Q1

	# Exclude outliers beyond 1.5 * IQR
	lower_bound = Q1 - 1.5 * IQR
	upper_bound = Q3 + 1.5 * IQR
	df_filtered = df.copy()#df[(df[y] >= lower_bound) & (df[y] <= upper_bound)]

	# Create the boxplot
	# ax = sns.boxplot(x=x, y=y, data=df,palette='Set3')
	ax = sns.boxplot(x=x, y=y, hue=x, data=df, palette='Set3', dodge=False, legend=False)

	# Calculate the number of observations per category
	counts = df.groupby(x)[y].size().reset_index(name='counts')

	# Calculate total observations to compute percentages
	counts['percentage'] = (counts['counts'] / counts["counts"].sum()) * 100

	# Add the observation count and percentage as text on the boxplot
	for i, row in counts.iterrows():
		# Get the whisker max (top whisker) for the filtered data
		whisker_max = (
			df_filtered[df_filtered[x] == row[x]][y].quantile(0.75) + 1.5 *
			(df_filtered[df_filtered[x] == row[x]][y].quantile(0.75) - df_filtered[df_filtered[x] == row[x]][y].quantile(0.25))
		)

		# Adjust the label position dynamically to avoid overlap with datapoints
		max_point = df_filtered[df_filtered[x] == row[x]][y].max()
		label_position = max(whisker_max, max_point) + (df_filtered[y].max() - df_filtered[y].min()) * 0.05

		# Add the text label with count and percentage
		ax.text(i, label_position,
				f'n = {int(row["counts"])}\n({row["percentage"]:.1f}%)',
				horizontalalignment='center', size='small', color='black', weight='semibold')
	ax.set_title(f"  {y}  ", fontsize=12, weight='bold')

	# Remove spines for cleaner visualization
	sns.despine(offset=10, trim=True)

	# Adjust the layout to ensure labels are not cut off
	plt.tight_layout()

	# Save the plot locally if required
	if export_locally:
		plt.savefig(f"{base_export_path}/{datetime.now().strftime('%Y%m%d')}_boxplot_{y}.png", format='png')

	# Display the plot
	plt.show()



def analyze_clusters(
    df: pd.DataFrame ,
	remove_outliers: bool = True,
    y_col_to_plot: str = 'resa [qt/ha',
    k: int = None,
    plot_clusters: bool = True,
    index_col: str = None
) -> Tuple[pd.DataFrame, np.ndarray, float, float]:
    """
    Perform a complete cluster analysis from data loading to visualization.

    Returns:
        Tuple[pd.DataFrame, np.ndarray, float, float]:
            - Full DataFrame with 'cluster' column (including outliers as -1)
            - Array of unique cluster labels
            - Silhouette score (excluding outliers)
            - Clustering inertia
    """
    if index_col:
        df = df.set_index(index_col)

    # Step 1: Detect outliers (returns both filtered and full data with 'is_anomaly')
    if remove_outliers:
        df_filtered, df_marked = detect_outliers(df, method="isolation_forest")
    else:
        df_filtered = df_marked = df.copy()
        df_marked["is_anomaly"] = 1  # all valid

    # Step 2: Perform clustering only on inliers
    clustered_df, unique_clusters, inertia = perform_clustering(df_filtered.copy(), method="kmeans", k=k)

    # Step 3: Merge cluster labels back to full data
    df_marked = df_marked.copy()
    df_marked["cluster"] = -1  # default to -1 for all
    df_marked.loc[df_marked["is_anomaly"] != -1, "cluster"] = clustered_df["cluster"].values

    # Step 4: Optional plot
    if plot_clusters:
        visualize_clusters(df_marked[df_marked["cluster"] != -1], 'cluster', y_col_to_plot)
        print(df_marked.cluster.value_counts(normalize=True))
        print(df_marked.cluster.value_counts(normalize=False))

    # Step 5: Silhouette score only on valid (non-outlier) data
    valid = df_marked[df_marked["cluster"] != -1]
    score = silhouette_score(valid.drop(columns=["cluster", "is_anomaly"]), valid["cluster"])

    return df_marked, unique_clusters, score, inertia




def get_cluster_stats(clustered_df: pd.DataFrame):
	stats_dict = {}

	for cluster, data in clustered_df.groupby('cluster'):

		stats_dict[cluster] = {}

		stats_dict[cluster]["size"] = len(data)

		for feature in clustered_df.drop("cluster", axis=1).columns:
			stats_dict[cluster][feature] = {
				'mean': data[feature].mean(),
				'std': data[feature].std()
			}

	return stats_dict


def compute_optimal_k(result_df: pd.DataFrame):
	"""
	Inertia directly reflects the compactness of clusters.
	Lower inertia indicates that points are closer to their cluster centers.
	calculate the second derivative or difference in inertia for each consecutive k value.
	The optimal k is typically where this rate of change slows down significantly.
	"""

	result_df = result_df.sort_values(by="k", ascending=True)

	# Calculate first difference in inertia (rate of change)
	result_df['inertia_diff'] = result_df['inertia'].diff()

	# Calculate second difference to find the elbow (change in the rate of change)
	result_df['inertia_diff2'] = result_df['inertia_diff'].diff()

	# Find the k with the maximum second derivative (steepest drop followed by slowing drop)
	optimal_k = result_df.loc[result_df['inertia_diff2'].idxmax(), 'k']

	print(
		f"The optimal number of clusters (k) based on the elbow method is approximately: {optimal_k}"
	)

	return optimal_k



