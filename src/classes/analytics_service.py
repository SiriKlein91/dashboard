import pandas as pd
from src.classes.customer_data import CustomerDataFrame
from src.classes.entry_data import EntryDataFrame
import geopandas as gpd

PLZ_PATH = "data/plz_coords.csv"
SHAPEFILE_PATH = "data/berlin_plz_shapefile/plz.shp"

class AnalyticsService:
    def __init__(self, customers: CustomerDataFrame, entries: EntryDataFrame):
        self.customers = customers.df
        self.entries = entries.df
        # Mergen nach customer_id für Analysen
        self.merged = self.entries.merge(self.customers, on="customer_id", how="left")

    def filter_by_date(self, start=None, end=None):
        df = self.merged
        if start:
            df = df[df["time"] >= pd.to_datetime(start)]
        if end:
            df = df[df["time"] <= pd.to_datetime(end)]
        return df

    def daily_visits(self, start=None, end=None):
        df = self.filter_by_date(start, end)
        return df.groupby(df["time"].dt.date).size()

    def visits_by_category(self, start=None, end=None):
        df = self.filter_by_date(start, end)
        return df.groupby(["admission", df["time"].dt.to_period("M")]).size().unstack(fill_value=0)

    def plz_summary(self, start=None, end=None):
        df = self.filter_by_date(start, end)
        return df.groupby("plz").agg(
            count=("entry_id", "size"),
            mean_age=("age", "mean")
        )
    
    def plz_geo_summary(self, start=None, end=None, plz_csv=PLZ_PATH, shapefile=SHAPEFILE_PATH):
        """
        Liefert ein GeoDataFrame mit count, mean_age, PLZ-Koordinaten
        für den gewünschten Zeitraum.
        """
        df = self.filter_by_date(start, end)
        # Aggregation: Kunden/Eintritte pro PLZ
        summary = df.groupby("plz").agg(
            count=("entry_id", "size"),
            mean_age=("age", "mean")
        ).reset_index()
    
        # PLZ-Koordinaten und Shapefile joinen
        #df_plz = pd.read_csv(plz_csv)
        gdf = gpd.read_file(shapefile)
        gdf['plz'] = gdf['plz'].astype(int)
    
        gdf_merged = gdf.merge(summary, left_on="plz", right_on="plz", how="left")
        gdf_merged = gdf_merged.to_crs(epsg=4326)
    
        return gdf_merged