#add_recipe_2016()
import bw2data as bd
import pandas as pd
import numpy as np




edb = bd.Database("ecowheataly")
edb.register()
wheat_prod=edb.new_activity(code = 'EcoWheataly production', name = "EcoWheataly production", unit = "ha")
#wheat_prod.new_exchange(input=('usda_item','ccfa048cb86343798ac04f50a504c3af'),amount=900,unit="megajoule",type='technosphere').save()
wheat_prod.new_exchange(input=('usda_item','work; ag. tractors for growing win wheat, 2014 fleet, all fuels; 100-175HP'),amount=MJ,unit="megajoule",type='technosphere').save()
wheat_prod.new_exchange(input=('bentrup_item','application to N fertilizer use in winter wheat production systems'),amount=50,unit="kilogram",type='technosphere').save()
#Fungicide harmful: 'Tebuconazole' (kilogram, None, ('soil', 'agricultural'))
wheat_prod.new_exchange(input=('biosphere3','a805071f-ce96-4d72-bdd5-4334d9aa3c23'),amount=Fungicide_harmful,unit="kilogram",type='biosphere').save()
#Herbicide caution: 'Glyphosate' (kilogram, None, ('soil', 'agricultural'))
wheat_prod.new_exchange(input=('biosphere3','3850d44e-8919-47bc-9c0a-51ccc4ec9d9f'),amount=Herbicide_caution,unit="kilogram",type='biosphere').save()
#Herbicide irritationg: '2,4-D dimethylamine salt' (kilogram, None, ('soil', 'agricultural'))
wheat_prod.new_exchange(input=('biosphere3','41a4e1fe-34ee-54d9-b049-3a60ada1ae3e'),amount=Herbicide_irritating,unit="kilogram",type='biosphere').save()
#Herbicide harmful: 'MCPA' (kilogram, None, ('soil', 'agricultural'))
wheat_prod.new_exchange(input=('biosphere3','e5492922-eaf5-4409-aa49-7f2a35cd0336'),amount=Herbicide_harmful,unit="kilogram",type='biosphere').save()
#Growth regulator harmful: 'Trinexapac-ethyl' (kilogram, None, ('soil', 'agricultural'))
wheat_prod.new_exchange(input=('biosphere3','51c7daf4-14e1-45e9-aa67-051c4ddcd9da'),amount=GrowthRegulator_harmful,unit="kilogram",type='biosphere').save()
#Insecticide_harmful: 'Deltamethrin' (kilogram, None, ('soil', 'agricultural'))
wheat_prod.new_exchange(input=('biosphere3','282973e4-3c2d-4a9c-a3f2-d39a5b36aa76'),amount=Insecticide_harmful,unit="kilogram",type='biosphere').save()
#Insecticide toxic: 'Pirimicarb' (kilogram, None, ('soil', 'agricultural'))
wheat_prod.new_exchange(input=('biosphere3','1c0699e2-9be2-4c30-8328-fc0ad8caac58'),amount=Insecticide_toxic,unit="kilogram",type='biosphere').save()
#Molluscicide irritating: 'Metaldehyde' (kilogram, None, ('soil', 'agricultural'))
wheat_prod.new_exchange(input=('biosphere3','597847df-518f-4bd6-ae50-1de01f2761a4'),amount=Molluscicide_irritating,unit="kilogram",type='biosphere').save()
wheat_prod.save()

for i,activity in enumerate(edb):
    print(f"Chiave: {activity.key}, Tipo: {type(activity.key)}, Lunghezza: {len(activity.key)}")
    print(activity)

import pandas as pd
activity.as_dict()
df_ex = pd.DataFrame(activity.exchanges())



functional_unit={edb.get('EcoWheataly production'): 1}
#chosen_methods=[('IPCC 2013', 'climate change', 'global warming potential (GWP100)'),('USEtox', 'ecotoxicity', 'total')];
recipe=[m for m in bd.methods if 'ReCiPe 2016' in str(m) and '20180117' in str(m)]

chosen_methods=recipe

