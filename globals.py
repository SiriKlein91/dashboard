import json
import geopandas as gpd

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



# GeoDaten Berlin
GDF = gpd.read_file(SHAPEFILE_BERLIN_PATH)
GDF['plz'] = GDF['plz'].astype(str)

# Nodes einlesen

# Edges einlesen
GDF_SUBWAY_EDGES = gpd.read_file("data/berlin_subway.geojson")
GDF_SUBWAY_EDGES = json.loads(GDF_SUBWAY_EDGES.to_json())

# City-Dictionary
with open(CITY_PATH, "r", encoding="utf-8") as f:
    CITY_DIC = json.load(f)

# Deutschland-Shapefile
with open(SHAPEFILE_GERMANY_PATH, "r", encoding="utf-8") as f:
    DE_STATES = json.load(f)

# Fragen
with open(QUESTION_PATH, "r", encoding="utf-8") as f:
    FRAGEN = json.load(f)


