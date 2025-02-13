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

#If you receive an error about setups.pickle file, please remove the file and execute the script again


"""
load a third party process, adapt it to the Brightway biosphere using natural language processing (thefuzz), pleas install thefuzz if not already done. 
This makes it possible to use Brightway impact assessment methods
"""
#type
#exec(open('setup_register_processes.py').read())
#to the python prompt to execute
#or use your favorite IDE facilities

import bw2data as bd
import bw2io.importers.json_ld as bij


print('===========================================================')
print('===========================================================')
print('IMPORTING THE MACHINERY PROCESS')
print('===========================================================')
print('===========================================================')

new_db_name='usda_item'
if new_db_name in bd.databases:
    del bd.databases[new_db_name]
folder_name='usda_tractors'
imported=bij.JSONLDImporter(folder_name,new_db_name)

bs3=bd.Database('biosphere3')
bs3_codes=[]
for bs3i in bs3:
    bs3_codes.append(bs3i['code'])

process_key=list(imported.data['processes'].keys())[0]

imported_exchanges=imported.data['processes'][process_key]['exchanges']
this_process=imported_exchanges[0]
new_exchanges=[]
print('  matching exchanges to biosphere3 database using code')
for i in range(len(imported_exchanges)):
    tmp_exchange=imported_exchanges[i]
    tmp_code=tmp_exchange['flow']['@id']
    if tmp_code in bs3_codes:
        match_in_bs3=bs3.get(tmp_code)
        new_exchange={'input': ('biosphere3',match_in_bs3['code']),'unit':match_in_bs3['unit'],'type':'biosphere','amount':tmp_exchange['amount']}
        new_exchanges.append(new_exchange)

this_process_name=this_process['flow']['name']
this_process_unit=this_process['unit']['name']
this_process_amount=this_process['amount']
self_exchange={'input': (new_db_name,this_process_name),'unit':this_process_unit,'type':'production','amount':this_process_amount}
new_exchanges.append(self_exchange)

new_process={(new_db_name,this_process_name):{'name':this_process_name,'unit':this_process_unit,'exchanges':new_exchanges}}

print()
print("  writing database process to database")
print()

new_db=bd.Database(new_db_name)
new_db.register()
new_db.write(new_process)

print('===========================================================')
print('===========================================================')
print('IMPORTING THE NITROGEN PROCESS')
print('===========================================================')
print('===========================================================')

import pandas as pd
print('   inporting the csv file')
df = pd.read_csv('csv_fertilization_process/fert1.csv',delimiter=';') 

#setup variables to apply thefuzz package

bs3=bd.Database('biosphere3')
bio_names=[]
bio_categories=[]
bio_combo=[]
bio_combo1=[]
for bitem in bs3:
    bio_names.append(bitem['name'])
    bio_categories.append(str(bitem['categories']))
    bio_combo1.append((bitem['code'],bitem['name']+"~"+str(bitem['categories'])))
    bio_combo.append(bitem['name']+"~"+str(bitem['categories']))

print('   pairing csv descriptions with biosphere3 using string matching')


#use fuzzy

from thefuzz import fuzz
from thefuzz import process
this_proc_names=[]
this_proc_categories=[]
strings_to_match=[]
chosen_by_fuzzy=[]
not_matched=[]
new_exchanges=[]
cnt = 0
for i in range(df.shape[0]):
    this_proc_names.append(str(df.loc[i]['name']))
    print(f" processo: {str(df.loc[i]['name'])}")
    this_proc_categories.append(str(df.loc[i]['to_element']))
    str_to_match=str(df.loc[i]['name'])+"~"+str(df.loc[i]['to_element'])
    strings_to_match.append(str_to_match)
    extracted=process.extractOne(str_to_match,bio_combo,scorer=fuzz.token_sort_ratio)
    chosen_by_fuzzy.append(extracted)
    if extracted[1]>80:
        splitted_extracted=extracted[0].split('~')
        extracted_name=splitted_extracted[0]
        extracted_categories=splitted_extracted[1]
        matches_in_bs3=[bs for bs in bs3 if (bs['name']==extracted_name) and (str(bs['categories'])==str(extracted_categories))]
        match_in_bs3=matches_in_bs3[0]
        quantity=df.loc[i]['N3_144_ha']
        if 'Gas' in df.loc[i]['name']:
            quantity=round(df.loc[i]['N3_144_ha']/0.76,2)
        #new_exchange={'input': ('biosphere3',match_in_bs3['code']),'unit':match_in_bs3['unit'],'type':match_in_bs3['type'],'amount':quantity}
        new_exchange={'input': ('biosphere3',match_in_bs3['code']),'unit':match_in_bs3['unit'],'type':'biosphere','amount':quantity}
        new_exchanges.append(new_exchange)
        print(f' 🎯 matched Biosphere flux: {match_in_bs3}')
        cnt = cnt+1
        #this_proc_item['code']=extracted_code
        #this_proc_item['name']=extracted_name
        #this_proc_item['categories']=extracted_categories
        #this_proc_item['input']=('biosphere3',extracted_code)
        if df.loc[i]['name'] != extracted_name:
            print("     warning: "+df.loc[i]['name']+" REPLACED BY "+extracted_name)
    else:
        not_matched.append(str_to_match+" WITH "+str(extracted))
        print(f'❌ No match found in Biosphere')
print(f'processi aggangiati: {cnt}')
print()
print("   the following poor matches were dropped:")
print()
for nm in not_matched:
    print("     "+nm)

this_process_name='application to N fertilizer use in winter wheat production systems'

db_name="bentrup_item"
if db_name in bd.databases:
    del bd.databases[db_name]

self_exchange={'input': (db_name,this_process_name),'unit':'kilogram','type':'production','amount':144}
new_exchanges.append(self_exchange)

new_process={(db_name,this_process_name):{'name':this_process_name,'unit':'kilogram','exchanges':new_exchanges}}

print()
print("   writing database")
print()

new_db=bd.Database(db_name)
new_db.register()
new_db.write(new_process)


