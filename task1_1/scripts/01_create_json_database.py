#type
#exec(open("01_create_json_database.py").read())
#to run this script from the python prompt -
import os
os.chdir('/Users/aria/Library/CloudStorage/OneDrive-CNR/ECOWHEATALY/dati_RICA_2008_2022')
import pandas as pd
import numpy as np

#set the verbose_flag to true to get some printing on the screen, or to False to avoid them
verbose_flag=True
if verbose_flag: print("Creating ECOWHEATALY database for LCA")

if 'aziende_all' not in locals():
    #import data from excel files
    if verbose_flag: print("Importing data from aziende_grano.csv")
    aziende_all = pd.read_csv('aziende_grano.csv',sep=';',decimal=',');
    #aziende_all.columns (shows columns names)
    if verbose_flag: print("Importing data from colture_grano.csv")
    colture_all = pd.read_csv('colture_grano.csv',sep=';',decimal=',');
    if verbose_flag: print("Importing data from fertilizzanti_grano.csv")
    fertilizzanti_all = pd.read_csv('fertilizzanti_grano.csv',sep=';',decimal=',');
    if verbose_flag: print("Importing data from fitofarmaci_grano.csv")
    fitofarmaci_all = pd.read_csv('fitofarmaci_grano.csv',sep=';',decimal=',');
   if verbose_flag: print("Importing data from bilancio_grano.csv")
   ce_all = pd.read_csv('bilancio_grano.csv',sep=';',decimal=',');
    if verbose_flag: print("Importing data from aiuti_grano.csv")
    #aiuti_all = pd.read_csv('aiuti_grano.csv',sep=';',decimal=',');
   # if verbose_flag: print("Importing data from Uso_acqua_cereali.xlsx")
   # acqua_all = pd.read_csv('Uso_acqua_cereali.xlsx');
    if verbose_flag: print("Importing data from certificazioni_grano.csv")
    certificazioni_all = pd.read_csv('certificazioni_grano.csv',sep=';',decimal=',');


#farm codes
farm_codes=aziende_all['Cod_Azienda'].drop_duplicates()

# a,b = np.unique(colture_all['PROD_PRINC'],return_counts=True)
nd = np.where(colture_all['PROD_PRINC']=='ND')[0]
farm_to_del = colture_all['Cod_Azienda'].iloc[nd].to_numpy()
farm_codes = farm_codes[~farm_codes.isin(farm_to_del)]

OTE = np.array([
        'Aziende con poliallevamento',
        'Aziende con policoltura',
       'Aziende miste coltivazioni ed allevamenti',
       'Aziende specializzate in erbivori',
       'Aziende specializzate in granivori',
       'Aziende specializzate in ortofloricoltura',
       'Aziende specializzate nei seminativi',
       'Aziende specializzate nelle coltivazioni permanenti'])

TEO = np.array(['polybreeding',
       'polyculture',
        'mixed_cultivation_and_breeding',
        'herbivores',
        'granivores',
        'horticulture',
        'arable_crops',
        'permanent_crops' ])
#Create dataset called datastore and insert data from file aziende.xlsx'

if verbose_flag: print("... writing farms general information ...")

datastore={}
# --------------------------------------------------------------------------------------
# GENERAL INFO
for code in farm_codes:
    tmp_df = aziende_all.loc[aziende_all["Cod_Azienda"] == code].sort_values("Anno")
    tmp_df.index = range(tmp_df.shape[0])
    # # check:Is SAU  constant or not?
    # if len(pd.unique(tmp_df["SAU"]))>1:
    #     print(f'farm {code} ha variato la SAU aziendale')
    ind = np.isin(OTE, tmp_df.loc[0,"PoloOTE"])
    teo = TEO[ind]
    datastore[str(code)] = {
                       # "count_in_farms_file(years)": int(tmp_df.shape[0]),
                       "region":tmp_df.loc[0,"Regione"],
                       "province":tmp_df.loc[0,"Provincia"],
                       "agronomic_region":tmp_df.loc[0,"Regione_Agraria"],
                       "technical-economic_orientation":teo[0],
                       }
    datastore[str(code)]["years"]={}
# YEARLY GENERAL INFO
    for runner in tmp_df.index:
         datastore[str(code)]["years"][str(tmp_df.loc[runner,"Anno"])] = {
                "farm_acreage":float(tmp_df.loc[runner,"SAU"]),
                "standard_gross_output":float(tmp_df.loc[runner,"Produzione_Standard_Aziendale"]),
                "KW_machines":float(tmp_df.loc[runner,"KW_Macchine"])}



