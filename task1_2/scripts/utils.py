# several functions
# Building Table 2.1: Pesticides active principles: from RICA to FITOGEST
import pandas as pd
data = {
    "type": [
        "acaricide", "fungicide", "fungicide", "fungicide", "herbicide", "herbicide",
        "herbicide", "growth regulator", "growth regulator", "Insecticide",
        "Insecticide", "Insecticide", "Molluscicide", "Molluscicide"
    ],
    "tox_level": [
        "irritating", "caution", "irritating", "harmful", "caution", "irritating",
        "harmful", "irritating", "harmful", "irritating", "harmful", "toxic",
        "caution", "irritating"
    ],
    "active_ingredient": [
        "potassium salts of fatty acids", "sulfur", "Prothioconazole", "Tebuconazole",
        "Glyphosate", "2,4-D", "MCPA", "Chlormequat chloride", "Trinexapac-ethil",
        "Deltamethrin", "Deltamethrin", "Pirimicarb", "ferric phosphate", "metaldehyde"
    ],
    "product": [
        "flipper", "cosavet df edge", "pecari 300", "ares 430 sc",
        "clean-up", "pimiento 600", "erbitox m pro", "stabilan", "moddus",
        "antal", "antal", "aphox 50", "ferrex", "luma-kl"
    ],
    "quantity": [
        "4-10 l/ha", "3-8 kg/ha", "0.65 l/ha", "0.58 l/ha",
        "1.4-6-12 l/ha", "0.6-1.2 l/ha", "1.6-2 l/ha", "2-3.5 l/ha",
        "0.5 l/ha", "0.3-0.5 l/ha", "0.3-0.5 l/ha", "260 g/ha",
        "6 kg/ha", "7 kg/ha"
    ],
    "concentration": [
        "479.8 g/l", "80%", "300 g/l", "430 g/l",
        "360 g/l", "600 g/l", "500 g/l", "461 g/l",
        "250 g/l", "25 g/l", "25 g/l", "50%",
        "25 g/kg", "50 g/kg"
    ],
    "active_ing_per_ha": [
        "1920-4800 g/ha", "2400-6400 g/ha", "195 g/ha", "250 g/ha",
        "360-4320 g/ha", "360-720 g/ha", "800-1000 g/ha", "922-1613.5 g/ha",
        "125 g/ha", "7.5-12.5 g/ha", "7.5-12.5 g/ha", "130 g/ha",
        "150 g/ha", "350 g/ha"
    ]
}

df = pd.DataFrame(data)

# Dizionario di mappatura dall'input italiano all'output inglese
category_mapping_RICA = {
    "Acaricida": "acaricide",
    "Anticrittogamico": "fungicide",
    "Insetticida": "Insecticide",
    "Molluschicida": "Molluscicide",
    "Nematocida": "Molluscicide",  # Mappato su Molluscicida
    "Rodenticida": "Molluscicide",  # Mappato su Molluscicida
    "Diserbante": "herbicide",
    "Fitoregolatore": "growth regulator"
}

category_mapping = {

    "Fungicide": "fungicide",
    "Insecticide": "Insecticide",
    "Herbicide": "herbicide",
}


# Mappatura delle classi di tossicità
toxicity_mapping = {
    0: "caution",
    1: "very toxic",
    2: "toxic",
    3: "harmful",
    4: "irritating"
}

# Funzione per ottenere la corrispondenza
def get_pesticide_info(category, toxicity,mode='flat'):
    if mode=='rica':
        fitogest_cat = category_mapping_RICA.get(category)
        fitogest_tox = toxicity_mapping_RICA.get(toxicity)
    else:
        fitogest_cat = category_mapping.get(category)
        fitogest_tox = toxicity_mapping.get(toxicity)

    if not fitogest_cat or not fitogest_tox:
        return "Errore: Categoria o livello di tossicità non valido"

    # Filtrare il DataFrame per tipo e tossicità
    correspondece = df[(df["type"] == fitogest_cat) & (df["tox_level"] == fitogest_tox)]
    correspondece.reset_index(drop=True, inplace=True)

    if correspondece.empty:
        return "Nessuna corrispondenza trovata per i criteri dati."


    return  correspondece.to_dict(orient='records')

# Test della funzione con l'input specificato
test_result = get_pesticide_info("Anticrittogamico", 4)

import re
def parse_pesticide_variable(var_name):
    match = re.match(r"(Herbicide|Insecticide|Fungicide)_Qt Tox-(\d)", var_name)
    if match:
        pesticide_type = match.group(1)
        number = int(match.group(2))
        return pesticide_type, number
    else:
        raise ValueError(f"Formato non riconosciuto: {var_name}")

    # Esempio di utilizzo
