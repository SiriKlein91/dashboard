import pandas as pd
import numpy as np
import random
from pathlib import Path
import requests
from io import StringIO
from datetime import datetime, timedelta


CUSTOMER_PATH = "data/customers.csv"
ENTRY_PATH = "data/entry.csv"
PLZ_PATH = "data/plz_coords.csv"
COUNTRY_PATH = "data/countries_and_cities.json"
CONTINENT_PATH = "data/continents.json"

start_date="2024-01-01"
end_date ="2024-12-31"


def download_plz_coords(dest_path=PLZ_PATH):
    """
    Lädt alle deutschen Postleitzahlen mit Koordinaten und Namen
    von OpenDataSoft (georef-germany-postleitzahl).
    Speichert: plz, name, lat, lon
    """
    url = "https://public.opendatasoft.com/explore/dataset/georef-germany-postleitzahl/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true"
    
    resp = requests.get(url)
    resp.raise_for_status()

    # CSV laden mit Semikolon als Separator
    csv_data = StringIO(resp.text)
    df = pd.read_csv(csv_data, sep=";", dtype=str)

    # geo_point_2d in lat/lon splitten
    df[["lat", "lon"]] = df["geo_point_2d"].str.split(",", expand=True).astype(float)

    # Spalten auswählen & umbenennen
    df = df.rename(columns={
        "Postleitzahl / Post code": "plz",
        "PLZ Name (short)": "name"
    })[["plz", "name", "lat", "lon"]]

    # Speichern
    path = Path(dest_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"PLZ-Koordinaten gespeichert unter {path} ({len(df)} Einträge)")

    return df