import bw2calc as bc
all_scores = {}
wheat_lca = bc.LCA(functional_unit,chosen_methods[0])
wheat_lca.lci()
wheat_lca.lcia()
for category in chosen_methods:
    wheat_lca.switch_method(category)
    wheat_lca.lcia()
    all_scores[category] = {}
    all_scores[category]['score'] = wheat_lca.score
    all_scores[category]['unit'] = bd.Method(category).metadata['unit']

#++++++ OUTPUT TO SCREEN +++++++++

print("");
print("LCA results:")
print("");
df = pd.DataFrame.from_dict(all_scores).T
print('Methodology: '+df.index[0][0])
print('Version: '+df.index[0][1])
#print('Level: '+df.index[0][2])
print("================= Midpoint analysis ===============")

summary_data=[]
for idx in df.index:
    #summary_data.append([idx[3],idx[4],idx[5],round(df.loc[idx,'score'],4),df.loc[idx,'unit']])
    summary_data.append([idx[3],idx[4],idx[5],df.loc[idx,'score'],df.loc[idx,'unit']])

lca_results=pd.DataFrame(summary_data,columns=['Method','Damage to','Geo CFs','Score','Unit'])
print(lca_results)


print("================= Endpoint analysis ===============")


# Brightwau ha dei metodi con cui iniziare?
Methods = pd.DataFrame(bd.methods)

# ii = np.isin(Methods.iloc[:,0],'ReCiPe 2016')
# recipe2 = Methods.iloc[ii]
chosen_methods=recipe_ecow_end


all_scores = {}
wheat_lca = bc.LCA(functional_unit,chosen_methods[0])
wheat_lca.lci()
wheat_lca.lcia()
for category in chosen_methods:
    wheat_lca.switch_method(category)
    wheat_lca.lcia()
    all_scores[category] = {}
    all_scores[category]['score'] = wheat_lca.score
    all_scores[category]['unit'] = bd.Method(category).metadata['unit']

df = pd.DataFrame.from_dict(all_scores).T
summary_data=[]
for idx in df.index:
    #summary_data.append([idx[3],idx[4],idx[5],round(df.loc[idx,'score'],4),df.loc[idx,'unit']])
    summary_data.append([idx[3],idx[4],idx[5],df.loc[idx,'score'],df.loc[idx,'unit']])

lca_results=pd.DataFrame(summary_data,columns=['Method','Damage to','Geo CFs','Score','Unit'])
print(lca_results)









# Brightwau ha dei metodi con cui iniziare?
Methods = pd.DataFrame(bd.methods)

ii = np.isin(Methods.iloc[:,0],'ReCiPe 2016')
recipe2 = Methods.iloc[ii]

recipe=[m for m in bd.methods if 'ReCiPe 2016' in str(m) and '20180117' in str(m)]
recipe_Im=[m for m in recipe if 'Individualist' in str(m) and 'Midpoint' in str(m)]
recipe_Hm=[m for m in recipe if 'Hierarchist' in str(m) and 'Midpoint' in str(m)]
recipe_Em=[m for m in recipe if 'Egalitarian' in str(m) and 'Midpoint' in str(m)]
recipe_NP=[m for m in recipe if 'Individualist' not in str(m) and 'Hierarchist' not in str(m) and 'Egalitarian' not in str(m)]
recipe_Ie=[m for m in recipe if 'Individualist' in str(m) and 'Endpoint' in str(m)]
recipe_He=[m for m in recipe if 'Hierarchist' in str(m) and 'Endpoint' in str(m)]
recipe_Ee=[m for m in recipe if 'Egalitarian' in str(m) and 'Endpoint' in str(m)]

print()
print("Regionalizing Terrestrial acidification Midpoint")
amm_conversion_coef=4.76/1.96
nit_conversion_coef=0.7/0.36
sul_conversion_coef=1.25/1

