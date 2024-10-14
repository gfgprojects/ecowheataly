#exec(open("ecowheataly_lca_database_stats.py").read())
import os
import json
import pandas as pd;

write_latex_tables_to_file=False

#load ecowheataly_database.json

#if 'ewdata' not in locals():
if True:
    with open("ecowheataly_database_lca.json") as ewdj:
        ewdata = json.load(ewdj)

farm_keys=list(ewdata.keys())


#number of years each firm appears in the database

counts=[ewdata.get(key)["count_in_farms_file(years)"] for key in ewdata]
#compute a frequency table
c_s=pd.Series(counts)
ages=c_s.value_counts()

#write the frequency table in a file in latex format
ages_to_sort=pd.DataFrame(data={"farm age": ages.index,"farms count": ages})
ages_sorted=ages_to_sort.sort_values("farm age")
if write_latex_tables_to_file:
    with open('table_ages_frequencies.tex', 'w') as tf:
         tf.write(ages_sorted.to_latex(index=False,column_format="cc"))

#get farms that appear most often
elder=[[key,ewdata.get(key)["count_in_farms_file(years)"]] for key in ewdata if ewdata.get(key)["count_in_farms_file(years)"]==max(ages.index)]
#print info on the first farm of the list
code=elder[0][0]
json_item=json.dumps(ewdata[code],indent=4)


#identify years and provinces
allyears=[]
allprovinces=[]
for key in farm_keys:
    farm_years=list(ewdata.get(key)['years'].keys())
    allyears.extend(farm_years)
    allprovinces.append(ewdata.get(key)['geo'])

str_period=sorted(list(set(allyears)))
int_period=[int(y) for y in str_period]

str_provinces=sorted(list(set(allprovinces)))

province_year_hard_table=pd.DataFrame(0,index=str_provinces,columns=str_period)
province_year_soft_table=pd.DataFrame(0,index=str_provinces,columns=str_period)
province_year_both_table=pd.DataFrame(0,index=str_provinces,columns=str_period)

n_farms=[0]*len(str_period)
n_farms_soft=[0]*len(str_period)
n_farms_hard=[0]*len(str_period)
n_farms_both=[0]*len(str_period)
n_farms_soft_using_fertilizers=[0]*len(str_period)
n_farms_hard_using_fertilizers=[0]*len(str_period)
n_farms_both_using_fertilizers=[0]*len(str_period)
n_farms_soft_using_herbicides=[0]*len(str_period)
n_farms_hard_using_herbicides=[0]*len(str_period)
n_farms_both_using_herbicides=[0]*len(str_period)
n_farms_soft_using_insecticides=[0]*len(str_period)
n_farms_hard_using_insecticides=[0]*len(str_period)
n_farms_both_using_insecticides=[0]*len(str_period)
n_farms_soft_using_coadjuvants=[0]*len(str_period)
n_farms_hard_using_coadjuvants=[0]*len(str_period)
n_farms_both_using_coadjuvants=[0]*len(str_period)
hectares_hard_only=[0]*len(str_period)
hectares_soft_only=[0]*len(str_period)
hectares_hard_both=[0]*len(str_period)
hectares_soft_both=[0]*len(str_period)

threshold_on_land_use_ratio=0.5
threshold_on_land_use_value=2.0
n_farms_soft_above_thresholds=[0]*len(str_period)
n_farms_hard_above_thresholds=[0]*len(str_period)
n_farms_both_above_thresholds=[0]*len(str_period)

