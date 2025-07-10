#exec(open("ecowheataly_lca_database_prepare_table_250704.py").read())
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
    regione=tmp_farm_data['regione']
    provincia=tmp_farm_data['geo']
    altimetria=tmp_farm_data['zona altimetrica 3']
    tmp_farm_years=tmp_farm_data['years'].keys()
    genere=tmp_farm_data['genere']
    giovane=tmp_farm_data['giovane']
    for y in tmp_farm_years:
        tmp_farm_year_colture=tmp_farm_data['years'][y]['colture'].keys()
        if 'Frumento duro' in tmp_farm_year_colture and len(tmp_farm_year_colture)==1:
        #if 'Frumento duro' in tmp_farm_year_colture:
            hom=tmp_farm_data['years'][y]['colture']['Frumento duro']['hours of own machines']
            hrm=tmp_farm_data['years'][y]['colture']['Frumento duro']['hours of rent machines']
            lu_tot=tmp_farm_data['years'][y]['SAU(ha)']
            if hrm==float('inf'):
                hrm=0
            lu=tmp_farm_data['years'][y]['colture']['Frumento duro']['land_use(ha)']
            pq=tmp_farm_data['years'][y]['colture']['Frumento duro']['produced_quantity(ql)']
            if lu>0 and (hom+hrm)!=0:
                luph=round((hom+hrm)/lu,2)
                #yield
                tmp_yield=round(pq/lu,2)
                #Fertilizzanti
                Nxha=tmp_farm_data['years'][y]['colture']['Frumento duro']['fertilizzanti']['azoto a ha(kg)']
                Pxha=tmp_farm_data['years'][y]['colture']['Frumento duro']['fertilizzanti']['fosforo a ha(kg)']
                Kxha=tmp_farm_data['years'][y]['colture']['Frumento duro']['fertilizzanti']['potassio a ha(kg)']

                #Pesticidi
                number_of_herbicides_treatments=0
                number_of_insecticides_treatments=0
                number_of_coajuvants_treatments=0
                tot_herbicides_ha=0
                tot_insecticides_ha=0
                tot_coajuvants_ha=0
                tmp_farm_year_colture_fito=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']
                if 'Herbicides' in tmp_farm_year_colture_fito:
                    herb_keys=tmp_farm_year_colture_fito['Herbicides'].keys()
                    for hk in herb_keys:
                        surface=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']['Herbicides'][hk]['superficie trattata(ha)']
                        number_of_herbicides_treatments+=round(surface/lu)
                        #add to tot_herbicides_ha only if surfate greater than a share of lu
                        if surface>0.8*lu:
                            tot_herbicides_ha+=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']['Herbicides'][hk]['quantit. per ha(??)']
                if 'Insecticides' in tmp_farm_year_colture_fito:
                    insect_keys=tmp_farm_year_colture_fito['Insecticides'].keys()
                    for ik in insect_keys:
                        surface=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']['Insecticides'][ik]['superficie trattata(ha)']
                        number_of_insecticides_treatments+=round(surface/lu)
                        #add to tot_insecticides_ha only if surfate greater than a share of lu
                        if surface>0.8*lu:
                            tot_insecticides_ha+=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']['Insecticides'][ik]['quantit. per ha(??)']
                if 'Co-adjuvants' in tmp_farm_year_colture_fito:
                    coad_keys=tmp_farm_year_colture_fito['Co-adjuvants'].keys()
                    for ck in coad_keys:
                        surface=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']['Co-adjuvants'][ck]['superficie trattata(ha)']
                        number_of_coajuvants_treatments+=round(surface/lu)
                        #add to tot_coajuvants_ha only if surfate greater than a share of lu
                        if surface>0.8*lu:
                            tot_coajuvants_ha+=tmp_farm_data['years'][y]['colture']['Frumento duro']['fitofarmaci']['Co-adjuvants'][ck]['quantit. per ha(??)']
                    #print([key,y,'Frumento duro',lu,luph,Nxha,Pxha,Kxha,number_of_herbicides_treatments,number_of_insecticides_treatments,number_of_coajuvants_treatments])
                tot_herbicides_ha=round(tot_herbicides_ha,2)
                tot_insecticides_ha=round(tot_insecticides_ha,2)


                data_for_table.append([key,y,lu,pq,luph,Nxha,Pxha,Kxha,number_of_herbicides_treatments,number_of_insecticides_treatments,number_of_coajuvants_treatments,regione,provincia,altimetria,tot_herbicides_ha,tot_insecticides_ha,lu_tot,genere,giovane])
                #print([key,y,'Frumento duro',lu,luph])
            else:
                print('land use=0 or hours of tractors=0')
                print([key,y,'Frumento duro',lu,hom+hrm])


import pandas as pd
table_df=pd.DataFrame(data=data_for_table,columns=['Farm ID','Year','Superficie coltivata ha','Quantita prodotta ql','Ore uso macchina per ettaro','kg azoto per ettaro','kg fosforo per ettaro','kg potassio per ettaro','n trattamenti diserbanti','n trattamenti insetticidi','n trattamenti coadiuvanti','regione','provincia','altimetria','tot_diserbanti_ha','tot_insetticidi_ha','Superficie totale coltivata ha','genere','giovane'])

table_df.to_csv('dati_grano_duro.csv',index=False)

table_df_2016=table_df[table_df['Year']=='2016']
table_df_2022=table_df[table_df['Year']=='2022']

table_df_2016.to_csv('dati_grano_duro_2016.csv',index=False)
table_df_2022.to_csv('dati_grano_duro_2022.csv',index=False)

col_list= ['n trattamenti diserbanti', 'n trattamenti insetticidi', 'n trattamenti coadiuvanti']
col_list= ['n trattamenti diserbanti', 'n trattamenti insetticidi']
# Get sum of specific columns for each row
pest_df_2016 = table_df_2016[col_list].sum(axis=1)

