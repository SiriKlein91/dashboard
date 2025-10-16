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



UBAHN_COLORS = {
            "U1": "#A6CE39",  # RAL 6018 Gelbgrün
            "U2": "#D2232A",  # RAL 2002 Blutorange
            "U3": "#00887C",  # RAL 6016 Türkisgrün
            "U4": "#FFD100",  # RAL 1023 Verkehrsgelb
            "U5": "#6E4B3A",  # RAL 8007 Rehbraun
            "U6": "#8B00A1",  # RAL 4005 Blaulila
            "U7": "#0096D6",   # RAL 5012 Lichtblau
            "U8": "#00529F",  # RAL 5010 Enzianblau
            "U9": "#FFB367"   # RAL 2003 Pastellorange
        }

# GeoDaten Berlin
GDF = gpd.read_file(SHAPEFILE_BERLIN_PATH)
GDF['plz'] = GDF['plz'].astype(str)

# Nodes einlesen

# Edges einlesen
with open("data/ubahn_colors_coords.json") as f:
    UBAHN_COLOR_COORDS = json.load(f)

# City-Dictionary
with open(CITY_PATH, "r", encoding="utf-8") as f:
    CITY_DIC = json.load(f)

# Deutschland-Shapefile
with open(SHAPEFILE_GERMANY_PATH, "r", encoding="utf-8") as f:
    DE_STATES = json.load(f)

# Fragen
with open(QUESTION_PATH, "r", encoding="utf-8") as f:
    FRAGEN = json.load(f)


