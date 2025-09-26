import pandas as pd
import numpy as np
import random
from pathlib import Path
import requests
from io import StringIO

def download_plz_coords(dest_path="data/plz_coords.csv"):
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



def generate_customers(n=10000, seed=42, plz_path="data/plz_coords.csv"):
    np.random.seed(seed)
    random.seed(seed)

    # ----------------------------
    # Geschlecht
    geschlechter = np.random.choice(
        ["m", "w", "d"],
        size=n,
        p=[0.65, 0.25, 0.10]
    )

    # ----------------------------
    # Alter
    altersgruppen = [
        (14, 19, 0.05),
        (20, 25, 0.20),
        (26, 30, 0.27),
        (31, 35, 0.20),
        (36, 65, 0.28)
    ]

    alter = []
    for low, high, prob in altersgruppen:
        count = int(n * prob)
        ages = np.random.randint(low, high + 1, count)
        alter.extend(ages)

    while len(alter) < n:
        alter.append(np.random.randint(36, 66))
    alter = np.array(alter)
    np.random.shuffle(alter)

    # ----------------------------
    # Postleitzahlen
    all_plz = pd.read_csv(plz_path, dtype=str)
    berlin_plz = all_plz[all_plz["name"].str.contains("Berlin", na=False)].copy()
    berlin_plz_list = berlin_plz["plz"].tolist()

    # Basisgewicht für jede PLZ = 1
    weights = pd.Series(1.0, index=berlin_plz_list)

    # Hotspot: Anhalter Bahnhof
    anhalter_umkreis = ["10963", "10961", "10965"]
    for plz in anhalter_umkreis:
        if plz in weights:
            weights[plz] += 10  # stark verstärkt

    # S25-Stationen (vereinfachtes Mapping PLZ-Bereiche)
    s25_plz = ["10785", "10997", "13353", "12247", "12101", "14195"]
    for plz in s25_plz:
        if plz in weights:
            weights[plz] += 5

    # Konkurrenz-Hallen mit weniger Vorkommen
    konkurrenz = {
        "Urban Apes Bright Site": "12059",  # Neukölln
        "Urban Apes Fhain": "10245",        # Friedrichshain
        "Boulderklub": "10999",             # Kreuzberg
        "Bouldergarten": "12435"            # Treptow
    }
    for _, plz in konkurrenz.items():
        if plz in weights:
            weights[plz] *= 0.2  # stark reduziert

    # Normalisieren
    probs = weights / weights.sum()

    # Ziehen von n PLZ
    plz = np.random.choice(berlin_plz_list, size=n, p=probs.values)

    # ----------------------------
    # DataFrame
    df = pd.DataFrame({
        "Alter": alter,
        "Geschlecht": geschlechter,
        "PLZ": plz
    })


    return df


def save_customers(df, path="data/customers.csv"):
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
    df = generate_customers(n=10000)
    save_customers(df)

    #Erstellen Postleitzahlliste
    #german_coords = download_plz_coords()
    #print(german_coords.head())


    shapefile_path = download_berlin_plz_shapefile()
    print("Shapefile gespeichert unter:", shapefile_path)