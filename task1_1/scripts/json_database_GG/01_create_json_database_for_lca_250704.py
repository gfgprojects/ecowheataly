#type
#exec(open("01_create_json_database.py").read())
#to run this script from the python prompt

import pandas as pd;
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
#    if verbose_flag: print("Importing data from bilancio_grano.csv")
#    ce_all = pd.read_csv('bilancio_grano.csv',sep=';',decimal=',');
    if verbose_flag: print("Importing data from aiuti_grano.csv")
    #aiuti_all = pd.read_csv('aiuti_grano.csv',sep=';',decimal=',');
#    if verbose_flag: print("Importing data from Uso_acqua_cereali.xlsx")
#    acqua_all = pd.read_csv('Uso_acqua_cereali.xlsx');
    if verbose_flag: print("Importing data from certificazioni_grano.csv")
    certificazioni_all = pd.read_csv('certificazioni_grano.csv',sep=';',decimal=',');

#farm codes
farm_codes=aziende_all['Cod_Azienda'].drop_duplicates();


#Create dataset called datastore and insert data from file aziende.xlsx

if verbose_flag: print("... writing farms general information ...")

datastore={}
for code in farm_codes:
 tmp_df=aziende_all.loc[aziende_all["Cod_Azienda"] == code].sort_values("Anno")
 tmp_df.index=range(tmp_df.shape[0])
 datastore[str(code)]={"count_in_farms_file(years)": int(tmp_df.shape[0]),"geo":tmp_df.loc[0,"Provincia"],"zona altimetrica 5":tmp_df.loc[0,"Zona_Altimetrica_5"],"zona altimetrica 3":tmp_df.loc[0,"Zona_Altimetrica_3"]}
 datastore[str(code)]["years"]={} 
 for runner in tmp_df.index:
  datastore[str(code)]["years"][str(tmp_df.loc[runner,"Anno"])]={"SAU(ha)":float(tmp_df.loc[runner,"SAU"]),"Produzione_Standard_Aziendale(Euro)":float(tmp_df.loc[runner,"Produzione_Standard_Aziendale"]),"KW_Macchine":float(tmp_df.loc[runner,"KW_Macchine"]),"colture":{}} 


#Insert data from colture.csv in datastore
if verbose_flag: print("... writing soft and hard wheat production data ...")

third_party_machine_makup=0.3
for key in datastore:
    tmp_df=colture_all.loc[colture_all["Cod_Azienda"] == int(key)].sort_values("Anno")
    tmp_df.index=range(tmp_df.shape[0])
    for runner in tmp_df.index:
        #compute machine hours
        tmp_year=tmp_df.loc[runner,"Anno"]
        third_party_machine_cost=tmp_df.loc[runner,"Contoterzismo"]
        hours_of_own_machines=tmp_df.loc[runner,"Ore_Macchina"]
        opportunity_cost_labor=aziende_all.loc[(aziende_all['Cod_Azienda']==int(key)) & (aziende_all["Anno"]==tmp_year),"Costo_Opp_Lavoro_Uomo_Orario"]
        opportunity_cost_machine=aziende_all.loc[(aziende_all['Cod_Azienda']==int(key)) & (aziende_all["Anno"]==tmp_year),"Costo_Opp_Lavoro_Macchina_Orario"]
        hours_of_rent_machines=round((third_party_machine_cost/((opportunity_cost_labor+opportunity_cost_machine)*(1+third_party_machine_makup))),2)
        if len(hours_of_rent_machines)>1:
            hours_of_rent_machines=list(hours_of_rent_machines)[0]
        cultivated_area=tmp_df.loc[runner,"SUPERFICIE_UTIL"]
        cost_of_own_machines=tmp_df.loc[runner,"Costo_Lav_Macchine"]
        if hours_of_own_machines >0:
            cost_own_machine_per_hour=round(cost_of_own_machines/hours_of_own_machines,2)
        else:
            cost_own_machine_per_hour=0
        #write data
        datastore[key]["years"][str(tmp_year)]["colture"][tmp_df.loc[runner,"Specie_Vegetale"]]={"produced_quantity(ql)": float(tmp_df.loc[runner,"QT_PROD_PRINC"]),"land_use(ha)": float(cultivated_area),"hours of own machines":float(hours_of_own_machines),"cost of own machines per hour":float(cost_own_machine_per_hour),"hours of rent machines":float(hours_of_rent_machines)}

