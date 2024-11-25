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
    
    return df.query("is_anomaly != -1").drop("is_anomaly", axis=1)
    

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
    
    else:
        target_k = k if k is not None else 4
        print(f"Method is kmeans with k equal to {target_k}...")
        kmeans = KMeans(n_clusters=target_k)
        df['cluster'] = kmeans.fit_predict(scaled_features)
        
    return df, df['cluster'].unique(), kmeans.inertia_


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
    if export_locally and (not os.path.exists("output")):
        os.makedirs("output")
    
    plt.figure(figsize=(8, 6))
    
    # Create the boxplot
    ax = sns.boxplot(x=x, y=y, data=df)
    
    # Calculate the number of observations per category
    counts = df.groupby(x)[y].size().reset_index(name='counts')
    
    # Calculate total observations to compute percentages
    counts['percentage'] = (counts['counts'] / counts["counts"].sum()) * 100
    
    # Add the observation count and percentage as text on the boxplot
    for i, row in counts.iterrows():
        # Get the whisker max (top whisker) for the boxplot to position the label better
        whisker_max = (
            df[df[x] == row[x]][y].quantile(0.75) + 1.5 * 
            (df[df[x] == row[x]][y].quantile(0.75) - df[df[x] == row[x]][y].quantile(0.25))
            ) * 2
        
        # Add the text label closer to the top of the whisker with count and percentage
        ax.text(i, whisker_max + (df[y].max() - df[y].min()) * 0.02, 
                f'n = {int(row["counts"])}\n({row["percentage"]:.1f}%)',
                horizontalalignment='center', size='small', color='black', weight='semibold')
    
    # Remove spines for cleaner visualization
    sns.despine(offset=10, trim=True)
    
    # Adjust the layout to ensure labels are not cut off
    plt.tight_layout()
    
    # Save the plot locally if required
    if export_locally:
        plt.savefig(f"output/{datetime.now().strftime('%Y%m%d')}_boxplot_{y}.png", format='png')
    
    # Display the plot
    plt.show()


def analyze_clusters(
        df: pd.DataFrame = pd.read_excel("clustering_pipeline/data/rica_duro_aziende_specializzate_all.xlsx"),
        remove_outliers: bool = True,
        y_col_to_plot: str = 'resa [qt/ha',
        k : int = None,
        plot_clusters: bool = True
        ) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Perform a complete cluster analysis from data loading to visualization.

    Args:
        file_path (str): The path to the Excel file containing the data.

    Returns:
        Tuple[pd.DataFrame, np.ndarray]: Modified DataFrame with cluster labels and unique cluster labels.
    """

    df_filtered = detect_outliers(df, method="isolation_forest") if remove_outliers else df
    # df_filtered = detect_outliers(df, method="svm") if remove_outliers else df
    
    clustered_df, unique_clusters, inertia = perform_clustering(df_filtered, method="kmeans", k=k)
    
    if plot_clusters:
        visualize_clusters(clustered_df, 'cluster', y_col_to_plot)
        
        print(clustered_df.cluster.value_counts(normalize=True))
        print(clustered_df.cluster.value_counts(normalize=False))
        
    return (
        clustered_df, 
        unique_clusters, 
        silhouette_score(
            X=clustered_df.drop("cluster", axis=1), 
            labels=clustered_df.cluster
            ),
        inertia
        )



