
"""
import third part LCI dataset (USDA and...)
found exchanges having a correspondece in Biosphere (i.e., flux linking)
create and save the linked fluxes in compliance with BrightWay standards

"""
import bw2data as bd
import bw2io as bi
import json
import pandas as pd

# Path to the folder containing the .xml files of EcoSpold01
db_path = "task1_2/scripts/usda_tractors"
db_name = "process_c0508675-d384-7e78-c6cd-e9c951ec8396.xml"

# Import the LCI database
db_lci = bi.importers.ecospold1.SingleOutputEcospold1Importer(db_path, db_name)
DB = db_lci.data[0]

# Display imported data
try:
    print(db_lci.statistics())  # Show the number of processes, exchanges, etc.
except TypeError as e:
    # Clean data before generating statistics
    for activity in db_lci.data:
        for exchange in activity.get("exchanges", []):
            if exchange.get("location") is None:
                exchange["location"] = "GLO"  # Assign a generic location
    print(db_lci.statistics())

# Loop through all activities in the database
for activity in db_lci:
    print(f"\n🔹 Activity: {activity.get('name', 'Unknown')}, Location: {activity.get('location', 'Unknown')}")

print(f'DB successfully imported: contains {len(DB.get("exchanges", []))} exchanges/fluxes')

# Matching exchanges to Biosphere3
cnt = 0
new_exchanges = []
for exchange in db_lci.data[0].get("exchanges", []):
    if exchange.get("type") == "biosphere":
        exchange_categories = exchange.get("categories", [])
        exchange_words = set(" ".join(exchange_categories).lower().split())

        # Find all flows with the same name in biosphere3
        matches = [bs for bs in bd.Database("biosphere3") if exchange["name"].lower() in bs["name"].lower()]

        if matches:
            best_match = None
            highest_overlap = 0

            for match in matches:
                bs_categories = match.get("categories", [])
                bs_words = set(" ".join(bs_categories).lower().split())
                common_elements = len(exchange_words & bs_words)
                overlap_ratio = common_elements / max(len(exchange_words), len(bs_words))

                if overlap_ratio > highest_overlap and overlap_ratio > 0:
                    highest_overlap = overlap_ratio
                    best_match = match

            if best_match:
                print(
                    f"Match found for: {best_match['name']} ({best_match['unit']}, {best_match.get('categories', 'Unknown')})")
                cnt += 1
                new_exchanges.append({
                    "input": ("biosphere3", best_match["code"]),
                    "unit": best_match["unit"],
                    "type": exchange["type"],
                    "amount": exchange["amount"]
                })
        else:
            print(f"❌ No category match found for {exchange['name']}")

# Creating the new database process
new_db_name = 'usda_item'
new_process = {
    (new_db_name, DB["name"]): {
        "name": DB["name"],
        "unit": DB["unit"],
        "exchanges": new_exchanges
    }
}

# Register and write the new database
new_db = bd.Database(new_db_name)
new_db.register()
new_db.write(new_process)

print(f"Data from >> {activity.get('name', 'Unknown')} << imported successfully")

# --------- PART 2 - Processing CSV Data on fertilizers
db_name = "bentrup_item"
if db_name in bd.databases:
    del bd.databases[db_name]

db_path = 'task1_2/scripts/csv_fertilization_process/fert1.csv'
df = pd.read_csv(db_path, delimiter=';')

# Setup variables for fuzzy matching
bs3 = bd.Database('biosphere3')
new_exchanges = []
cnt = 0

for i in range(df.shape[0]):
    exchange_name = str(df.loc[i]['name'])
    print(f"\n🔗 Attempting to link: {exchange_name}")
    exchange_categories = str(df.loc[i]['to_element'])
    exchange_words = set(exchange_categories.lower().split())

    matches = [bs for bs in bs3 if exchange_name.lower() in bs['name'].lower()]

    if matches:
        if len(matches) > 1:
            best_match = None
            highest_overlap = 0

            for match in matches:
                bs_words = set(" ".join(match.get('categories', [])).lower().split())
                common_elements = len(exchange_words & bs_words)
                overlap_ratio = common_elements / max(len(exchange_words), len(bs_words))

                if overlap_ratio > highest_overlap and overlap_ratio > 0:
                    highest_overlap = overlap_ratio
                    best_match = match
        elif len(matches) == 1:
            best_match = matches[0]

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
    else:
        print(f"❌ No category match for {exchange_name}")

print(f"Total matches found: {cnt}")

# Create new database
new_db_name = "bentrup_item"
this_process_name = 'application to N fertilizer use in winter wheat production systems'

new_process = {
    (db_name, this_process_name): {
        'name': this_process_name,
        'unit': 'kilogram',
        'exchanges': new_exchanges
    }
}

# Register and write the new database
new_db = bd.Database(new_db_name)
new_db.register()
new_db.write(new_process)
