"""
Script for extracting and preprocessing agricultural data from the EcoWheataly JSON database.

This script processes multi-year data (2008–2022) from the EcoWheataly project, focusing on durum wheat production.
It performs the following steps:
1. Loads general agronomic and economic indicators for each farm (e.g., yield, costs, wheat price).
2. Extracts and aggregates detailed information on fertilizer use, categorized by type (Mineral, OrganoMineral, etc.).
3. Extracts and processes phytosanitary product usage by toxicity class and product type (Herbicide, Insecticide, Fungicide).
4. Merges all information into a flat panel dataset with one row per farm-year combination.
5. Cleans and filters the dataset for downstream analysis (e.g., clustering).
6. Outputs diagnostic plots and saves the cleaned data to CSV for further processing.

The output dataset includes variables such as crop acreage, production costs, fertilizer application rates, and phytosanitary usage profiles across farms and years.
"""

import json
import numpy as np
import pandas as pd

with open("Stats/ecowheataly_database.json") as ewdj:
    data = json.load(ewdj)

# anno, colture, Frumento duro, fertilizzanti, fitofarmaci
wheat_vars = ['produced_quantity','PLV','crop_acreage','hours_of_machines_ha','fert_costs','phyto_costs',
              'human_costs','machinery_costs','wheat_price']
# fertilizzanti, fitofarmaci
fert_vars_type = ['Mineral','OrganoMineral','Other','Micro_Mineral']
fert_vars = ['fert_area','whole_qt_ha','unit_cost','distribuited_value',
             'nitrogen_ha','phosphorus_ha','potassium_ha']

phy_vars_type = ['Herbicide', 'Insecticide', 'Fungicide']
phy_vars = ['phyto_area','distribuited_quantity_ha','unit_cost','distribuited_value']


years = np.arange(2008,2023)
species = 'durum_wheat'

farms = []
for key, val in data.items():
  # print(key,val)
    farms.append(key)
farms = np.array(farms)

## part 1 -  general data + fertilizers†

# # --------- TEST SCRIPT FOR A SINGLE YEAR -----------------------
# anno1 = '2011'
# Vars_name = ['year', 'farm code','farm_acreage','species'] + wheat_vars + fert_vars
# species = 'durum_wheat'
# Mat = []
# for i,fid in enumerate(farms):
#     # print(data[fid]['years'][anno1]['colture']['Frumento duro'])
#     try:
#         # -----------EXTRACT GENERAL DATA----------------------------------------
#         farm_acreage = data[fid]['years'][anno1]['farm_acreage']
#         crop = data[fid]['years'][anno1][species]
#         row = [anno1, fid,farm_acreage,species]
#         # extract data within crop_level keys (quantity,acreage,hours_of_machines) if available, otherwise insert 0
#         row.extend(crop.get(key, 0) for key in wheat_vars)
#     # -------------------- checks forn inf
#     #     if row[-1]> 1000:
#     #         print(fid,row[-1])
#     # except KeyError:
#     #     pass
#
#         #---------- EEXTRACT DATA ON FERTILIZERS
#         fertilizers = crop['fertilizers']
#         # extract data within crop_level keys (quantity,acreage,hours_of_machines) if available, otherwise insert 0
#         row.extend(fertilizers.get(key, 0) for key in fert_vars)
#         # CHECK THE COEHERENCE
#         if len(row) != len(Vars_name):
#             print(i, fid)
#         # Mat.append(mat)
#         Mat.append(row)
#     except KeyError:
#         pass
#
#
# Mat = np.array(Mat)
# df = pd.DataFrame(Mat,columns=Vars_name)
# # ------------------------------------------------------------------------------

# -------------- PUT THE SCRIPT INTO A FUNCTION----------------------------
def extract_data(data, anno, farms, wheat_vars, species='durum_wheat'):
    columns =['year', 'farm code',species,'farm_acreage'] + wheat_vars + fert_vars
    data_list = []

    for fid in farms:
        try:
            farm_acreage = data[fid]['years'][anno]['farm_acreage']
            # crop == datasubset
            crop = data[fid]['years'][anno][species]
            row = [anno, fid,species,farm_acreage]

            # extract data recalled in wheat_vars
            row.extend(crop.get(key, 0) for key in wheat_vars)

            # # extract data recalled in fert_vars
            # fertilizers = crop['fertilizers']
            # row.extend(fertilizers.get(key, 0) for key in fert_vars)

            data_list.append(row)
        except KeyError:
            # Handle KeyError more gracefully, e.g., log the error or return partial data
            pass
    # mat = np.array(data_list)
    # df = pd.DataFrame(data_list, columns=columns)
    return data_list

