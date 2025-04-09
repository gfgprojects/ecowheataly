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

with open("DB_population/ecowheataly_database.json") as ewdj:
    data = json.load(ewdj)

# anno, colture, Frumento duro, fertilizzanti, fitofarmaci
wheat_vars = ['produced_quantity','PLV','crop_acreage','hours_of_machines_ha','fert_costs','phyto_costs',
              'energy_costs','thirdy_costs', 'human_costs','machinery_costs','wheat_price']
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

## part 1 -  general data

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


## Add some extra columns

# Calculate farm yield as produced quantity per crop acreage
flat_df = flat_df.assign(
	crop_yield=lambda x: x.produced_quantity / x.crop_acreage
)

print('crop yield cannot be zero: removing few rows...')
flat_df.loc[flat_df['crop_yield'] == 0, 'crop_yield'] = np.nan


print('Hours of machine has few inf... let us remove them')
n_inf = np.isinf(flat_df.iloc[:,4::].astype(float)).sum()
flat_df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Normalize some vslues:
flat_df["PLV_2_Qt"] = flat_df['PLV'] / flat_df['produced_quantity']


flat_df["phyto_costs_2_Qt"] = flat_df['phyto_costs'] / flat_df['produced_quantity']


flat_df["fert_costs_2_Qt"] = flat_df['fert_costs'] / flat_df['produced_quantity']




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
flat_df["herbicide_inefficiency"] = flat_df["herbicide_ha"] / flat_df["crop_yield"]
flat_df["insecticide_inefficiency"] = flat_df["insecticide_ha"] / flat_df["crop_yield"]
flat_df["fungicide_inefficiency"] = flat_df["fungicide_ha"] / flat_df["crop_yield"]

phyto_cols = ["herbicide_inefficiency","insecticide_inefficiency","fungicide_inefficiency"]
flat_df["phyto_inefficiency"] = (
		flat_df[phyto_cols].sum(axis=1)
)

# ======= Ferti AGGREGATION and Normaliztion to acrage==============================
# Define columns representing essential elements for crop nutrition
keywords = ['nitrogen_ha', 'phosphorus_ha', 'potassium_ha']
new_cols = ['N_ha','P_ha','K_ha']
for k,c in zip(keywords,new_cols):
	x_cols = [elem for elem in flat_df.columns if k in elem]
	flat_df[c] = flat_df[x_cols].sum(axis=1)/ flat_df["crop_yield"]


# Calculate total elements ratio over yield
flat_df["ferti_inefficiency"] = flat_df[new_cols].sum(axis=1)

# Calculate hours of machinery use per hectare relative to yield
flat_df["hours_of_machines_inefficiency"] = (
		flat_df["hours_of_machines_ha"] / flat_df["crop_yield"]
)


## ===================== FILTERING ===========================
from DB_population.flat_utils  import remove_outliers_adjusted_boxplot
import gc

# BEFORE CLEANING:  Let see some numbers about the size of flat_df
from matplotlib import pyplot as plt
cols = flat_df.columns[3::]
sel_cols =[]
Mat = []
from scipy.stats import skew
for c in cols:
    temp = flat_df[c]
    data_skew = skew(temp.dropna())
    if abs(data_skew) > 0.2:
         sel_cols.append(c)
    Mat.append(temp[temp>0])

plt.boxplot(Mat,labels = cols)
plt.xticks(rotation = 90)
plt.tight_layout()

# NB phyto_inefficiency' and ferti_inefficiency fa da cappello per tutte le colonne sui fito e fertilizzanti!
sel_cols=['produced_quantity', 'PLV',
        'fert_costs', 'phyto_costs',
       'thirdy_costs', 'human_costs', 'machinery_costs', 'Mineral_nitrogen_ha',
          'crop_yield',  'phyto_inefficiency', 'ferti_inefficiency',
          'hours_of_machines_inefficiency']

log1_records = []
 # Informazioni sulle dimensioni iniziali
initial_shape = flat_df.shape
finited_shape = flat_df.dropna().shape

log1_records = []
# Per ogni anno
for year in years:
    temp = flat_df[flat_df['year'] == year]
    n_total = temp.shape[0]
    n_finite = temp.dropna().shape[0]
    n_farms = len(temp.dropna()['farm code'].unique())

    log1_records.append({
        "year": year,
        "n_obs": n_total,
        "n_finite": n_finite,
        "n_farms": n_farms,
    })