tmp_method_name=list(recipe_NP)[1]
tmp_method=bd.Method(tmp_method_name)
tmp_method_unit=tmp_method.metadata['unit']
method_cfs=tmp_method.load()
#print(*method_cfs,sep='\n')
new_CFs=[]
bs3=bd.Database("biosphere")
for cf in method_cfs:
	print(cf)
    element_name=bs3.get(cf[0][1])['name']
    if 'Sul' in element_name:
        #print(str(bs3.get(cf[0][1]))+" .......... CF: "+str(cf[1]))
        #print(str(bs3.get(cf[0][1]))+" .......... CF: "+str(round(cf[1]*sul_conversion_coef,2)))
        new_CFs.append([cf[0],cf[1]*sul_conversion_coef])
    elif 'Nit' in element_name:
        #print(str(bs3.get(cf[0][1]))+" .......... CF: "+str(cf[1]))
        #print(str(bs3.get(cf[0][1]))+" .......... CF: "+str(round(cf[1]*nit_conversion_coef,2)))
        new_CFs.append([cf[0],cf[1]*nit_conversion_coef])
    elif 'Amm' in element_name:
        #print(str(bs3.get(cf[0][1]))+" .......... CF: "+str(cf[1]))
        #print(str(bs3.get(cf[0][1]))+" .......... CF: "+str(round(cf[1]*amm_conversion_coef,2)))
        new_CFs.append([cf[0],cf[1]*amm_conversion_coef])
new_method_name=tmp_method_name+('Ecosystems','Italy','ecowheataly')
ReCiPe_2016_terrestrial_acidification_Italy = bd.Method(new_method_name);
ReCiPe_2016_terrestrial_acidification_Italy.validate(new_CFs);
ReCiPe_2016_terrestrial_acidification_Italy.register(**{'unit':tmp_method_unit});
ReCiPe_2016_terrestrial_acidification_Italy.write(new_CFs);


print("Regionalizing Terrestrial acidification Endpoint Egalitarian")
tmp_method_name=('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Terrestrial ecosystems', 'Terrestrial Acidification', 'Egalitarian')
tmp_method=bd.Method(tmp_method_name)
tmp_method_unit=tmp_method.metadata['unit']
method_cfs=tmp_method.load()
new_CFs=[]
for cf in method_cfs:
    element_name=bs3.get(cf[0][1])['name']
    if 'Sul' in element_name:
        new_CFs.append([cf[0],cf[1]*sul_conversion_coef])
    elif 'Nit' in element_name:
        new_CFs.append([cf[0],cf[1]*nit_conversion_coef])
    elif 'Amm' in element_name:
        new_CFs.append([cf[0],cf[1]*amm_conversion_coef])
new_method_name=('ReCiPe 2016', '1.1 (20180117)', 'Endpoint','Terrestrial Acidification','Ecosystems','Italy','ecowheataly')
ReCiPe_2016_terrestrial_acidification_Italy_epE = bd.Method(new_method_name);
ReCiPe_2016_terrestrial_acidification_Italy_epE.validate(new_CFs);
ReCiPe_2016_terrestrial_acidification_Italy_epE.register(**{'unit':tmp_method_unit});
ReCiPe_2016_terrestrial_acidification_Italy_epE.write(new_CFs);

print()
print("Regionalizing Particulate Matter Formation, Midpoint Egalitarian")

amm_conversion_coef=0.65/0.24
nit_conversion_coef=0.22/0.11
sul_conversion_coef=0.28/0.29
pm25_conversion_coef=2.02/1


tmp_method_name=list(recipe_Em)[3]
tmp_method=bd.Method(tmp_method_name)
tmp_method_unit=tmp_method.metadata['unit']
method_cfs=tmp_method.load()
pm_it_CFs=[]
for cf in method_cfs:
    element_name=bs3.get(cf[0][1])['name']
    if 'Sul' in element_name:
        pm_it_CFs.append([cf[0],round(cf[1]*sul_conversion_coef,2)])
    elif 'Nit' in element_name:
        pm_it_CFs.append([cf[0],round(cf[1]*nit_conversion_coef,2)])
    elif 'Amm' in element_name:
        pm_it_CFs.append([cf[0],round(cf[1]*amm_conversion_coef,2)])

pm25_items=bs3.search('Particulate Matter, < 2.5 um')
pm_lt_25_items=[ite for ite in pm25_items if '10um' not in str(ite)]
for pm in pm_lt_25_items:
    pm_it_CFs.append([(pm_lt_25_items[0]['database'],pm_lt_25_items[0]['code']),pm25_conversion_coef])