# # CHECKS:
# anno1 = '2011'
# Vars_name = ['year', 'farm code','farm_acreage','species'] + wheat_vars + fert_vars
# Mat = extract_data(data, anno1, farms, wheat_vars, fert_vars)
# df2 = pd.DataFrame(Mat,columns=Vars_name)

Vars_name = ['year', 'farm code','species','farm_acreage'] + wheat_vars
years = np.arange(2008,2023)
for year in years:
    if year == years[0]:
        Mat = extract_data(data, str(year), farms, wheat_vars)
    else:
        mat = extract_data(data, str(year), farms, wheat_vars)
        Mat.extend(mat)


dtypes = {}
for i in range(len(Vars_name)):
    if i <2:
        dtypes[i] ='int'
    elif i ==3:
        dtypes[i] ='float'
    elif i ==2:
        dtypes[i] = 'str'
    else:
        dtypes[i] = 'float'

df1 = pd.DataFrame(Mat,columns=Vars_name)
dtypes1 = {col: 'int' if i < 2 else 'float' if i == 3 else 'str' if i == 2 else 'float' for i, col in enumerate(df1.columns)}
df1 = df1.astype(dtypes1)


# NOTES:
# >> manage the "inf" in the hours_of_machines (due to 0 costs in the Azienda.scv files)

## PART 2 : Pythosanitary
# fertilizzanti, fitofarmaci
# fert_vars_type = ['Mineral','OrganoMineral','Other','Micro_Mineral']

Mat2 = []

for year in years:
    for fid in farms:
        row = [year,fid]
        try:
            crop = data[fid]["years"][str(year)][species]
            fert = crop.get("fertilizers", {})
        except KeyError:
            fert = {}

        for ftype in fert_vars_type:
            values = fert.get(ftype, {})
            for var in fert_vars:
                # print(var)
                # print(values.get(var, 0))
                colname = f"{ftype}_{var}"
                # Se var è una chiave presente in values, allora viene usato il valore associato, anche se è np.nan.
                # Se var NON è una chiave di values, allora viene usato il default 0.
                row.append(values.get(var, 0))

        Mat2.append(row)

# Convert to DataFrame


df_colname  = ['year','farm code']
for t in fert_vars_type:
    for c in fert_vars:
        df_colname.append(t+'_'+c)
df2 = pd.DataFrame(Mat2,columns=df_colname)
dtypes2 = {col: 'int' if i < 2  else 'float' for i, col in enumerate(df2.columns)}
df2 = df2.astype(dtypes2)


## PART 3 : Pythosanitary


types  =['Herbicide', 'Insecticide', 'Fungicide']
ColName = ['year','farm code','Qt Tox-0','Qt Tox-1','Qt Tox-2','Qt Tox-3','Qt Tox-4']
Mat3 = []
for T,TYPE in enumerate(types):
    print(f'organizzando {TYPE}')
    mat = []
    for year in years:
        print(year)
        for i, fid in enumerate(farms):
            try:
                # ------------prova 1----------------------------------------

                crop = data[fid]['years'][str(year)][species]
                row = np.full((len(ColName),), np.nan, dtype=object)
                row[0:2] = [year,int(fid)]

                # Estrazione variabili ft
                phyto = crop['phytosanitary']

                try:

                    val = {}
                    for item in phyto[TYPE].keys():
                        # print(item)
                        classe=int(item)
                        item_data = phyto[TYPE][item]
                        qt_ha = item_data['distributed_quantity_ha'] #* item_data['phyto_area']
                        val[classe] = val.get(classe, 0) + qt_ha
                        # print(val)
                    for c,v in val.items():
                        row[c+2]= float(v)
                    mat.append(row)
                except:
                    mat.append(row) # year, farm code + 5 nan

            except KeyError:
                pass
    Mat3.append(mat)

# store the data into 3D arrays for plots
Phyto = np.stack(Mat3,axis=2)

Mat3 = np.concatenate(Mat3,axis=1)

df_colname  = []
for t in types:
    for c in ColName:
        if (c==ColName[0]) | (c==ColName[1]):
            df_colname.append(c)
        else:
            df_colname.append(t+'_'+c)


