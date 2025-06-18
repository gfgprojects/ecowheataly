#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 18:39:59 2024

@author: alessandro 
"""
import os
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import matplotlib.pyplot as plt

# from clustering_pipeline import clustering
from clustering_AC.clustering_pipeline import clustering

def _get_cluster_stats(clustered_df: pd.DataFrame):
    
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

def _compute_optimal_k(result_df: pd.DataFrame):
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


def main(year: int = 2016):

    # Create the "output" folder if it doesn't exist
    output_folder_path = 'clustering_AC/clustering_pipeline/output'
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    
    # Step 1: Load data
    flat_df = pd.read_csv("clustering_AC/clustering_pipeline/data/flat_df.csv")  # Load data into a DataFrame
    
    # Filter data for the selected year
    print(f"Filtering year for selected value: {year}")
    flat_df = flat_df.query(f"year=={year}")
    
    if flat_df.empty:
        raise Exception(
            f"Emtpy DataFram with year {year}. Please, select another value."
            )

    # Filter Relevant Columns
    input_l = [
        'phyto_inefficiency',
         'ferti_inefficiency',
        'hours_of_machines_inefficiency'
    ]

    # Handle Infinite Values
    # Remove rows containing infinite values in the specified input columns
    flat_df = (
        flat_df[~np.isinf(flat_df.filter(input_l)).any(axis=1)]
        .dropna(subset=input_l, how="any")
        )
    infinite_rows = flat_df[np.isinf(flat_df.filter(input_l)).any(axis=1)]

    # Save any remaining rows with infinite values to an Excel file for further inspection
    if not infinite_rows.empty:
        infinite_rows.to_excel(
            os.path.join(
                output_folder_path,
                f"{datetime.now().strftime('%Y%m%d_%H_%M')}_Inf rows.xlsx"
                ), index=False
            )

    # Step 6: Clustering Analysis
    result_l = []  # List to store clustering results
    for k in tqdm(range(2, 15, 1)):  # Iterate over a range of cluster sizes
    
        # Analyze clusters for the current number of clusters (k)
        _, _, silhouette_score, inertia = clustering.analyze_clusters(
            df=flat_df.filter(input_l),
            remove_outliers=True,
            y_col_to_plot="phyto_inefficiency",
            k=k,
            plot_clusters=False
        )
        
        # Append clustering performance metrics
        result_l.append({
            "silhouette_score": silhouette_score,
            "inertia": inertia,
            "k": k
        })
    
    result_df = pd.DataFrame(result_l)  # Convert results list to DataFrame
    
    # Determine optimal number of clusters using silhouette and inertia scores
    optimal_k = _compute_optimal_k(result_df)

    # Step 7: Visualization
    # Plot Inertia vs. Number of Clusters
    plt.figure(figsize=(6, 5))
    plt.plot(result_df.k, result_df.inertia, marker='o', linestyle='-', color='blue', label='Inertia')
    plt.axvline(x=optimal_k, color='red', linestyle='--', linewidth=1.5, label=f'Optimal k = {optimal_k}')
    plt.xlabel("Number of Clusters (k)", fontsize=14, weight='bold')
    plt.ylabel("Inertia", fontsize=14, weight='bold')
    plt.title(f"Inertia vs. Number of Clusters (k; optimality is at {optimal_k})", fontsize=16, weight='bold', pad=15)
    plt.legend(fontsize=12, frameon=False, loc='upper right')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{output_folder_path}/elbow.png")
    plt.show()

    # Step 8: Final Clustering with Optimal k
    clustered_df, unique_labels, silhouette_score, inertia = clustering.analyze_clusters(
        df=flat_df.filter(input_l + ["farm code"]),
        remove_outliers=False,
        y_col_to_plot="phyto_inefficiency",
        k=optimal_k,
        plot_clusters=False,
        index_col="farm code"
    )

    # Generate statistics for each cluster
    stats_dict = _get_cluster_stats(clustered_df)
    
    # Export Json
    # Save the dictionary as a JSON file in the output folder
    export_path = os.path.join(
        output_folder_path, 
        # f"{datetime.now().strftime('%Y%m%d_%H_%M')}_cluster_kpi.json"
        "cluster_kpi.json"
        )
    
    with open(export_path, 'w') as json_file:
        json.dump(stats_dict, json_file, indent=4)

    # Assign cluster labels to the main DataFrame
    flat_df["cluster"] = clustered_df["cluster"].tolist()

    # Step 9: Cluster Visualization
    cols_to_plot = input_l


    cols_to_plot =  [
        'PLV_2_Qt','crop_yield',
        'crop_acreage', 'hours_of_machines_ha',
        'fert_costs_2_Qt', 'phyto_costs_2_Qt',
        'N_ha', 'P_ha', 'K_ha'
    ] + input_l
    #cols_to_plot =  ['hours_of_machines_ha','N_ha','crop_acreage']
    cols_to_plot =  ['herbicide_inefficiency','phyto_inefficiency','ferti_inefficiency', 'hours_of_machines_inefficiency']



    # Visualize each cluster against specified columns
    for y_col_to_plot in cols_to_plot:
        
        clustering.visualize_clusters(
            df=flat_df, 
            x='cluster', 
            y=y_col_to_plot, 
            export_locally=True,
            sort_by=y_col_to_plot
        )
    # export flat_df with clusters in LCA folder
    flat_df.to_csv("task1_2/scripts/flat_df.csv", index=False)

if __name__ == "__main__":
    main()
