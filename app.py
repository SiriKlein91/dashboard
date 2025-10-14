import dash
from src.layout import create_layout
from src import callbacks
from src.classes.customer_data import CustomerDataFrame
from src.classes.entry_data import EntryDataFrame
from src.classes.analytics_service import AnalyticsService
from src.classes.plot_service import PlotService
import json
import geopandas as gpd


CUSTOMER_PATH = "data/customers.csv"
ENTRY_PATH = "data/entry.csv"
CITY_PATH = "data/city_long.json"
SHAPEFILE_GERMANY_PATH = "data/2_hoch.geo.json"
PLZ_PATH = "data/plz_coords.csv"
SHAPEFILE_BERLIN_PATH = "data/berlin_plz_shapefile/plz.shp"
QUESTION_PATH = "data/questions.json"
#
with open(QUESTION_PATH, "r", encoding="utf-8") as f:
    FRAGEN = json.load(f)

GDF = gpd.read_file(SHAPEFILE_BERLIN_PATH)
GDF = gpd.read_file(SHAPEFILE_BERLIN_PATH)
GDF['plz'] = GDF['plz'].astype(str)

with open(CITY_PATH, "r", encoding="utf-8") as f:
    CITY_DIC = json.load(f)

with open(SHAPEFILE_GERMANY_PATH, "r", encoding="utf-8") as f:
    DE_STATES = json.load(f)

with open(QUESTION_PATH, "r", encoding="utf-8") as f:
    FRAGEN = json.load(f)


customers = CustomerDataFrame.from_csv(CUSTOMER_PATH)
entries = EntryDataFrame.from_csv(ENTRY_PATH)

# Analytics- und Plot-Services erzeugen
analytics = AnalyticsService(customers, entries)
plots = PlotService(analytics)


app = dash.Dash(__name__)
app.layout = create_layout()

# Callbacks registrieren
callbacks.register_callbacks(app, plots)

if __name__ == "__main__":
    app.run(debug=True)
