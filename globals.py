import json
import geopandas as gpd
import pandas as pd

# ----------------------
# Pfade zu Dateien
# ----------------------
CUSTOMER_PATH = "data/customers.csv"
ENTRY_PATH = "data/entry.csv"
CITY_PATH = "data/city_long.json"
SHAPEFILE_GERMANY_PATH = "data/2_hoch.geo.json"
PLZ_PATH = "data/plz_coords.csv"
SHAPEFILE_BERLIN_PATH = "data/berlin_plz_shapefile/plz.shp"
QUESTION_PATH = "data/questions.json"
BOULDERGYM_PATH = "data/Bouldergyms.json"
SUBWAY_PATH = "data/ubahn_colors_lan_lat.json"
CATEGORY_PATH = "data/categories.json"
BEZIRKE_PATH = "data/berlin_bezirke.json"


# GeoDaten Berlin
GDF = gpd.read_file(SHAPEFILE_BERLIN_PATH)
GDF['plz'] = GDF['plz'].astype(str)

GERMAN_PLZ = pd.read_csv(PLZ_PATH)
GERMAN_PLZ['plz'] = GERMAN_PLZ['plz'].astype(str)

# Edges einlesen
with open(SUBWAY_PATH) as f:
    UBAHN_COLOR_COORDS = json.load(f)

with open(BEZIRKE_PATH) as f:
    BERLIN_BEZIRKE = json.load(f)

# Edges einlesen
with open(BOULDERGYM_PATH) as f:
    BOULDERGYMS = json.load(f)

# Edges einlesen
with open(CATEGORY_PATH) as f:
    CATEGORY_MAP = json.load(f)


# City-Dictionary
with open(CITY_PATH, "r", encoding="utf-8") as f:
    CITY_DIC = json.load(f)

# Deutschland-Shapefile
with open(SHAPEFILE_GERMANY_PATH, "r", encoding="utf-8") as f:
    DE_STATES = json.load(f)