def generate_customers(n=1000, seed=42, plz_path=PLZ_PATH, country_path = COUNTRY_PATH, continent_path = CONTINENT_PATH):
    import json
    np.random.seed(seed)
    random.seed(seed)

    with open(country_path, encoding="utf-8") as f:
        country_dic = json.load(f)

    with open(continent_path, "r", encoding="utf-8") as f:
        country_to_continent = json.load(f)


    # ----------------------------
    # PLZ-Verteilung wie vorher
    all_plz = pd.read_csv(plz_path, dtype=str)
    berlin_plz = all_plz[all_plz["name"].str.contains("Berlin", na=False)].copy()
    berlin_plz_list = berlin_plz["plz"].tolist()

    weights = pd.Series(1.0, index=berlin_plz_list)
    for plz in ["10963", "10961", "10965"]:  # Anhalter
        if plz in weights:
            weights[plz] += 5
    for plz in ["10967", "10969", "10997", "10999", "10783", "10785", "10787", "10789"]:  # Anhalter Umgebung
        if plz in weights:
            weights[plz] += 3
    for plz in ["10117", "10178", "10785", "10997", "13353", "12247", "12101", "14195","10827", "12109"]:  # S25
        if plz in weights:
            weights[plz] += 2
    for plz in ["12059", "10245", "10999", "12435"]:  # Konkurrenz
        if plz in weights:
            weights[plz] *= 0.5
    probs = weights / weights.sum()

    plz = np.random.choice(berlin_plz_list, size=n, p=probs.values)
    city = np.array(["Berlin"]*n)
    country = np.array(["Deutschland"]*n)
    continent = np.array(["Europe"]*n)
    # ----------------------------
    # Basisattribute
    geschlechter = np.random.choice(["m", "w", "d"], size=n, p=[0.65, 0.25, 0.10])
    alter = np.random.randint(18, 50, n)  # Kurzversion hier

    # Eintrittsarten (angepasste Verteilung)
    eintrittsarten = np.random.choice(
        ["USC", "Abo", "Tageseintritt"],
        size=n,
        p=[4/7, 1/7, 2/7]
    )

    df_customers = pd.DataFrame({
        "customer_id": range(1, n+1),
        "age": alter,
        "gender": geschlechter,
        "plz": plz,
        "city": city,
        "country": country,
        "admission": eintrittsarten,
        "continent": continent
    })
    

    # Wir nehmen 50% mehr Kund*innen (deutsche + ausländische)
    n_foreign = int(n * 0.2)
    
    # Auswahl von Ländern (ohne Deutschland)
    available_countries = [c for c in country_dic.keys() if c not in ["Germany", "Deutschland"]]
    selected_countries = random.choices(available_countries, k=n_foreign)
    
    # Zufällige Städte und PLZ aus den gewählten Ländern
    city_f = []
    plz_f = []
    continent_f = []
    for c in selected_countries:
        city_zip = random.choice(country_dic[c])
        city_f.append(city_zip[0])
        plz_f.append(city_zip[1])
        continent_f.append(country_to_continent[c])
    
    country_f = np.array(selected_countries)
    geschlechter_f = np.random.choice(["m", "w", "d"], size=n_foreign, p=[0.75, 0.20, 0.05])
    alter_f = np.random.randint(18, 60, n_foreign)
    eintrittsarten_f = np.random.choice(["USC", "Abo", "Tageseintritt"], size=n_foreign, p=[1/20, 0, 19/20])
    
    df_customer_foreign = pd.DataFrame({
        "customer_id": range(n+1, n+n_foreign+1),
        "age": alter_f,
        "gender": geschlechter_f,
        "plz": plz_f,
        "city": city_f,
        "country": country_f,
        "admission": eintrittsarten_f,
        "continent": continent_f
    })


    # Wir nehmen 50% mehr Kund*innen (deutsche + ausländische)
    n_domestic = int(n * 0.3)

    selected_countries = random.choices(["Deutschland"], k=n_domestic)
    
    # Zufällige Städte und PLZ aus den gewählten Ländern
    city_d = []
    plz_d = []
    continent_d = np.array(["Europe"]*n_domestic)
    for c in selected_countries:
        city_zip = random.choice(country_dic[c])
        city_d.append(city_zip[0])
        plz_d.append(city_zip[1])
    
    country_d = np.array(selected_countries)
    geschlechter_d = np.random.choice(["m", "w", "d"], size=n_domestic, p=[0.65, 0.30, 0.05])
    alter_d = np.random.randint(18, 60, n_domestic)
    eintrittsarten_d = np.random.choice(["USC", "Abo", "Tageseintritt"], size=n_domestic, p=[0.1, 0.1, 0.8])

    df_customer_domestic = pd.DataFrame({
        "customer_id": range(n+n_foreign+1, n+n_foreign+n_domestic+1),
        "age": alter_d,
        "gender": geschlechter_d,
        "plz": plz_d,
        "city": city_d,
        "country": country_d,
        "admission": eintrittsarten_d,
        "continent": continent_d
    })

    df_customer = pd.concat([df_customers, df_customer_foreign, df_customer_domestic])
    return df_customer