log1_rec = pd.DataFrame(log1_records)

# CLEANING DATA AND REPORTETING
# from sklearn.ensemble import IsolationForest


log2_records=[]
# for batch in range(0, len(cols), 5):
#     for c in cols[batch:batch+5]:
for c in sel_cols:
    print(f"********** Analysing variable {c} ********************")

    temp = flat_df[c].copy()
    n_obs =  temp.shape[0]
    n_finite_before =  temp.dropna().shape[0]
    # iso_forest = IsolationForest(contamination=0.1, random_state=42)
    # iso_forest.fit(temp.to_numpy().reshape(-1, 1))
    # # Predizione: -1 = outlier, 1 = normale
    # outliers = iso_forest.predict(temp.to_numpy().reshape(-1, 1))
    # print(len(outliers[outliers==-1]))
       # var= temp.copy()
    # var[outliers == -1] = np.nan
    var = remove_outliers_adjusted_boxplot(temp)
    flat_df[c] = var
    n_finite_after = var.dropna().shape[0]
    num_zeri = var.eq(0).sum()
    gc.collect()

    log2_records.append({
        "variable": c,
        "n_obs": n_obs,
        "n_finite_before": n_finite_before,
        "n_finite_after": n_finite_after,
        "n_outliers" : n_finite_before - n_finite_after,
        "n_zeros": num_zeri
    })
log2_rec = pd.DataFrame(log2_records)

# LAST BUT NON LEAST: HANDINGL ZEROS IN AREA AND PLV:
for c in cols[1:4]:
    zero_rows = flat_df[c] == 0  # Maschera booleana per righe con 0 in colonna `c`
    num_zeri = zero_rows.sum()
    print(f"In '{c}' remain {num_zeri} zeros that are put to NaN in entire rows")
    # Sostituisce tutte le celle dell'intera riga con NaN dove `c == 0`
    flat_df.loc[zero_rows, :] = np.nan

log3_records = []
# Per ogni anno
for year in years:
    temp = flat_df[flat_df['year'] == year]
    n_total = temp.shape[0]
    n_finite = temp.dropna().shape[0]
    n_farms = len(temp.dropna()['farm code'].unique())

    log3_records.append({
        "year": year,
        "n_obs": n_total,
        "n_finite": n_finite,
        "n_farms": n_farms,
    })
log3_rec = pd.DataFrame(log3_records)
log3_rec.insert(loc=2, column='n_finite_before', value=log1_rec['n_finite'])
log3_rec = log3_rec.drop('n_farms', axis=1)
log3_rec['n_deletion'] = log3_rec['n_finite_before'] -log3_rec['n_finite']
# Esportazione in tabella LaTeX
# log_df.to_latex("report_outlier_summary.tex", index=False, na_rep='')



MatNew = []

for c in cols:
    temp = flat_df[c]
    MatNew.append(temp[temp>0])

plt.subplot(1,2,1)
plt.boxplot(Mat,labels = cols)
plt.xticks(rotation = 90)
plt.tight_layout()
plt.title('before cleaning')
plt.subplot(1,2,2)
plt.boxplot(MatNew,labels = cols)
plt.xticks(rotation = 90)
plt.tight_layout()
plt.title('after  cleaning')

# np.shape(flat_df)
# np.shape(flat_df.dropna())
# for year in years:
#     temp = flat_df[flat_df['year']==year]
#     print(f'in year {year} there are: ')
#     print (f'{np.shape(temp)[0]} observations...')
#     print(f'{np.shape(temp.dropna())[0]} observations with "finite" data...')
#     print(f' and {len(temp.dropna()["farm code"].unique())} farms producing {species}')



# import gc
# #HANDING OUTLIERS (use batch sample to avoid oversaturation of the harddisk)
# for batch in range(0,len(cols),5):
#     for c in cols[batch:batch+5]:
#         print(f'********** analysing variable {c} ********************')
#         temp = flat_df[c]
#         var = remove_outliers_adjusted_boxplot(temp)
#         flat_df[c]=temp
#         gc.collect()

# Esportazione in LaTeX
log3_rec.to_latex("DB_population/tabella_output.tex", index=False, encoding='utf-8')

!dos2unix DB_population/tabella_output.tex




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


flat_df.to_csv("DB_population/flat_df.csv", index=False)