#Insert data from colture.csv in datastore
if verbose_flag: print("... writing soft and hard wheat production data ...")

third_party_machine_makup=0.3
# # y =  cost_of_own_machines + (contoterzismo /(costi opportunità)(1+0.3))
for key in datastore:
    tmp_df_ = colture_all.loc[colture_all["Cod_Azienda"] == int(key)].sort_values("Anno")
    # tmp_df_ = tmp_df_[tmp_df_['PROD_PRINC'] != 'ND']
    # tmp_df_.index=range(tmp_df.shape[0])

    for crop, species in [(3, 'durum_wheat'), (4, 'common_wheat')]:
        tmp_df = tmp_df_[tmp_df_["ID_SPECIE_VEG"] == crop].reset_index(drop=True)


        for runner in tmp_df.index:
            #part 1 - compute machine hours
            tmp_year = tmp_df.loc[runner,"Anno"]
            third_party_machine_cost = tmp_df.loc[runner,"Contoterzismo"]
            opportunity_cost_labor = aziende_all.loc[
                (aziende_all['Cod_Azienda'] == int(key) ) &
                (aziende_all["Anno"] == tmp_year) &
                (aziende_all["ID_SPECIE_VEG"] == crop),"Costo_Opp_Lavoro_Uomo_Orario"]
            opportunity_cost_machine = aziende_all.loc[(aziende_all['Cod_Azienda']==int(key)) & (aziende_all["Anno"]==tmp_year) &  (aziende_all["ID_SPECIE_VEG"] == crop),"Costo_Opp_Lavoro_Macchina_Orario"]
            hours_of_rent_machines = round((third_party_machine_cost/((opportunity_cost_labor+opportunity_cost_machine)*(1+third_party_machine_makup))),2)
            if len(hours_of_rent_machines)>1:
                print(f'key: {key} - runner: {runner} >> ricontrollare le ore di rent machines')
                # hours_of_rent_machines=list(hours_of_rent_machines)[0]
            # part 2 - owned machine
            hours_of_own_machines = tmp_df.loc[runner, "Ore_Macchina"]
            sau_crop=tmp_df.loc[runner,"SUPERFICIE_UTIL"]
            # print(hours_of_rent_machines,hours_of_own_machines,sau_crop)
            hours_of_machines_ha = (hours_of_rent_machines + hours_of_own_machines)/sau_crop
            # QUESTO NON CI SERVE
            # cost_of_own_machines=tmp_df.loc[runner,"Costo_Lav_Macchine"]
            # if hours_of_own_machines >0:
            #     cost_own_machine_per_hour=round(cost_of_own_machines/hours_of_own_machines,2)
            # else:
            #     cost_own_machine_per_hour=0
            #write data
            # datastore[key]["years"][str(tmp_year)][species]={}
            datastore[key]["years"][str(tmp_year)][species]={
                "produced_quantity": float(tmp_df.loc[runner,"QT_PROD_PRINC"]),
                "crop_acreage": float(sau_crop),
                "hours_of_machines_ha":float(hours_of_machines_ha)}

# --------------------------------------------------------------------------------------
#Insert data from fertilizzanti.csv in datastore
if verbose_flag: print("... writing fertilization data ...")

um = np.unique(fertilizzanti_all['UM'])
print(f"fertilizers may have the following unit: {um}")
print(f"% of fertilizers in HL: { fertilizzanti_all['UM'].value_counts().get('HL', 0) / len(fertilizzanti_all)*100}")
print(f'fertilizers in HL are excluded')

fertilizzanti_all.drop(fertilizzanti_all[fertilizzanti_all['UM'] == 'HL'].index, inplace=True)


for key, data in datastore.items():
    tmp_df_ = fertilizzanti_all[fertilizzanti_all["Cod_Azienda"] == int(key)].sort_values("Anno")

    for crop, species in [(3, 'durum_wheat'), (4, 'common_wheat')]:
        tmp_df = tmp_df_[tmp_df_["Cod_Specie_Vegetale"] == crop].reset_index(drop=True)

        if tmp_df.shape[0] > 0:
            for year in data["years"].keys():
                tmp_df_y = tmp_df[tmp_df["Anno"] == int(year)].reset_index(drop=True)

                if tmp_df_y.shape[0] > 0:
                    n_trattamenti = len(tmp_df_y)
                    azoto_per_ha = tmp_df_y["Azoto_ad_ettaro"].sum()
                    fosforo_per_ha = tmp_df_y["Fosforo_ad_ettaro"].sum()
                    potassio_per_ha = tmp_df_y["Potassio_ad_ettaro"].sum()

                    if azoto_per_ha <= 0:
                        azoto_per_ha = -888
                    if fosforo_per_ha <= 0:
                        fosforo_per_ha = -888
                    if potassio_per_ha <= 0:
                        potassio_per_ha = -888

                    datastore[key]["years"][str(year)][species]["fertilizers"] = {
                        # "number_of_treatments": n_trattamenti,
                        "fert_area": tmp_df_y["Superficie_della_coltura"].mean(),
                        "nitrogen_ha": round(azoto_per_ha, 2),
                        "phosphorus_ha": round(fosforo_per_ha, 2),
                        "potassium_ha": round(potassio_per_ha, 2),
                    }