#Insert data from fertilizzanti.csv in datastore
if verbose_flag: print("... writing fertilization data ...")
for key in datastore:
    tmp_df=fertilizzanti_all.loc[fertilizzanti_all["Cod_Azienda"] == int(key)].sort_values("Anno")
    if tmp_df.shape[0]>0:
        for year in datastore.get(key)["years"].keys():
            tmp_df_y=tmp_df.loc[tmp_df["Anno"]==int(year)]
            if tmp_df_y.shape[0]>0:
                tmp_df_y.index=range(tmp_df_y.shape[0])
                for veg_spec in datastore.get(key)["years"][year]["colture"].keys():
                    n_trattamenti=sum(tmp_df_y["Specie_Vegetale"]==veg_spec)
                    if n_trattamenti>0:
                        tmp_df_y_sv=tmp_df_y.loc[tmp_df_y["Specie_Vegetale"]==veg_spec]
                        tmp_df_y_sv.index=range(tmp_df_y_sv.shape[0])
                        datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fertilizzanti"]={"numero_items_in_file":int(n_trattamenti),"superficie fertilizzata(ha)":float(tmp_df_y_sv.loc[0,"Superficie_della_coltura"])}
                        azoto_per_ha=0
                        fosforo_per_ha=0
                        potassio_per_ha=0
                        for fert_item_idx in range(tmp_df_y_sv.shape[0]):
                            azoto_per_ha+=tmp_df_y_sv.loc[fert_item_idx,"Azoto_ad_ettaro"]
                            fosforo_per_ha+=tmp_df_y_sv.loc[fert_item_idx,"Fosforo_ad_ettaro"]
                            potassio_per_ha+=tmp_df_y_sv.loc[fert_item_idx,"Potassio_ad_ettaro"]
                        datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fertilizzanti"]["azoto a ha(kg)"]=float(round(azoto_per_ha,2))
                        datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fertilizzanti"]["fosforo a ha(kg)"]=float(round(fosforo_per_ha,2))
                        datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fertilizzanti"]["potassio a ha(kg)"]=float(round(potassio_per_ha,2))
                    else:
                        datastore[key]["years"][str(tmp_df_y.loc[0,"Anno"])]["colture"][veg_spec]["fertilizzanti"]={"numero_items_in_file":0,"superficie fertilizzata(ha)":0,"azoto a ha(kg)":0,"fosforo a ha(kg)":0,"potassio a ha(kg)":0}
            else:
                for veg_spec in datastore.get(key)["years"][year]["colture"].keys():
                    datastore[key]["years"][year]["colture"][veg_spec]["fertilizzanti"]={"numero_items_in_file":0,"superficie fertilizzata(ha)":0,"azoto a ha(kg)":0,"fosforo a ha(kg)":0,"potassio a ha(kg)":0}
    else:
        for year in datastore.get(key)["years"].keys():
            for veg_spec in datastore.get(key)["years"][year]["colture"].keys():
                datastore[key]["years"][year]["colture"][veg_spec]["fertilizzanti"]={"numero_items_in_file":0,"superficie fertilizzata(ha)":0,"azoto a ha(kg)":0,"fosforo a ha(kg)":0,"potassio a ha(kg)":0}
 
#Insert data from fitofarmaci.csv in datastore

if verbose_flag: print("... writing pesticides data ...")

