#Created on October 2023 by Gianfranco Giulioni within the activities of the following research project:
#FINANCING INSTITUTION
    #EU Financing plan: Next Generation EU
    #IT Financing plan: Piano Nazionale di Ripresa e Resilienza (PNRR)
    #Thematic Priority: Missione 4: istruzione e ricerca
    #IT Managing institution: Ministero dell’Universita' e della Ricerca
    #Investment name: Progetti di Ricerca di Significativo Interesse Nazionale (PRIN)
    #Call: Bando 2022
#PROJECT DETAILS
    #Title: Evaluation of Policies for Enhancing Sustainable Wheat Production in Italy
    #Short name: ECOWHEATALY
    #Contract No: 202288L9YN
    #Investment No: Codice Unico Progetto (CUP): D53D23006260006
    #Start date: 28/09/2023
    #Duration: 24 months
    #Website: www.ecowheataly.it
#License: GPL-3 

#type
#exec(open('ecowheataly_lca_with_brightway.py').read())
#to the python prompt to execute
#or use your favorite IDE facilities

print('===========================================================')
print('===========================================================')
print('STARTING LCA')
print('===========================================================')
print('===========================================================')
print()


print('=================== Methods selection ==================')

recipe=[m for m in bd.methods if 'ReCiPe 2016' in str(m) and '20180117' in str(m)]
recipe_ecow_mid=[m for m in recipe if 'ecowheataly' in str(m) and 'Midpoint' in str(m)]
recipe_ecow_end=[m for m in recipe if 'ecowheataly' in str(m) and 'Endpoint' in str(m)]

###################
#import bw2calc as bc

#Inputs for 1 hectar
hours_of_tractor_use=2.5

kg_of_nitrogen=50

Fungicide_harmful=0
Herbicide_caution=0
Herbicide_irritating=0
Herbicide_harmful=0
GrowthRegulator_harmful=0
Insecticide_harmful=0
Insecticide_toxic=0.13    
Molluscicide_irritating=0 


MJ=100/0.2779*hours_of_tractor_use #for a 100kw tractor

print("ECOWHEATALY LCA")
print('Inputs:')
print()
print('hours of tactor use: '+str(hours_of_tractor_use))
print('kg of Nitrogen: '+str(kg_of_nitrogen))
print('Fungicide_harmful: '+str(Fungicide_harmful))
print('Herbicide_caution: '+str(Herbicide_caution))
print('Herbicide_irritating: '+str(Herbicide_irritating))
print('Herbicide_harmful: '+str(Herbicide_harmful))
print('GrowthRegulator_harmful: '+str(GrowthRegulator_harmful))
print('Insecticide_harmful: '+str(Insecticide_harmful))
print('Insecticide_toxic : '+str(Insecticide_toxic))
print('Molluscicide_irritating: '+str(Molluscicide_irritating))


del bd.databases['ecowheataly']
ecowheatalydb = bd.Database("ecowheataly")
ecowheatalydb.register()
wheat_prod=ecowheatalydb.new_activity(code = 'EcoWheataly production', name = "EcoWheataly production", unit = "ha")
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



functional_unit={ecowheatalydb.get('EcoWheataly production'): 1}
#chosen_methods=[('IPCC 2013', 'climate change', 'global warming potential (GWP100)'),('USEtox', 'ecotoxicity', 'total')];
chosen_methods=recipe_ecow_mid

import bw2calc as bc;
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