# --------------------------------------------------------------------------------------
#Insert data from fitofarmaci.csv in datastore
# brief statistcs: percentage of data taht will be matched in Biosphere3

# Seleziona solo le colonne di interesse
df = fitofarmaci_all[['Anno', 'Produzione_Industriale', 'Cod_Specie_Vegetale','Classe_di_Tossicità']]
# before 2011 there are no data
df = df[df['Anno'] >= 2011]


# Step 1: Translate category names from Italian to English
categories = {
    "Fungicide": ["Anticrittogamico"],
    "Acaricide": ["Acaricida"],
    "Herbicide": ["Diserbante"],
    "Insecticide": ["Insetticida"],
    "GrowthRegulator": ["Fitoregolatore"],
    "Molluscicide": ["Molluschicida", "Nematocida", "Rodenticida"]  # Unified as Molluscicide
}

# Step 2: Map toxicity levels to English names
toxicity_labels = {
    0: "Caution",
    1: "Very_Toxic",
    2: "Toxic",
    3: "Harmful",
    4: "Irritating"
}

# Step 3: Define the variables dictionary (only these combinations should be counted)
fito_biosphere_exchanges = {
    "Fungicide_harmful": ("Fungicide", "Harmful"),
    "Herbicide_caution": ("Herbicide", "Caution"),
    "Herbicide_irritating": ("Herbicide", "Irritating"),
    "Herbicide_harmful": ("Herbicide", "Harmful"),
    "GrowthRegulator_harmful": ("GrowthRegulator", "Harmful"),
    "Insecticide_harmful": ("Insecticide", "Harmful"),
    "Insecticide_toxic": ("Insecticide", "Toxic"),
    "Molluscicide_irritating": ("Molluscicide", "Irritating")
}


# Function to categorize based on 'Produzione_Industriale'
def assign_category(product_name):
    product_name = str(product_name).strip().lower()  # Normalize text
    for category, keywords in categories.items():
        if product_name in [kw.lower() for kw in keywords]:  # Exact match
            return category
    return "Other"  # If it does not match any category


# Function to map toxicity level to English
def map_toxicity(tox_level):
    return toxicity_labels.get(tox_level, "Unknown")


# Apply category and toxicity mapping
df['Category'] = df['Produzione_Industriale'].apply(assign_category)
df['Toxicity'] = df['Classe_di_Tossicità'].apply(map_toxicity)

# Loop through species codes [3, 4] and years [2011-2021]
for specie in [3, 4]:
    print(f"\n🔍 **Analysis for Cod_Specie_Vegetale = {specie}**\n")

    # Filter for the species
    df_specie = df[df['Cod_Specie_Vegetale'] == specie].copy()

    # Loop through years 2011-2021
    for year in np.arange(2011, 2022):
        print(f"\n📅 **Year: {year}**")

        # Filter for the current year
        df_year = df_specie[df_specie['Anno'] == year]

        # Count total occurrences for this year
        total_year = len(df_year)

        if total_year == 0:
            print("  - No data available for this year.")
            continue  # Skip if there is no data

        # Filter only relevant category + toxicity combinations
        df_filtered = df_year[
            df_year.apply(lambda row: (row['Category'], row['Toxicity']) in fito_biosphere_exchanges.values(), axis=1)]

        if df_filtered.empty:
            print("  - No matching products found for this year.")
            continue

        # Compute relevant category-toxicity combinations as percentages
        combo_counts = df_filtered.groupby(['Category', 'Toxicity']).size() / total_year * 100

        # Print results for each relevant product-toxicity pair
        for key, (category, toxicity) in fito_biosphere_exchanges.items():
            if (category, toxicity) in combo_counts:
                print(f"  📌 {category} - {toxicity}: {combo_counts[(category, toxicity)]:.2f}%")

        # Print the total sum of percentages for the year
        total_percentage = combo_counts.sum()
        print(f"  🔷 Total percentage of matched products: {total_percentage:.2f}%")

