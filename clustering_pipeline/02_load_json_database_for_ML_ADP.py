
import json
import numpy as np
import pandas as pd

with open("ecowheataly_database_lca.json") as ewdj:
  data = json.load(ewdj)
# SAREBBE DA AGGIUNGERE AL JSON DATABSE:
# AZIENDE: ' Reddito_Netto','Aiuti_EU','Aiuti_Pubblici_Conto_Capitale','Aiuti_altri'


# anno, colture, Frumento duro, fertilizzanti, fitofarmaci
wheat_vars = ['produced_quantity','crop_acreage','hours_of_machines_ha']
# fertilizzanti, fitofarmaci
fert_vars = ['nitrogen_ha','phosphorus_ha',
                'potassium_ha','fert_area']
phy_vars_type = ['Herbicide', 'Insecticide', 'Fungicide']
phy_vars = ['distribuited_quantity','phyto_area']
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
def extract_data(data, anno, farms, wheat_vars, fert_vars,species='durum_wheat'):
    columns =['year', 'farm code','farm_acreage',species] + wheat_vars + fert_vars
    data_list = []

    for fid in farms:
        try:
            farm_acreage = data[fid]['years'][anno]['farm_acreage']
            crop = data[fid]['years'][anno][species]
            row = [anno, fid,farm_acreage,species]

            # extract data recalled in wheat_vars
            row.extend(crop.get(key, 0) for key in wheat_vars)

            # extract data recalled in fert_vars
            fertilizers = crop['fertilizers']
            row.extend(fertilizers.get(key, 0) for key in fert_vars)

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

Vars_name = ['year', 'farm code','farm_acreage','species'] + wheat_vars + fert_vars
years = np.arange(2008,2023)
for year in years:
    if year == years[0]:
        Mat = extract_data(data, str(year), farms, wheat_vars, fert_vars)
    else:
        mat = extract_data(data, str(year), farms, wheat_vars, fert_vars)
        Mat.extend(mat)


dtypes = {}
for i in range(len(Vars_name)):
    if i <2:
        dtypes[i] ='int'
    elif i ==3:
        dtypes[i] ='str'
    else:
        dtypes[i] = 'float'

df1 = pd.DataFrame(Mat,columns=Vars_name)
dtypes1 = {col: 'int' if i < 2 else 'str' if i == 3 else 'float' for i, col in enumerate(df1.columns)}
df1 = df1.astype(dtypes1)


# NOTES:
# >> manage the "inf" in the hours_of_machines (due to 0 costs in the Azienda.scv files)



## PART 2 : Pythosanitary


types  =['Herbicide', 'Insecticide', 'Fungicide']
ColName = ['year','farm code','Qt Tox-0','Qt Tox-1','Qt Tox-2','Qt Tox-3','Qt Tox-4']
Mat2 = []
for T,TYPE in enumerate(types):
    print(f'organizzando {TYPE}')
    mat = []
    for year in years:
        print(year)
        for i, fid in enumerate(farms):
            try:
                # ------------prova 1----------------------------------------

                crop = data[fid]['years'][str(year)][species]
                row = np.full((7,), np.nan, dtype=object)
                row[0:2] = [year,np.array(fid, dtype=np.int64)]

                # Estrazione variabili ft
                phyto = crop['phytosanitary']

                try:
                    # len(phyto[TYPE]) >=1
                    val = {}
                    # for item in phyto[TYPE].values():
                    #     print(item)
                    #     classe = item['classe di tossicit.']
                    #     prodotto = item['superficie trattata(ha)'] * item['quantit. per ha(??)']
                    #     val[classe] = val.get(classe, 0) + prodotto
                    for item in phyto[TYPE].keys():
                        # print(item)
                        classe=int(item)
                        item_data = phyto[TYPE][item]
                        prodotto = item_data['distributed_quantity_ha'] * item_data['phyto_area']
                        val[classe] = val.get(classe, 0) + prodotto
                        # print(val)
                    for c,v in val.items():
                        row[c+2]= float(v)
                    mat.append(row)
                except:
                    mat.append(row) # year, farm code + 5 nan


            except KeyError:
                pass
    Mat2.append(mat)

# store the data into 3D arrays for plots
Phyto = np.stack(Mat2,axis=2)

Mat2 = np.concatenate(Mat2,axis=1)
# # checked!
# for i,r in enumerate(Mat2):
#     if r[1]!=r[8]:
#         print(i,r)
#     if r[1]!=r[15]:
#         print(i,r)
#     if r[8]!=r[15]:
#         print(i,r)
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
Mat2 = np.delete(Mat2,cols_todel,axis=1)

df2 = pd.DataFrame(Mat2, columns=df_colname )
dtypes2 = {col: 'int' if i < 2  else 'float' for i, col in enumerate(df2.columns)}
df2 = df2.astype(dtypes2)




## MERGING df1 with df2


flat_df = pd.merge(df1, df2, on=['year', 'farm code'], how='left')
# where there are no data on Phytosanitary means that the farm didn't use it in that year
# hence we insert 0 and 0 must be kept as good value!
flat_df.fillna(0, inplace=True)

# dtypes = dtypes1 | dtypes2
# flat_dtypes = dtypes1.copy()  # Copia per non modificare dtypes1
# flat_dtypes.update(dtypes2)
# flat_df.astype(flat_dtypes)


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


flat_df.to_csv("data/flat_df.csv", index=False)