for i in range(0,len(str_period)):
    for key in farm_keys:
        if str_period[i] in ewdata.get(key)['years'].keys():
            n_farms[i]+=1
            if len(ewdata.get(key)['years'][str_period[i]]['colture'].keys())==1:
                if 'Frumento tenero' in ewdata.get(key)['years'][str_period[i]]['colture'].keys():
                    n_farms_soft[i]+=1
                    province_year_soft_table.at[ewdata.get(key)['geo'],str_period[i]]+=1
                    this_farm_wheat_land_use=round(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['land_use(ha)'],2)
                    this_farm_total_land_use=round(ewdata.get(key)['years'][str_period[i]]['SAU(ha)'],2)
                    if this_farm_total_land_use>0:  #a few firms have total land use equal to zero
                        if this_farm_wheat_land_use>threshold_on_land_use_value:
                            this_farm_land_use_ratio=round(this_farm_wheat_land_use/this_farm_total_land_use,2)
                            if this_farm_land_use_ratio>threshold_on_land_use_ratio:
                                n_farms_soft_above_thresholds[i]+=1
                    hectares_soft_only[i]+=this_farm_wheat_land_use
                    if ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['fertilizzanti']['numero_items_in_file']>0:
                        n_farms_soft_using_fertilizers[i]+=1
                    if ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['fitofarmaci']['numero_items_in_file']>0:
                        if len(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['fitofarmaci']['Herbicides'].keys())>0:
                            n_farms_soft_using_herbicides[i]+=1
                        if len(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['fitofarmaci']['Insecticides'].keys())>0:
                            n_farms_soft_using_insecticides[i]+=1
                        if len(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['fitofarmaci']['Co-adjuvants'].keys())>0:
                            n_farms_soft_using_coadjuvants[i]+=1
                else:
                    n_farms_hard[i]+=1
                    province_year_hard_table.at[ewdata.get(key)['geo'],str_period[i]]+=1
                    this_farm_wheat_land_use=round(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['land_use(ha)'],2)
                    this_farm_total_land_use=round(ewdata.get(key)['years'][str_period[i]]['SAU(ha)'],2)
                    if this_farm_total_land_use>0:  #a few firms have total land use equal to zero
                        if this_farm_wheat_land_use>threshold_on_land_use_value:
                            this_farm_land_use_ratio=round(this_farm_wheat_land_use/this_farm_total_land_use,2)
                            if this_farm_land_use_ratio>threshold_on_land_use_ratio:
                                n_farms_hard_above_thresholds[i]+=1
                    hectares_hard_only[i]+=round(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['land_use(ha)'],2)
                    if ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['fertilizzanti']['numero_items_in_file']>0:
                        n_farms_hard_using_fertilizers[i]+=1
                    if ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['fitofarmaci']['numero_items_in_file']>0:
                        if len(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['fitofarmaci']['Herbicides'].keys())>0:
                            n_farms_hard_using_herbicides[i]+=1
                        if len(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['fitofarmaci']['Insecticides'].keys())>0:
                            n_farms_hard_using_insecticides[i]+=1
                        if len(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['fitofarmaci']['Co-adjuvants'].keys())>0:
                            n_farms_hard_using_coadjuvants[i]+=1
            if len(ewdata.get(key)['years'][str_period[i]]['colture'].keys())==2:
                    n_farms_both[i]+=1
                    province_year_both_table.at[ewdata.get(key)['geo'],str_period[i]]+=1
                    this_farm_wheat_land_use=round(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['land_use(ha)']+ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['land_use(ha)'],2)
                    this_farm_total_land_use=round(ewdata.get(key)['years'][str_period[i]]['SAU(ha)'],2)
                    if this_farm_total_land_use>0:  #a few firms have total land use equal to zero
                        if this_farm_wheat_land_use>threshold_on_land_use_value:
                            this_farm_land_use_ratio=round(this_farm_wheat_land_use/this_farm_total_land_use,2)
                            if this_farm_land_use_ratio>threshold_on_land_use_ratio:
                                n_farms_both_above_thresholds[i]+=1
                    hectares_soft_both[i]+=round(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['land_use(ha)'],2)
                    hectares_hard_both[i]+=round(ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['land_use(ha)'],2)
                    
                    tmp1=ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['fertilizzanti']['numero_items_in_file']
                    tmp2=ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['fertilizzanti']['numero_items_in_file']
                    
                    if (tmp1>0) or (tmp2>0):
                        n_farms_both_using_fertilizers[i]+=1
                    
                    tmp1=ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['fitofarmaci']['numero_items_in_file']
                    tmp2=ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['fitofarmaci']['numero_items_in_file']
                    
                    if (tmp1>0) or (tmp2>0):
                        
                        tmp1 = ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['fitofarmaci'].get("Herbicides")
                        tmp2 = ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['fitofarmaci'].get("Herbicides")
                        
                        if tmp1 or tmp2:
                            n_farms_both_using_herbicides[i]+=1
                        
                        tmp1 = ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['fitofarmaci'].get("Insecticides")
                        tmp2 = ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['fitofarmaci'].get("Insecticides")
                        
                        if tmp1 or tmp2:
                            n_farms_both_using_insecticides[i]+=1
                        
                        tmp1 = ewdata.get(key)['years'][str_period[i]]['colture']['Frumento duro']['fitofarmaci'].get('Co-adjuvants')
                        tmp2 = ewdata.get(key)['years'][str_period[i]]['colture']['Frumento tenero']['fitofarmaci'].get('Co-adjuvants')
                        
                        if tmp1 or tmp2:
                            n_farms_both_using_coadjuvants[i]+=1

