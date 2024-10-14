#exec(open("ecowheataly_lca_database_prepare_table.py").read())
import json
import pandas as pd;


#load ecowheataly_database.json

#if 'ewdata' not in locals():
if True:
    with open("ecowheataly_database_lca.json") as ewdj:
        ewdata = json.load(ewdj)

farm_keys=list(ewdata.keys())


data_for_table=[]
for key in farm_keys:
    tmp_farm_data=ewdata.get(key)
    tmp_farm_years=tmp_farm_data['years'].keys()
    for y in tmp_farm_years:
        tmp_farm_year_colture=tmp_farm_data['years'][y]['colture'].keys()
        if 'Frumento duro' in tmp_farm_year_colture and len(tmp_farm_year_colture)==1:
        #if 'Frumento duro' in tmp_farm_year_colture:
            hom=tmp_farm_data['years'][y]['colture']['Frumento duro']['hours of own machines']
            hrm=tmp_farm_data['years'][y]['colture']['Frumento duro']['hours of rent machines']
            if hrm==float('inf'):
                hrm=0
            lu=tmp_farm_data['years'][y]['colture']['Frumento duro']['land_use(ha)']
            if lu>0 and (hom+hrm)!=0:
                luph=round((hom+hrm)/lu,2)
                #Fertilizzanti
                Nxha=tmp_farm_data['years'][y]['colture']['Frumento duro']['fertilizzanti']['azoto a ha(kg)']
                Pxha=tmp_farm_data['years'][y]['colture']['Frumento duro']['fertilizzanti']['fosforo a ha(kg)']
                Kxha=tmp_farm_data['years'][y]['colture']['Frumento duro']['fertilizzanti']['potassio a ha(kg)']

                #Pesticidi
                number_of_herbicides_treatments=0
                number_of_insecticides_treatments=0
                number_of_coajuvants_treatments=0
                tmp_farm_year_colture_fito=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']
                if 'Herbicides' in tmp_farm_year_colture_fito:
                    herb_keys=tmp_farm_year_colture_fito['Herbicides'].keys()
                    for hk in herb_keys:
                        surface=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']['Herbicides'][hk]['superficie trattata(ha)']
                        number_of_herbicides_treatments+=round(surface/lu)
                if 'Insecticides' in tmp_farm_year_colture_fito:
                    insect_keys=tmp_farm_year_colture_fito['Insecticides'].keys()
                    for ik in insect_keys:
                        surface=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']['Insecticides'][ik]['superficie trattata(ha)']
                        number_of_insecticides_treatments+=round(surface/lu)
                if 'Co-adjuvants' in tmp_farm_year_colture_fito:
                    coad_keys=tmp_farm_year_colture_fito['Co-adjuvants'].keys()
                    for ck in coad_keys:
                        surface=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']['Co-adjuvants'][ck]['superficie trattata(ha)']
                        number_of_coajuvants_treatments+=round(surface/lu)
                    #print([key,y,'Frumento duro',lu,luph,Nxha,Pxha,Kxha,number_of_herbicides_treatments,number_of_insecticides_treatments,number_of_coajuvants_treatments])


                data_for_table.append([key,y,lu,luph,Nxha,Pxha,Kxha,number_of_herbicides_treatments,number_of_insecticides_treatments,number_of_coajuvants_treatments])
                #print([key,y,'Frumento duro',lu,luph])
            else:
                print('land use=0 or hours of tractors=0')
                print([key,y,'Frumento duro',lu,hom+hrm])


import pandas as pd
table_df=pd.DataFrame(data=data_for_table,columns=['Farm ID','Year','Superficie coltivata','Ore uso macchina per ettaro','kg azoto per ettaro','kg fosforo per ettaro','kg potassio per ettaro','n trattamenti diserbanti','n trattamenti insetticidi','n trattamenti coadiuvanti'])

#table_df.to_csv('dati_grano_duro.csv',index=False)

table_df_2016=table_df[table_df['Year']=='2016']
table_df_2022=table_df[table_df['Year']=='2022']

table_df_2016.to_csv('dati_grano_duro_2016.csv',index=False)
table_df_2022.to_csv('dati_grano_duro_2022.csv',index=False)

col_list= ['n trattamenti diserbanti', 'n trattamenti insetticidi', 'n trattamenti coadiuvanti']
col_list= ['n trattamenti diserbanti', 'n trattamenti insetticidi']
# Get sum of specific columns for each row
pest_df_2016 = table_df_2016[col_list].sum(axis=1)