new_method_name=tmp_method_name[0:4]+('Humans','Italy','ecowheataly')
ReCiPe_2016_particles_formation_Italy = bd.Method(new_method_name);
ReCiPe_2016_particles_formation_Italy.validate(pm_it_CFs);
ReCiPe_2016_particles_formation_Italy.register(**{'unit':tmp_method_unit})
ReCiPe_2016_particles_formation_Italy.write(pm_it_CFs);


print("Regionalizing Particulate Matter Formation, Endpoint Egalitarian")
#tmp_method_name=('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Human health', 'Particulate Matter Formation', 'Egalitarian')
#Use the just created method
tmp_method_name=new_method_name
tmp_method=bd.Method(tmp_method_name)
tmp_method_unit=tmp_method.metadata['unit']
method_cfs=tmp_method.load()
pm_it_CFs=[]
for cf in method_cfs:
    pm_it_CFs.append([cf[0],cf[1]/10000])
    #pm_it_CFs.append([cf[0],cf[1]/(6.29*10000)])

new_method_name=('ReCiPe 2016', '1.1 (20180117)', 'Endpoint','Particulate Matter Formation','Humans','Italy','ecowheataly')
ReCiPe_2016_particles_formation_Italy_epE = bd.Method(new_method_name);
ReCiPe_2016_particles_formation_Italy_epE.validate(pm_it_CFs);
ReCiPe_2016_particles_formation_Italy_epE.register(**{'unit':tmp_method_unit})
ReCiPe_2016_particles_formation_Italy_epE.write(pm_it_CFs);



print()
print("Regionalizing Ozone Formation, Damage to Humans Midpoint")

nit_conversion_coef=1.13/1
nmvoc_conversion_coef=0.57/0.18

tmp_method_name=list(recipe_NP)[3]
tmp_method=bd.Method(tmp_method_name)
tmp_method_unit=tmp_method.metadata['unit']
method_cfs=tmp_method.load()
ofdh_it_CFs=[]
for cf in method_cfs:
    element_name=bs3.get(cf[0][1])['name']
    if 'Nit' in element_name:
        ofdh_it_CFs.append([cf[0],cf[1]*nit_conversion_coef])
    else:
        ofdh_it_CFs.append([cf[0],cf[1]*nmvoc_conversion_coef])

new_method_name=tmp_method_name[0:len(tmp_method_name)-1]+('Humans','Italy','ecowheataly')
ReCiPe_2016_ozone_formation_damage_to_humans_Italy = bd.Method(new_method_name);
ReCiPe_2016_ozone_formation_damage_to_humans_Italy.validate(ofdh_it_CFs);
ReCiPe_2016_ozone_formation_damage_to_humans_Italy.register(**{'unit':tmp_method_unit});
ReCiPe_2016_ozone_formation_damage_to_humans_Italy.write(ofdh_it_CFs);


print("Regionalizing Ozone Formation, Damage to Humans Endpoint Egalitarian")
tmp_method_name=('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Human health', 'Ozone Formation', 'Damage to Humans', 'Egalitarian')
tmp_method=bd.Method(tmp_method_name)
tmp_method_unit=tmp_method.metadata['unit']
method_cfs=tmp_method.load()
ofdh_it_CFs=[]
for cf in method_cfs:
    element_name=bs3.get(cf[0][1])['name']
    if 'Nit' in element_name:
        ofdh_it_CFs.append([cf[0],cf[1]*nit_conversion_coef])
    else:
        ofdh_it_CFs.append([cf[0],cf[1]*nmvoc_conversion_coef])

new_method_name=('ReCiPe 2016', '1.1 (20180117)', 'Endpoint','Ozone Formation','Humans','Italy','ecowheataly')
ReCiPe_2016_ozone_formation_damage_to_humans_Italy_epE = bd.Method(new_method_name);
ReCiPe_2016_ozone_formation_damage_to_humans_Italy_epE.validate(ofdh_it_CFs);
ReCiPe_2016_ozone_formation_damage_to_humans_Italy_epE.register(**{'unit':tmp_method_unit});
ReCiPe_2016_ozone_formation_damage_to_humans_Italy_epE.write(ofdh_it_CFs);