if verbose_flag: print("... writing pesticides data ...")

types = pd.unique(fitofarmaci_all["Produzione_Industriale"])
for i in types:
    for crop in [3,4]:
        temp = fitofarmaci_all[(fitofarmaci_all["Produzione_Industriale"]==i) & (fitofarmaci_all["Cod_Specie_Vegetale"]==3)]
        temp2 = fitofarmaci_all[ fitofarmaci_all["Cod_Specie_Vegetale"]==crop]
        print(f'crop == {crop}: >> {round(len(temp)/len(temp2)*100,2)}% of data "{i}" in "fitofarmaci"    ')

print('---------------------------------------------')
print('given these statistics we only import:')
tipi = np.array(['Diserbante', 'Insetticida', 'Anticrittogamico'])
types = np.array(['Herbicide', 'Insecticide', 'Fungicide'])

for i in types:
    print(i)
print('---------------------------------------------')

# checks_
sau = fitofarmaci_all['SAU']
sau2 = fitofarmaci_all['Quantità_distribuita']/fitofarmaci_all['Quantità_distribuita_per_Ha']

for key in datastore:
    tmp_df_=fitofarmaci_all.loc[fitofarmaci_all["Cod_Azienda"] == int(key)].sort_values("Anno")
    for crop, species in [(3, 'durum_wheat'), (4, 'common_wheat')]:
        tmp_df = tmp_df_[tmp_df_["Cod_Specie_Vegetale"] == crop].reset_index(drop=True)
        # Identifica incoerenze
        todel= tmp_df[tmp_df['ID_SPECIE_VEG'] != crop].index

        # Elimina le righe
        tmp_df = tmp_df.drop(todel)


        # se ho dati....
        if tmp_df.shape[0]>0:
            for year in datastore.get(key)["years"].keys():
                # se year è presente...
                tmp_df_y = tmp_df.loc[tmp_df["Anno"]==int(year)].reset_index(drop=True)
                # if len(np.unique(tmp_df_y['Produzione_Industriale']))<len(tmp_df_y):
                #     print(key,crop,year)
                if tmp_df_y.shape[0]>0:
                    datastore[key]["years"][str(year)][species]["phytosanitary"] = {}
                    # n_trattamenti = len(tmp_df_y)
                    # datastore[key]["years"][str(year)][species]["phytosanitary"]={
                    #         "number_of_treatments":int(n_trattamenti)}
                    # let iterate over the pesticides' types
                    for i in tmp_df_y["Produzione_Industriale"].unique():
                        # if len(tmp_df_y["Produzione_Industriale"].unique()) < len(tmp_df_y):
                        #      print(key,crop,year)
                       if i in tipi:
                            ind = np.isin(tipi,i)
                            iname = types[ind][0]
                            datastore[key]["years"][str(year)][species]["phytosanitary"][iname] = {}
                            # row = tmp_df_y[tmp_df_y["Produzione_Industriale"] ==i ].index
                            df_i =  tmp_df_y[tmp_df_y["Produzione_Industriale"] ==i ]
                            # sum the quantity over the same tox class (if any)
                            val = df_i.groupby('Classe_di_Tossicità').agg({
                                'Quantità_distribuita_per_Ha': 'sum',   # Somma i valori della colonna 'Quantità_distribuita_per_Ha'
                                'SAU': 'mean'                           # Calcola la media dei valori della colonna 'SAU'
                                }).reset_index()
                            # val =df_i.groupby('Classe_di_Tossicità')['Quantità_distribuita_per_Ha'].sum().reset_index()
                            # assign the values splitting for tox class
                            for _, row in val.iterrows():

                                datastore[key]["years"][str(year)][species]["phytosanitary"][iname][int(row['Classe_di_Tossicità'])] = {}
                                datastore[key]["years"][str(year)][species]["phytosanitary"][iname][
                                    int(row['Classe_di_Tossicità'])] = {
                                    "distributed_quantity_ha":row['Quantità_distribuita_per_Ha'],
                                    "phyto_area":row['SAU']
                                }





# --------------------------------------------------------------------------------------
#write datastore to a file in json format

if verbose_flag: print("writing data to ecowheataly_database_lca.txt file")
print(f'directory: {os.getcwd()}')
import json
with open("ecowheataly_database_lca.json", "w") as ewd:
    json.dump(datastore, ewd, indent=4)


