
import bw2data as bd
import bw2io as bi
import json
import pandas as pd
# Percorso della cartella che contiene i file .xml di EcoSpold01
db_path = "task1_2/scripts/usda_tractors"
db_name = "process_c0508675-d384-7e78-c6cd-e9c951ec8396.xml"

# Importiamo il database LCI
# ei_importer = bi.importers..
db_lci = bi.importers.ecospold1.SingleOutputEcospold1Importer(db_path, db_name)
DB = db_lci.data[0]

# Visualizziamo i dati importati
try:
    print(db_lci.statistics())  # Mostra il numero di processi, scambi, ecc.
except TypeError as e:
    # Puliamo i dati prima di generare le statistiche
    for activity in db_lci.data:
        for exchange in activity.get("exchanges", []):
            if exchange.get("location") is None:
                #"GLO" è spesso usato nei database LCI per indicare una localizzazione generica
                exchange["location"] = "GLO"  # Assegniamo una location generica
    #----------------------------------------------------------
    print(db_lci.statistics())

# print(json.dumps(db_lci.data[0], indent=4))  # Visualizza il primo processo

for activity in db_lci:  # Scorriamo tutte le attività nel database
    print(f"\n🔹 Activity: {activity.get('name', 'Unknown')}, Location: {activity.get('location', 'Unknown')}")


# QUI per ispezionarei il la amtrice dei flussi:
# for exchange in DB.get("exchanges", []):
#     print(exchange["name"])
print(f'DB importato correttamente: contiene {len(DB.get("exchanges", []))} exchanges/fluxes')

## # ---------------------------------------------
# Dobbiamo collegare i flussi a Biosphere.
# Dobbiamo confrontare anche la categoria (categories) per evitare di collegare due flussi diversi
# con lo stesso nome. Ad esempio potrei ottenere che
# 'Phenanthrene' (kilogram, None, ('water', 'surface water'))
# 'Phenanthrene' (kilogram, None, ('air',))
# vengano collegati.

# 1️⃣ Per ogni flusso non collegato, troviamo il miglior match in biosphere3.
# 2️⃣ Aggiorniamo il database LCI sostituendo il valore input con il codice corretto di biosphere3.
# 3️⃣ Registriamo e salviamo il database aggiornato in Brightway2.



cnt = 0
new_exchanges = []
for exchange in db_lci.data[0].get("exchanges", []):
    if exchange.get("type") == "biosphere":
        # print(f"\n🔗 Attempting to link: {exchange['name']}")

        # Convertiamo le categorie di exchange in parole chiave
        exchange_categories = exchange.get("categories", [])
        exchange_words = set(" ".join(exchange_categories).lower().split())  # Divide le parole chiave

        # Trova tutti i flussi con lo stesso nome in biosphere3
        matches = [bs for bs in bd.Database("biosphere3") if bs["name"] == exchange["name"]]

        if matches:
            # print(f"✅ Found {len(matches)} matches in biosphere3 for {exchange['name']}")

            best_match = None
            highest_overlap = 0

            for match in matches:
                bs_categories = match.get("categories", [])
                bs_words = set(" ".join(bs_categories).lower().split())  # Divide parole chiave

                # Conta il numero di parole in comune
                common_elements = len(exchange_words & bs_words)
                overlap_ratio = common_elements / max(len(exchange_words), len(bs_words))


                # Scegliamo il match con il punteggio più alto
                if overlap_ratio > highest_overlap and overlap_ratio > 0:  # almeno qualcosa vistro che il nime è azzeccato
                    highest_overlap = overlap_ratio
                    best_match = match

            if best_match:
                print(
                    f"match found for : {best_match['name']} ({best_match['unit']}, {best_match.get('categories', 'Unknown')})")
                # print(
                #     f"🎯 Best match: {best_match['name']} ({best_match['unit']}, {best_match.get('categories', 'Unknown')})")
                cnt += 1
                # print(f' il match è {best_match}')
                # print(f" il flusso target è {exchange['categories']}")

                # SALVARE i flussi per poi RISCRIVERli  IN UN NUOVO DB compatibile con biosphere3
                new_exchanges.append({
                    "input": ("biosphere3", best_match["code"]),  # Assegna il codice corretto
                    "unit": best_match["unit"],  # Usa l'unità del match
                    "type": exchange["type"],
                    "amount": exchange["amount"]
                })
            # else:
                # print(f"⚠️ No category match found for {exchange['name']}!")
                # print(f' il match (in Biosphere3!) è {match}')
                # print(f" il flusso target (BD/dfex) è {exchange['categories']}")

        # else:
        #     print(f"❌ No match found for {exchange['name']}")