print()
print("Regionalizing Ozone Formation, Damage to Ecosystem Midpoint")

nit_conversion_coef=2.6/1
nmvoc_conversion_coef=1.41/0.29

tmp_method_name=list(recipe_NP)[4]
tmp_method=bd.Method(tmp_method_name)
tmp_method_unit=tmp_method.metadata['unit']
method_cfs=tmp_method.load()
ofde_it_CFs=[]
for cf in method_cfs:
    element_name=bs3.get(cf[0][1])['name']
    if 'Nit' in element_name:
        ofde_it_CFs.append([cf[0],cf[1]*nit_conversion_coef])
    else:
        ofde_it_CFs.append([cf[0],cf[1]*nmvoc_conversion_coef])

new_method_name=tmp_method_name[0:len(tmp_method_name)-1]+('Ecosystems','Italy','ecowheataly')
ReCiPe_2016_ozone_formation_damage_to_ecosystem_Italy = bd.Method(new_method_name);
ReCiPe_2016_ozone_formation_damage_to_ecosystem_Italy.validate(ofde_it_CFs);
ReCiPe_2016_ozone_formation_damage_to_ecosystem_Italy.register(**{'unit':tmp_method_unit});
ReCiPe_2016_ozone_formation_damage_to_ecosystem_Italy.write(ofde_it_CFs);

print("Regionalizing Ozone Formation, Damage to Ecosystem Endpoint Egalitarian")


tmp_method_name=('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Terrestrial ecosystems', 'Ozone Formation', 'Damage to Ecosystems', 'Egalitarian')
tmp_method=bd.Method(tmp_method_name)
tmp_method_unit=tmp_method.metadata['unit']
method_cfs=tmp_method.load()
ofde_it_CFs=[]
for cf in method_cfs:
    element_name=bs3.get(cf[0][1])['name']
    if 'Nit' in element_name:
        ofde_it_CFs.append([cf[0],cf[1]*nit_conversion_coef])
    else:
        ofde_it_CFs.append([cf[0],cf[1]*nmvoc_conversion_coef])

new_method_name=('ReCiPe 2016', '1.1 (20180117)', 'Endpoint','Ozone Formation','Ecosystems','Italy','ecowheataly')
ReCiPe_2016_ozone_formation_damage_to_ecosystem_Italy_epE = bd.Method(new_method_name);
ReCiPe_2016_ozone_formation_damage_to_ecosystem_Italy_epE.validate(ofde_it_CFs);
ReCiPe_2016_ozone_formation_damage_to_ecosystem_Italy_epE.register(**{'unit':tmp_method_unit});
ReCiPe_2016_ozone_formation_damage_to_ecosystem_Italy_epE.write(ofde_it_CFs);




print()
print("Regionalizing Freshwater Eutrophication Midpoint")

phosphorus_conversion_coef=0.46
#we could compute conversion coefficients for water and for soil, however the will give the same result (0.46).
#in fact the coef for water is 0,46/1 and the one for soil is 0.046/0.1
phosphate_conversion_coef=0.15/0.33
#the previous comment applies even in this case

tmp_method_name=list(recipe_NP)[6]
tmp_method=bd.Method(tmp_method_name)
tmp_method_unit=tmp_method.metadata['unit']
method_cfs=tmp_method.load()

eutr_it_CFs=[]
for cf in method_cfs:
    element_name=bs3.get(cf[0][1])['name']
    if 'Phospho' in element_name:
        eutr_it_CFs.append([cf[0],cf[1]*phosphorus_conversion_coef])
    else:
        eutr_it_CFs.append([cf[0],cf[1]*phosphate_conversion_coef])

new_method_name=tmp_method_name+('Ecosystems','Italy','ecowheataly')
ReCiPe_2016_freshwater_eutrophication_Italy = bd.Method(new_method_name);
ReCiPe_2016_freshwater_eutrophication_Italy.validate(eutr_it_CFs);
ReCiPe_2016_freshwater_eutrophication_Italy.register(**{'unit':tmp_method_unit});
ReCiPe_2016_freshwater_eutrophication_Italy.write(eutr_it_CFs);