for key in datastore:
    tmp_df=fitofarmaci_all.loc[fitofarmaci_all["Cod_Azienda"] == int(key)].sort_values("Anno")
    if tmp_df.shape[0]>0:
        for year in datastore.get(key)["years"].keys():
            tmp_df_y=tmp_df.loc[tmp_df["Anno"]==int(year)]
            if tmp_df_y.shape[0]>0:
                tmp_df_y.index=range(tmp_df_y.shape[0])
                for veg_spec in datastore.get(key)["years"][year]["colture"].keys():
                    n_trattamenti=sum(tmp_df_y["Specie_Vegetale"]==veg_spec)
                    if n_trattamenti>0:
                        tmp_df_y_sv=tmp_df_y.loc[tmp_df_y["Specie_Vegetale"]==veg_spec]
                        tmp_df_y_sv.index=range(tmp_df_y_sv.shape[0])
                        datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]={"numero_items_in_file":int(n_trattamenti),"Herbicides":{},"Insecticides":{},"Co-adjuvants":{}}
                        countDiserbante=0
                        countAnticrittogamico=0
                        countInsetticida=0
                        countAcaricida=0
                        countGeodisinfestante=0
                        countFitoregolatore=0
                        countBagnante=0
                        countCoadiuvante=0
                        countMolluschicida=0
                        countRepellente=0
                        for pest_item_idx in range(tmp_df_y_sv.shape[0]):
                            industrial_production=tmp_df_y_sv.loc[pest_item_idx,"Produzione_Industriale"]
                            match industrial_production:
                                case "Diserbante":
                                    countDiserbante+=1
                                    datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]["Herbicides"]["diserbante"+str(countDiserbante)]={"classe di tossicit.":int(tmp_df_y_sv.loc[pest_item_idx,"Classe_di_Tossicità"]),"superficie trattata(ha)":float(tmp_df_y_sv.loc[pest_item_idx,"SAU"]),"quantit. per ha(??)":float(tmp_df_y_sv.loc[pest_item_idx,"Quantità_distribuita_per_Ha"])}
                                case "Anticrittogamico":
                                    countAnticrittogamico+=1
                                    datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]["Insecticides"]["anticrittogamico"+str(countAnticrittogamico)]={"classe di tossicit.":int(tmp_df_y_sv.loc[pest_item_idx,"Classe_di_Tossicità"]),"superficie trattata(ha)":float(tmp_df_y_sv.loc[pest_item_idx,"SAU"]),"quantit. per ha(??)":float(tmp_df_y_sv.loc[pest_item_idx,"Quantità_distribuita_per_Ha"])}
                                case "Insetticida":
                                    countInsetticida+=1
                                    datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]["Insecticides"]["insetticida"+str(countInsetticida)]={"classe di tossicit.":int(tmp_df_y_sv.loc[pest_item_idx,"Classe_di_Tossicità"]),"superficie trattata(ha)":float(tmp_df_y_sv.loc[pest_item_idx,"SAU"]),"quantit. per ha(??)":float(tmp_df_y_sv.loc[pest_item_idx,"Quantità_distribuita_per_Ha"])}
                                case "Acaricida":
                                    countAcaricida+=1
                                    datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]["Insecticides"]["acaricida"+str(countAcaricida)]={"classe di tossicit.":int(tmp_df_y_sv.loc[pest_item_idx,"Classe_di_Tossicità"]),"superficie trattata(ha)":float(tmp_df_y_sv.loc[pest_item_idx,"SAU"]),"quantit. per ha(??)":float(tmp_df_y_sv.loc[pest_item_idx,"Quantità_distribuita_per_Ha"])}
                                case "Geodisinfestante":
                                    countGeodisinfestante+=1
                                    datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]["Insecticides"]["geodisinfestante"+str(countGeodisinfestante)]={"classe di tossicit.":int(tmp_df_y_sv.loc[pest_item_idx,"Classe_di_Tossicità"]),"superficie trattata(ha)":float(tmp_df_y_sv.loc[pest_item_idx,"SAU"]),"quantit. per ha(??)":float(tmp_df_y_sv.loc[pest_item_idx,"Quantità_distribuita_per_Ha"])}
                                case "Molluschicida, nematocida, rodenticida":
                                    countMolluschicida+=1
                                    datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]["Insecticides"]["molluschicida, nematocida, rodenticida"+str(countMolluschicida)]={"classe di tossicit.":int(tmp_df_y_sv.loc[pest_item_idx,"Classe_di_Tossicità"]),"superficie trattata(ha)":float(tmp_df_y_sv.loc[pest_item_idx,"SAU"]),"quantit. per ha(??)":int(tmp_df_y_sv.loc[pest_item_idx,"Quantità_distribuita_per_Ha"])}
                                case "Repellente":
                                    countRepellente+=1
                                    datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]["Insecticides"]["repellente"+str(countRepellente)]={"classe di tossicit.":int(tmp_df_y_sv.loc[pest_item_idx,"Classe_di_Tossicità"]),"superficie trattata(ha)":float(tmp_df_y_sv.loc[pest_item_idx,"SAU"]),"quantit. per ha(??)":float(tmp_df_y_sv.loc[pest_item_idx,"Quantità_distribuita_per_Ha"])}
                                case "Fitoregolatore":
                                    countFitoregolatore+=1
                                    datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]["Co-adjuvants"]["fitoregolatore"+str(countFitoregolatore)]={"classe di tossicit.":int(tmp_df_y_sv.loc[pest_item_idx,"Classe_di_Tossicità"]),"superficie trattata(ha)":float(tmp_df_y_sv.loc[pest_item_idx,"SAU"]),"quantit. per ha(??)":float(tmp_df_y_sv.loc[pest_item_idx,"Quantità_distribuita_per_Ha"])}
                                case "Bagnante, coadiuvante":
                                    countBagnante+=1
                                    datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]["Co-adjuvants"]["bagnante, coadiuvante"+str(countBagnante)]={"classe di tossicit.":int(tmp_df_y_sv.loc[pest_item_idx,"Classe_di_Tossicità"]),"superficie trattata(ha)":float(tmp_df_y_sv.loc[pest_item_idx,"SAU"]),"quantit. per ha(??)":float(tmp_df_y_sv.loc[pest_item_idx,"Quantità_distribuita_per_Ha"])}
                                case "Coadiuvante":
                                    countCoadiuvante+=1
                                    datastore[key]["years"][str(tmp_df_y_sv.loc[0,"Anno"])]["colture"][tmp_df_y_sv.loc[0,"Specie_Vegetale"]]["fitofarmaci"]["Co-adjuvants"]["coadiuvante"+str(countCoadiuvante)]={"classe di tossicit.":int(tmp_df_y_sv.loc[pest_item_idx,"Classe_di_Tossicità"]),"superficie trattata(ha)":float(tmp_df_y_sv.loc[pest_item_idx,"SAU"]),"quantit. per ha(??)":float(tmp_df_y_sv.loc[pest_item_idx,"Quantità_distribuita_per_Ha"])}
                    else:
                        datastore[key]["years"][str(tmp_df_y.loc[0,"Anno"])]["colture"][veg_spec]["fitofarmaci"]={"numero_items_in_file":0}
            else:
                for veg_spec in datastore.get(key)["years"][year]["colture"].keys():
                    datastore[key]["years"][year]["colture"][veg_spec]["fitofarmaci"]={"numero_items_in_file":0}
    else:
        for year in datastore.get(key)["years"].keys():
            for veg_spec in datastore.get(key)["years"][year]["colture"].keys():
                datastore[key]["years"][year]["colture"][veg_spec]["fitofarmaci"]={"numero_items_in_file":0}


#write datastore to a file in json format

if verbose_flag: print("writing data to ecowheataly_database_lca.json file")
import json
with open("ecowheataly_database_lca.json", "w") as ewd:
    json.dump(datastore, ewd, indent=4)