def generate_entries(customers, start=start_date, end=end_date, seed=42):
    np.random.seed(seed)
    random.seed(seed)

    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    # Saisonfaktoren pro Monat (Juli/August niedrig, Winter hoch)
    saison_faktor = {
        1: 2.0, 2: 2.0, 3: 1.2, 4: 1.0, 5: 0.8,
        6: 0.6, 7: 0.5, 8: 0.4,
        9: 0.8, 10: 1.5, 11: 1.8, 12: 2.0
    }

    entries = []
    entry_id = 1

    for day in all_days:
        weekday = day.weekday()  # 0=Mo, 6=So
        month = day.month

        # Basisanzahl Eintritte pro Tag
        base = 50 if weekday < 5 else 80  # WE mehr Leute
        count_today = int(base * saison_faktor[month] * np.random.uniform(0.8, 1.2))

        # Uhrzeitverteilungen
        if weekday < 5:  # Wochentage
            hours = np.concatenate([
                np.random.normal(loc=17.5, scale=2, size=int(count_today*0.6)),  # Rushhour
                np.random.normal(loc=12, scale=2, size=int(count_today*0.2)),   # Mittags
                np.random.normal(loc=20, scale=1, size=int(count_today*0.2))    # Abend
            ])
        else:  # Wochenende
            hours = np.concatenate([
                np.random.normal(loc=12, scale=2, size=int(count_today*0.5)),   # Peak Mittag
                np.random.normal(loc=17, scale=2, size=int(count_today*0.3)),   # Nachmittag
                np.random.normal(loc=20, scale=1, size=int(count_today*0.2))    # Abend
            ])

        hours = np.clip(hours, 8 if weekday < 5 else 10, 23 if weekday < 5 else 22)

        for h in hours:
            customer = customers.sample(1).iloc[0]
            time = day + timedelta(hours=float(h))
            entries.append([
                entry_id,
                customer["customer_id"],
                customer["admission"],
                time
            ])
            entry_id += 1

    df_entries = pd.DataFrame(entries, columns=["entry_id", "customer_id", "admission", "time"])
    n = df_entries.shape[0]
    df_entries["admission_detail"] = None

    # 1. Tageseintritt → regulär oder ermäßigt
    mask_tageseintritt = df_entries["admission"] == "Tageseintritt"
    df_entries.loc[mask_tageseintritt, "admission_detail"] = np.random.choice(
        ["Regulär", "Ermäßigt"], 
        size=mask_tageseintritt.sum(), 
        p=[0.7, 0.3]
    )

    # 2. Abo → S, M, L, L-Fremdhalle
    mask_abo = df_entries["admission"] == "Abo"
    df_entries.loc[mask_abo, "admission_detail"] = np.random.choice(
        ["S-Abo", "M-Abo", "L-Abo", "L-Abo Fremdhalle"], 
        size=mask_abo.sum(), 
        p=[0.25, 0.25, 0.35, 0.15]
    )
    mask_random = np.random.rand(n) < 0.05
    df_entries.loc[mask_random, "admission"] = "Sonstige"

    mask_sonstige = df_entries["admission"] == "Sonstige"
    df_entries.loc[mask_sonstige, "admission_detail"] = np.random.choice(
        ["Probemonat", "Day Ticket", "Boulderbuddy"], size=mask_sonstige.sum(), p=[0.2, 0.6, 0.2]
    )
    # USC → nur "USC"
    mask_usc = df_entries["admission"] == "USC"
    df_entries.loc[mask_usc, "admission_detail"] = "USC"
    return df_entries


def save_customers(df, path=CUSTOMER_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"Mock-Daten gespeichert unter {path} ({len(df)} Kunden)")


import requests
import zipfile
import io
from pathlib import Path

def download_berlin_plz_shapefile(target_dir="../data/berlin"):
    """
    Lädt das Shapefile der Berliner Postleitzahlen herunter, entpackt es
    und speichert es unter dem angegebenen Verzeichnis.

    Args:
        target_dir (str or Path): Pfad, unter dem die Daten gespeichert werden.
                                  Standard: 'data/berlin'

    Returns:
        Path: Pfad zum Verzeichnis, in dem das Shapefile gespeichert ist.
    """
    # Zielverzeichnis erstellen
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    # URL des Shapefiles
    url = "https://tsb-opendata.s3.eu-central-1.amazonaws.com/plz/plz.shp.zip"

    print(f"Lade Shapefile von {url} herunter...")
    response = requests.get(url)
    response.raise_for_status()  # Fehler werfen, falls Download fehlschlägt

    print(f"Entpacke in {target_dir}...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(target_dir)

    print("Download abgeschlossen.")
    return target_dir



if __name__ == "__main__":
    customers = generate_customers(n=10000)
    entries = generate_entries(customers)
    save_customers(customers, path = CUSTOMER_PATH)
    save_customers(entries, path = ENTRY_PATH)

    #Erstellen Postleitzahlliste
    #german_coords = download_plz_coords()
    #print(german_coords.head())


    #shapefile_path = download_berlin_plz_shapefile()
    #print("Shapefile gespeichert unter:", shapefile_path)