print("Regionalizing Freshwater Eutrophication Endpoint Egalitarian")
print()

tmp_method_name=('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Freshwater ecosystems', 'Freshwater Eutrophication', 'Egalitarian')
tmp_method=bd.Method(tmp_method_name)
tmp_method_unit=tmp_method.metadata['unit']
method_cfs=tmp_method.load()

eutr_it_CFs=[]
for cf in method_cfs:
    element_name=bs3.get(cf[0][1])['name']
    if 'Phospho' in element_name:
        eutr_it_CFs.append([cf[0],cf[1]*phosphorus_conversion_coef])
    else:
        eutr_it_CFs.append([cf[0],cf[1]*phosphate_conversion_coef])

new_method_name=('ReCiPe 2016', '1.1 (20180117)', 'Endpoint','Freshwater Eutrophication','Ecosystems','Italy','ecowheataly')
ReCiPe_2016_freshwater_eutrophication_Italy_epE = bd.Method(new_method_name);
ReCiPe_2016_freshwater_eutrophication_Italy_epE.validate(eutr_it_CFs);
ReCiPe_2016_freshwater_eutrophication_Italy_epE.register(**{'unit':tmp_method_unit});
ReCiPe_2016_freshwater_eutrophication_Italy_epE.write(eutr_it_CFs);

#bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Global Warming', '1000 year timescale', 'Egalitarian')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Global Warming 1000 year timescale', 'Humans and Ecosystems','Global','ecowheataly'))
print('Copying global warming 100years Midpoint')
bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Global Warming', '100 year timescale', 'Hierarchist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Global Warming 100 year timescale', 'Humans and Ecoystems','Global','ecowheataly'))
#bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Global Warming', '20 year timescale', 'Individualist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Global Warming 20 year timescale', 'Humans and Ecosystems','Global','ecowheataly'))

print('Copying Toxicity Humans carcinogenic Midpoint')
bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Carcinogenic', 'Hierarchist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Humans - Carcinogenic','Global','ecowheataly'))
print('Copying Toxicity Humans non-carcinogenic Midpoint')
bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Non-carcinogenic', 'Hierarchist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Humans - Non-carcinogenic','Global','ecowheataly'))
print('Copying Toxicity Terrestrial Midpoint')
bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Ecotoxicity', 'Terrestrial', 'Hierarchist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Ecosystems - Terrestrial','Global','ecowheataly'))
print('Copying Toxicity Freshwater Midpoint')
bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Ecotoxicity', 'Freshwater', 'Hierarchist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Toxicity', 'Ecosystems - Freshwater','Global','ecowheataly'))

#bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Ecotoxicity', 'Marine', 'Hierarchist').copy(('ReCiPe 2016', '1.1 (20180117)', 'Midpoint', 'Ecoxicity - Marine', 'Damage to Ecosystems','Global','ecowheataly'))

print('Copying global warming 100years Endpoint')
bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Human health', 'Global Warming', '100 year timescale', 'Hierarchist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Global Warming 100 year timescale', 'Humans and Ecoystems','Global','ecowheataly'))
print('Copying Toxicity Humans carcinogenic Endpoint')
bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Human health', 'Toxicity', 'Carcinogenic', 'Hierarchist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Toxicity', 'Humans - Carcinogenic','Global','ecowheataly'))
print('Copying Toxicity Humans non-carcinogenic Endpoint')
bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Human health', 'Toxicity', 'Non-carcinogenic', 'Hierarchist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Toxicity', 'Humans - Non-carcinogenic','Global','ecowheataly'))
print('Copying Toxicity Terrestrial Endpoint')
bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Terrestrial ecosystems', 'Ecotoxicity', 'Terrestrial', 'Hierarchist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Toxicity', 'Ecosystems - Terrestrial','Global','ecowheataly'))
print('Copying Toxicity Freshwater Endpoint')
bd.Method(('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Freshwater ecosystems', 'Ecotoxicity', 'Freshwater', 'Hierarchist')).copy(('ReCiPe 2016', '1.1 (20180117)', 'Endpoint', 'Toxicity', 'Ecosystems - Freshwater','Global','ecowheataly'))

