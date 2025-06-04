#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 16:08:19 2024

@author: alessandro

This module provides functions to detect outliers and cluster data using
multiple possible methods (K-Means, DBSCAN, GMM, etc.). It also provides
visualization utilities for cluster results.

Based on reviewer feedback, we have:
- Added flexibility to choose from several clustering algorithms.
- Added larger figure sizes for improved readability in boxplots.
- Expanded docstrings to clarify clustering assumptions and logic.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime
from sklearn.svm import OneClassSVM
from sklearn.cluster import DBSCAN, KMeans
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Union, List

np.random.seed(42)


def detect_outliers_w_gmm(
    df: pd.DataFrame,
    components: int = 2,
    threshold_quantile: float = 0.01
) -> pd.DataFrame:
    """
    Detect and filter outliers using a Gaussian Mixture Model.

    The GMM is fit on the entire DataFrame (numerical columns). The log-likelihood
    scores are calculated for each row; any row below a given quantile of the log-likelihood
    distribution is deemed an outlier and removed.

    Args:
        df (pd.DataFrame): Input data frame.
        components (int): Number of mixture components.
        threshold_quantile (float): Threshold quantile below which points are removed.

    Returns:
        pd.DataFrame: Filtered DataFrame after removing outliers.
    """
    gmm = GaussianMixture(n_components=components)
    df["gmm_score"] = gmm.fit(df).score_samples(df)

    return (
        df[df["gmm_score"] >= np.quantile(df["gmm_score"], threshold_quantile)]
          .drop("gmm_score", axis=1)
    )


def detect_outliers(
    df: pd.DataFrame,
    method: str = "isolation_forest"
) -> pd.DataFrame:
    """
    Detect and filter outliers in a DataFrame using either Isolation Forest or One-Class SVM.
    
    Args:
        df (pd.DataFrame): Input DataFrame (all numerical).
        method (str): 'isolation_forest' or 'svm' (OneClassSVM) for outlier detection.
                      Default is "isolation_forest".
    
    Returns:
        pd.DataFrame: Filtered DataFrame with outliers removed.
    """
    if method == "isolation_forest":
        print("Using Isolation Forest...")
        df["is_anomaly"] = IsolationForest(random_state=0).fit_predict(df)
    else:
        print("Using OneClassSVM ...")
        df["is_anomaly"] = OneClassSVM(gamma='auto').fit_predict(df)

    # Keep only inliers
    return df.query("is_anomaly != -1").drop("is_anomaly", axis=1)


def perform_clustering(
    df: pd.DataFrame,
    method: str = "kmeans",
    k: int = 5
) -> Tuple[pd.DataFrame, np.ndarray, Union[float, None]]:
    """
    Apply a chosen clustering algorithm (K-means, DBSCAN, or GMM) on standardized features.

    Args:
        df (pd.DataFrame): DataFrame to cluster (all numeric).
        method (str): Clustering method: 'kmeans', 'dbscan', 'gmm'.
        k (int): Number of clusters if method == 'kmeans' or 'gmm'. For 'dbscan', this is ignored.

    Returns:
        Tuple[pd.DataFrame, np.ndarray, float or None]: 
            - DataFrame with cluster labels added as 'cluster'.
            - Array of unique cluster labels.
            - Inertia (K-means) or None otherwise.
    """
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df)

    if method == "dbscan":
        print("Method is DBSCAN...")
        dbscan = DBSCAN()
        labels = dbscan.fit_predict(scaled_features)
        df["cluster"] = labels
        inertia = None  # Not applicable to DBSCAN
    elif method == "gmm":
        print(f"Method is GaussianMixture with {k} components ...")
        gmm = GaussianMixture(n_components=k, random_state=42)
        labels = gmm.fit_predict(scaled_features)
        df["cluster"] = labels
        # 'Inertia' is not a direct metric for GMM, so we set to None.
        inertia = None
    else:
        # Default K-means
        print(f"Method is K-Means with k={k} ...")
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
        labels = kmeans.fit_predict(scaled_features)
        df["cluster"] = labels
        inertia = kmeans.inertia_

    return df, df["cluster"].unique(), inertia


