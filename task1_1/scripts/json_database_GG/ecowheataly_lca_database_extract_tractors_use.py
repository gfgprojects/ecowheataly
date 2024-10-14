#exec(open("ecowheataly_lca_database_extract_tractors_use.py").read())
data_on_h_tractors_per_h=[]
for key in farm_keys:
    tmp_farm_data=ewdata.get(key)
    tmp_farm_years=tmp_farm_data['years'].keys()
    for y in tmp_farm_years:
        tmp_farm_year_colture=tmp_farm_data['years'][y]['colture'].keys()
        if 'Frumento duro' in tmp_farm_year_colture:
            hom=tmp_farm_data['years'][y]['colture']['Frumento duro']['hours of own machines']
            hrm=tmp_farm_data['years'][y]['colture']['Frumento duro']['hours of rent machines']
            lu=tmp_farm_data['years'][y]['colture']['Frumento duro']['land_use(ha)']
            if lu>0:
                luph=round((hom+hrm)/lu,2)
                data_on_h_tractors_per_h.append([key,y,'Frumento duro',lu,luph])
                #print([key,y,'Frumento duro',lu,luph])
            else:
                print('land use=0')
                print([key,y,'Frumento duro',lu,luph])
import pandas as pd
h_tractors_df=pd.DataFrame(data=data_on_h_tractors_per_h,columns=['Farm ID','Year','Specie vegetale','Superficie coltivata','Ore uso macchina per ettaro'])
h_tractors_df.to_csv('dati_uso_carburanti.csv',index=False)