# Creiamo il dizionario `new_process`
new_db_name='usda_item'
new_process = {
    (new_db_name, DB["name"]): {
        "name": DB["name"],
        "unit": DB["unit"],
        "exchanges": new_exchanges
    }
}

# Registriamo e scriviamo il nuovo database con il processo aggiornato
new_db = bd.Database(new_db_name)
new_db.register()
new_db.write(new_process)

print(f"Data form  >> {activity.get('name', 'Unknown')} << imported succesfully")
del new_db, new_process
## PART 2 -
db_name="bentrup_item"
if db_name in bd.databases:
    del bd.databases[db_name]

import pandas as pd
db_path = 'task1_2/scripts/csv_fertilization_process/fert1.csv'
df = pd.read_csv(db_path,delimiter=';')

# Setup variables for fuzzy matching
bs3 = bd.Database('biosphere3')
# DB3 = pd.DataFrame(bs3)
# filtered_df = DB3[DB3["name"].str.contains("Phosphorus", case=False, na=False)]

new_exchanges = []
cnt = 0
# [  69  170  541  561  676  883 1998 2112 2429 2510 2662 3023 3147 4323
#  4684]
for i in range(df.shape[0]):
    exchange_name = str(df.loc[i]['name'])
    print(f"\n🔗 Attempting to link: {exchange_name}")
    exchange_categories = str(df.loc[i]['to_element'])
    exchange_words = set(exchange_categories.lower().split())
    # Find matches by name
    # matches = [bs for bs in bs3 if bs['name'] == exchange_name]
    matches = [bs for bs in bs3 if exchange_name.lower() in bs['name'].lower()]

    if matches:

        if len(matches)>1:
            best_match = None
            highest_overlap = 0

            for match in matches:
                bs_words = set(" ".join(match.get('categories', [])).lower().split())
                common_elements = len(exchange_words & bs_words)
                overlap_ratio = common_elements / max(len(exchange_words), len(bs_words))

                if overlap_ratio > highest_overlap and overlap_ratio > 0:
                    highest_overlap = overlap_ratio
                    best_match = match

        elif len(matches)==1:
            best_match=matches[0]

        print(f"🎯 Best match from Biosphere: {best_match}")
        cnt += 1
        quantity = df.loc[i]['N3_144_ha']
        if 'Gas' in exchange_name:
            quantity = round(quantity / 0.76, 2)

        new_exchanges.append({
            "input": ("biosphere3", best_match['code']),
            "unit": best_match['unit'],
            "type": "biosphere",
            "amount": quantity
        })

            # print(f"✅ Match found for: {exchange_name} ({best_match['unit']}, {best_match.get('categories', 'Unknown')})")
    else:
        print(f"❌ No category match for {exchange_name}")


print(f"Total matches found: {cnt}")

# Nome del nuovo database
new_db_name = "bentrup_item"
this_process_name='application to N fertilizer use in winter wheat production systems'

new_process={
    (db_name,this_process_name):{
        'name':this_process_name,
        'unit':'kilogram',
        'exchanges':new_exchanges}}



# Registriamo e scriviamo il nuovo database con il processo aggiornato
new_db = bd.Database(new_db_name)
new_db.register()
new_db.write(new_process)