#aggregate hectares
hectares_hard=[hectares_hard_only[i]+hectares_hard_both[i] for i in range(0,len(str_period))]
hectares_soft=[hectares_soft_only[i]+hectares_soft_both[i] for i in range(0,len(str_period))]
hectares_total=[hectares_hard[i]+hectares_soft[i] for i in range(0,len(str_period))]
    

#define table numbers per year
#data_per_year=pd.DataFrame(data={"years":int_period,"n hard only": n_farms_hard,"n soft only": n_farms_soft,"n both": n_farms_both,"n farms total": n_farms,"ha hard":hectares_hard,"ha soft":hectares_soft,"ha total":hectares_total})
data_per_year=pd.DataFrame(data={"\\rotatebox{90}{years}":int_period,"\\rotatebox{90}{n hard only}": n_farms_hard,"\\rotatebox{90}{n soft only}": n_farms_soft,"\\rotatebox{90}{n both}": n_farms_both,"\\rotatebox{90}{n farms total}": n_farms,"\\rotatebox{90}{ha hard}":hectares_hard,"\\rotatebox{90}{ha soft}":hectares_soft,"\\rotatebox{90}{ha total}":hectares_total})
if write_latex_tables_to_file:
    with open('table_n_farms_per_year.tex', 'w') as tf:
         tf.write(data_per_year.to_latex(index=False,column_format="c|cccc|ccc",float_format="%.0f"))
#define table numbers using fertilizers and pesticides
#data_fert_pest=pd.DataFrame(data={"n farms soft using fertilizers" :n_farms_soft_using_fertilizers,"n farms hard using fertilizers" :n_farms_hard_using_fertilizers,"n farms both using fertilizers" :n_farms_both_using_fertilizers,"n farms soft using herbicides"  :n_farms_soft_using_herbicides,"n farms hard using herbicides"  :n_farms_hard_using_herbicides,"n farms both using herbicides"  :n_farms_both_using_herbicides,"n farms soft using insecticides":n_farms_soft_using_insecticides,"n farms hard using insecticides":n_farms_hard_using_insecticides,"n farms both using insecticides":n_farms_both_using_insecticides,"n farms soft using coadjuvants" :n_farms_soft_using_coadjuvants,"n farms hard using coadjuvants" :n_farms_hard_using_coadjuvants,"n farms both using coadjuvants" :n_farms_both_using_coadjuvants})
data_fert_pest=pd.DataFrame(data={
    "\\rotatebox{90}{years}":int_period,
    "\\rotatebox{90}{n farms hard using fertilizers}" :n_farms_hard_using_fertilizers,
    "\\rotatebox{90}{n farms hard using herbicides}"  :n_farms_hard_using_herbicides,
    "\\rotatebox{90}{n farms hard using insecticides}":n_farms_hard_using_insecticides,
    "\\rotatebox{90}{n farms hard using coadjuvants}" :n_farms_hard_using_coadjuvants,
    "\\rotatebox{90}{n farms soft using fertilizers}" :n_farms_soft_using_fertilizers,
    "\\rotatebox{90}{n farms soft using herbicides}"  :n_farms_soft_using_herbicides,
    "\\rotatebox{90}{n farms soft using insecticides}":n_farms_soft_using_insecticides,
    "\\rotatebox{90}{n farms soft using coadjuvants}" :n_farms_soft_using_coadjuvants,
    "\\rotatebox{90}{n farms both using fertilizers}" :n_farms_both_using_fertilizers,
    "\\rotatebox{90}{n farms both using herbicides}"  :n_farms_both_using_herbicides,
    "\\rotatebox{90}{n farms both using insecticides}":n_farms_both_using_insecticides,
    "\\rotatebox{90}{n farms both using coadjuvants}" :n_farms_both_using_coadjuvants})

if write_latex_tables_to_file:
    with open('table_n_farms_using_fert_pest.tex', 'w') as tf:
         tf.write(data_fert_pest.to_latex(index=False,column_format="c|cccc|cccc|cccc"))

province_year_hard_table.to_csv('province_year_hard_greater_than_'+str(threshold_on_land_use_value)+'ha_threshold_'+str(threshold_on_land_use_ratio)+'.csv')
province_year_soft_table.to_csv('province_year_soft_greater_than_'+str(threshold_on_land_use_value)+'ha_threshold_'+str(threshold_on_land_use_ratio)+'.csv')
province_year_both_table.to_csv('province_year_both_greater_than_'+str(threshold_on_land_use_value)+'ha_threshold_'+str(threshold_on_land_use_ratio)+'.csv')
#os.system

  