# afterchecks we can delete redundant colum:
cols_todel = [7,8,14,15]
df_colname = np.delete(df_colname,cols_todel)
Mat3 = np.delete(Mat3,cols_todel,axis=1)


df3 = pd.DataFrame(Mat3, columns=df_colname)
dtypes3 = {col: 'int' if i < 2  else 'float' for i, col in enumerate(df3.columns)}
df3 = df3.astype(dtypes3)
# here we got NaN that must be changed by zero (if at least 1 pythosanitary priducts has been used)
# mx = np.shape(Mat3)[1] - 2
# ii = np.sum(np.isnan(Mat3[:,2::].astype(float)),axis=1)
# id_to_del = np.where(ii==mx)[0]
df3.fillna(0, inplace=True) #cheked! nan are 0 uses



## MERGING df1 with df2


temp_df = pd.merge(df1, df2, on=['year', 'farm code'], how='left')
flat_df = pd.merge(temp_df,df3,on=['year', 'farm code'], how='left' )
# where there are no data on Phytosanitary means that the farm didn't use it in that year
# hence we insert 0 and 0 must be kept as good value!
flat_df.fillna(np.nan, inplace=True)


## ===================== FILTERING ===========================
from clustering_AC.clustering_pipeline.utils import clean_and_plot

np.shape(flat_df)
np.shape(flat_df.dropna())
for year in years:
    temp = flat_df[flat_df['year']==year]
    print(f'in year {year} there are: ')
    print (f'{np.shape(temp)[0]} observations...')
    print(f'{np.shape(temp.dropna())[0]} observations with "finite" data...')
    print(f' and {len(temp.dropna()["farm code"].unique())} farms producing {species}')

from matplotlib import pyplot as plt
cols = flat_df.columns[3::]

plt.boxplot(flat_df[cols],labels = cols)
plt.xticks(rotation = 90)

selected_cols = ['PLV', 'fert_costs', 'phyto_costs','human_costs', 'machinery_costs',
                 'Mineral_distribuited_value','Mineral_nitrogen_ha']

for c in selected_cols:
    # Salta colonne con troppi zeri
    zero_ratio = (flat_df[c] == 0).sum() / len(flat_df[c] )
    print(f'{c} : {np.round(zero_ratio,2)}')
# df = clean_and_plot(flat_df,cols, plot=True, title_prefix="DB")


df = clean_and_plot(flat_df.dropna(),selected_cols, plot=True, title_prefix="DB")
for year in years:
    temp = df[df['year']==year]
    print(f'in year {year} there are: ')
    print (f'{np.shape(temp)[0]} observations...')
    print(f'{np.shape(temp.dropna())[0]} observations with "finite" data...')
    print(f' and {len(temp.dropna()["farm code"].unique())} farms producing {species}')
# ===========================================================




## plots


from matplotlib import pyplot as plt
for T,TYPE in enumerate(types):
    plt.figure(T+1)
    mat = Phyto[:, :, T]

    for tox in range(5):
        vec = []
        for year in years:
            ii = np.where(mat[:,0]==year)[0]
            a = mat[ii,tox+2].astype(float)
            vec.append(a[a>0])
        vec = [np.log1p(v) for v in vec]
        num = [len(v) for v in vec]
        plt.subplot(2, 3, tox+1)
        plt.boxplot(vec,patch_artist=True)
        plt.xticks(np.arange(len(years))+1,years, fontsize=12,rotation = 90)
        [plt.text(y+1,-1,n) for y,n in zip(years,num)]
        plt.title(f' Tox {tox+1}')
        plt.ylim(-2.5,)
    plt.suptitle(TYPE)

colori =['tab:blue','tab:cyan','tab:olive','tab:orange','tab:red']


for T, TYPE in enumerate(types):
    plt.figure(T + 4)
    mat = Phyto[:, :, T]

    for tox in range(5):
        vec = []
        for year in years:
            ii = np.where(mat[:, 0] == year)[0]
            a = mat[ii, tox + 2].astype(float)
            vec.append(a[a > 0])
        vec = [np.mean(v) for v in vec]
        plt.plot(years,vec,'-o',color=colori[tox],label=f'TOX {tox}')
        plt.xticks(years, years, fontsize=12, rotation=90)
    plt.legend()
    plt.title(TYPE)


df.to_csv("clustering_AC/clustering_pipeline/data/flat_df2.csv", index=False)

