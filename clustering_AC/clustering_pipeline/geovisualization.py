#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 21:46:13 2025

@author: alessandro
"""
import pandas as pd
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
import seaborn as sns


def plot_provinces_by_cluster(clustered_df: pd.DataFrame):
   
    geo_df = pd.read_csv(
        "clustering_pipeline/data/aziende_grano.csv", sep=";",
        usecols=[
            "Cod_Azienda",
            "Provincia",
            "Sigla_Prov",
        ]
    ).drop_duplicates(subset=["Cod_Azienda"])

    temp_cluster_df = clustered_df.filter(["farm code", "cluster"])

    # Ensure farm codes are strings for merging
    temp_cluster_df.index = temp_cluster_df.index.astype(str)
    geo_df['Cod_Azienda'] = geo_df['Cod_Azienda'].astype(str)

    # Merge on farm code (Cod_Azienda)
    merged_df = geo_df.merge(temp_cluster_df, left_on='Cod_Azienda', right_index=True, how='inner')

    province_cluster = merged_df.groupby('Sigla_Prov')['cluster'].agg(lambda x: x.mode()[0]).reset_index()

    # Load an Italy shapefile for provinces
    italy_provinces = gpd.read_file("clustering_pipeline/data/geo_ref/georef-italy-provincia-millesime.shp")

    # Merge the province cluster data with the shapefile
    italy_provinces = italy_provinces.merge(province_cluster, left_on='prov_sigla', right_on='Sigla_Prov', how='left')

    # Assign a color to each cluster
    num_clusters = italy_provinces['cluster'].nunique()
    palette = sns.color_palette("husl", num_clusters)
    cluster_values = italy_provinces['cluster'].dropna().unique()
    color_dict = {cluster: f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}" for cluster, (r, g, b) in zip(cluster_values, palette)}

    # Create a folium map
    m = folium.Map(location=[42.5, 12.5], zoom_start=6)

    # Add provinces to the map
    for _, row in italy_provinces.iterrows():
        cluster_color = color_dict.get(row['cluster'], '#808080')  # Default grey for missing clusters
        folium.GeoJson(
            row.geometry,
            name=row['Sigla_Prov'],
            style_function=lambda x, color=cluster_color: {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            },
            tooltip=f"Province: {row['Sigla_Prov']}<br>Cluster: {row['cluster']}"
        ).add_to(m)

    # Save or show the map
    m.save("italy_clusters_map.html")

        