def visualize_clusters(
    df: pd.DataFrame, 
    x: str, 
    y: str, 
    export_locally: bool = False, 
    sort_by: str = None
) -> None:
    """
    Visualize clusters using a boxplot with observation counts and percentages annotated.
    Optionally reorder the cluster categories based on the median of a reference variable.
    
    Args:
        df (pd.DataFrame): DataFrame containing cluster data.
        x (str): Name of the column to be used as the "category" (e.g., 'cluster').
        y (str): Name of the column to be used as the numeric variable (e.g., a cost or yield).
        export_locally (bool): Whether to save the plot locally in 'clustering_pipeline/output'.
        sort_by (str): If provided, re-orders the x-axis categories by the median of this column.
                       Useful to see ascending/descending patterns.
    """
    # Create output directory if needed
    base_export_path = "'clustering_AC/clustering_pipeline/output'"
    if export_locally and not os.path.exists(base_export_path):
        os.makedirs(base_export_path)

    # Determine cluster order based on median of `sort_by` variable
    if sort_by is not None:
        cluster_order = (
            df.groupby(x)[sort_by]
              .median()
              .sort_values()
              .index
              .tolist()
        )
    else:
        cluster_order = sorted(df[x].unique())

    # Increase figure size for better readability
    plt.figure(figsize=(10, 8))

    # Remove outliers based on IQR of y to avoid extreme points overshadowing the boxplot
    Q1 = df[y].quantile(0.25)
    Q3 = df[y].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df_filtered = df[(df[y] >= lower_bound) & (df[y] <= upper_bound)]

    # Create the boxplot
    ax = sns.boxplot(
        x=x,
        y=y,
        data=df_filtered,
        order=cluster_order,
        palette="Set3",
        hue=x, 
        # legend=False
    )

    # Count observations per cluster
    counts = df.groupby(x)[y].size().reset_index(name='counts')
    counts['percentage'] = (counts['counts'] / counts["counts"].sum()) * 100

    # Annotate each box with count and %
    for i, cluster_name in enumerate(cluster_order):
        row = counts[counts[x] == cluster_name]
        if row.empty:
            continue
        
        cluster_data = df_filtered[df_filtered[x] == cluster_name][y]
        if cluster_data.empty:
            continue
        
        whisker_max = (
            cluster_data.quantile(0.75)
            + 1.5 * (cluster_data.quantile(0.75) - cluster_data.quantile(0.25))
        )
        max_point = cluster_data.max()
        label_position = max(whisker_max, max_point) + (
            (df_filtered[y].max() - df_filtered[y].min()) * 0.05
        )

        ax.text(
            i,
            label_position,
            f'n = {int(row["counts"].iloc[0])}\n({row["percentage"].iloc[0]:.1f}%)',
            ha='center',
            va='bottom',
            fontsize='small',
            weight='semibold'
        )

    sns.despine(offset=10, trim=True)
    plt.tight_layout()

    if export_locally:
        plt.savefig(
            # f"{base_export_path}/{datetime.now().strftime('%Y%m%d')}_boxplot_{y}.png",
            f"{base_export_path}/boxplot_{y}.png",
            format='png'
        )

    plt.show()


def analyze_clusters(
    df: pd.DataFrame = None,
    remove_outliers: bool = True,
    outlier_method: str = "isolation_forest",
    cluster_method: str = "kmeans",
    y_col_to_plot: str = 'resa [qt/ha',
    k: int = 5,
    plot_clusters: bool = True,
    index_col: str = None
) -> Tuple[pd.DataFrame, np.ndarray, float, float]:
    """
    Perform a complete clustering analysis: load data (if not passed),
    optionally remove outliers, cluster, and visualize.

    This function can compare multiple methods (K-Means, DBSCAN, GMM), based on
    reviewer feedback to test for non-normal distributions.

    Args:
        df (pd.DataFrame): DataFrame containing numeric features (and optionally an index).
        remove_outliers (bool): Whether to remove outliers before clustering.
        outlier_method (str): 'isolation_forest' or 'svm' for outlier detection.
        cluster_method (str): 'kmeans', 'dbscan', or 'gmm' for final clustering.
        y_col_to_plot (str): Column name used for optional boxplot (e.g., yield).
        k (int): Number of clusters/components for K-Means/GMM. Not used if DBSCAN is selected.
        plot_clusters (bool): Whether to display the boxplot of the resulting clusters.
        index_col (str): If provided, set this column as index.

    Returns:
        Tuple[pd.DataFrame, np.ndarray, float, float]:
            - DataFrame with cluster labels in a 'cluster' column
            - Array of unique cluster labels
            - Silhouette score of the final clustering
            - Inertia (if K-Means), else None
    """
    # If no DataFrame is provided, load an example
    if df is None:
        df = pd.read_excel("clustering_pipeline/data/rica_duro_aziende_specializzate_all.xlsx")

    if index_col:
        df = df.set_index(index_col)

    # Outlier removal
    if remove_outliers:
        df_filtered = detect_outliers(df.copy(), method=outlier_method)
    else:
        df_filtered = df.copy()

    # Perform clustering
    clustered_df, unique_clusters, inertia = perform_clustering(
        df_filtered,
        method=cluster_method,
        k=k
    )

    # Calculate the silhouette score
    #   - For DBSCAN, there may be noise label (-1), or single cluster => silhouette fails
    #   - We'll handle it gracefully.
    try:
        silhouette = silhouette_score(
            X=clustered_df.drop("cluster", axis=1), 
            labels=clustered_df["cluster"]
        )
    except ValueError:
        silhouette = np.nan

    # Optional boxplot
    if plot_clusters and cluster_method != "dbscan":
        # DBSCAN can produce negative cluster labels and outliers, so you may want
        # a specialized plot function or handle them differently.
        visualize_clusters(
            clustered_df, 
            x="cluster", 
            y=y_col_to_plot
        )
        print(clustered_df["cluster"].value_counts(normalize=True))
        print(clustered_df["cluster"].value_counts(normalize=False))

    return clustered_df, unique_clusters, silhouette, inertia
