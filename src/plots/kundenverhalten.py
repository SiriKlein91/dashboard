import pandas as pd
import plotly.express as px
import geopandas as gpd

DATA_PATH = "data/customers.csv"
DATA_PATH_PLZ = "data/plz_coords.csv"
DATA_PATH_SHP = "data/berlin_plz_shapefile/plz.shp"


def plot_altersverteilung():
    df = pd.read_csv(DATA_PATH)
    return px.histogram(df, x="Alter", nbins=15, title="Altersverteilung")

def plot_geschlecht():
    df = pd.read_csv(DATA_PATH)
    counts = df["Geschlecht"].value_counts().reset_index()
    counts.columns = ["Geschlecht", "Anzahl"]
    return px.bar(counts, x="Geschlecht", y="Anzahl", title="Geschlechterverteilung")

def plot_herkunft():
    df = pd.read_csv(DATA_PATH)
    top_plz = df["PLZ"].value_counts().reset_index().head(10)
    top_plz.columns = ["PLZ", "Anzahl"]
    return px.bar(top_plz, x="PLZ", y="Anzahl", title="Top 10 PLZ")


def plot_customer_density_map():
    # Choroplethenkarte mit Mapbox
    df = create_summary_stats()
    gdf = prepare_customer_plz_map(df)

    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,  # eindeutiger Index für jedes Feature
        color="count",               # Anzahl der Besucher
        hover_name="name",
        hover_data=["plz","count","mean"],
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        zoom=9,
        center={"lat":52.52, "lon":13.405},
    )
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return(fig)

def create_summary_stats():
    df_customer = pd.read_csv(DATA_PATH)
    gender_counts = df_customer.groupby(["PLZ", "Geschlecht"]).size().unstack(fill_value=0)
    # Altersstatistik pro PLZ
    age_stats = df_customer.groupby("PLZ")["Alter"].agg(['count', 'mean'])
    # Beide Tabellen zusammenführen
    plz_summary = gender_counts.join(age_stats)
    return(plz_summary)


def prepare_customer_plz_map(df_customer):

    df_plz =  pd.read_csv(DATA_PATH_PLZ)
    df_plz_unique = df_plz.drop_duplicates(subset="plz")
    gdf = gpd.read_file(DATA_PATH_SHP)
    gdf['plz'] = gdf['plz'].astype(int)


    df = pd.merge(df_customer, df_plz_unique.loc[:,["name", "plz","lat", "lon"]], left_on="PLZ", right_on="plz", how="left")

    gdf_merged = gdf.merge(df, left_on='plz', right_on='plz', how='left')
    gdf_plot = gdf_merged[gdf_merged['count'].notna()]
    gdf_plot['count'] = gdf_plot['count'].astype(float)
    gdf_plot = gdf_plot.to_crs(epsg=4326)
    return(gdf_plot)