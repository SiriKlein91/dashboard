import pandas as pd
from src.classes.customer_data import CustomerDataFrame
from src.classes.entry_data import EntryDataFrame
from globals import GDF, GERMAN_PLZ

class AnalyticsService:
    def __init__(self, customers: CustomerDataFrame, entries: EntryDataFrame):
        self.customers = customers.df
        self.entries = entries.df
        # Mergen nach customer_id für Analysen
        self.merged = self.entries.merge(self.customers, on="customer_id", how="left").drop(columns=["admission_y"]).rename(columns={"admission_x": "admission"})

    def __repr__(self):
        # Wenn die Instanz in der Konsole angezeigt wird
        return repr(self.merged)

    def __str__(self):
        # Wenn print() aufgerufen wird
        return str(self.merged)

    def filter_data(self, start=None, end=None, plz_list=None, country_list = None):
        df = self.merged
        if start:
            df = df[df["time"] >= pd.to_datetime(start)]
        if end:
            df = df[df["time"] <= pd.to_datetime(end)]
        if plz_list:
            df = df[df["plz"].isin(plz_list)]
        if country_list:
            df = df[df["country"].isin(country_list)]
        return df

    def daily_visits(self, start=None, end=None, plz_list = None, country_list = None):
        df = self.filter_data(start, end, plz_list, country_list)
        return df.groupby(df["time"].dt.date).size()

    def visits_by_category(self, start=None, end=None, plz_list = None, country_list = None):
        df = self.filter_data(start, end, plz_list, country_list)
        return df.groupby(["admission", df["time"].dt.to_period("M")]).size().unstack(fill_value=0)

    def plz_summary(self, start=None, end=None, plz_list = None, country_list = None):
        df = self.filter_data(start, end, plz_list, country_list)
        return df.groupby("plz").agg(
            count=("entry_id", "size"),
            mean_age=("age", "mean")
        )

    
    def create_bins(self, start = None, end = None, plz_list = None, country_list = None, dist=5):
        from pandas.api.types import CategoricalDtype
        import numpy as np
        df=self.filter_data(start, end, plz_list, country_list)
        arr = np.arange (20,60,dist)
        bins = [5,10, 15] + arr.tolist() + [100]
        labels = ["5-10", "11-15", "15-20"]
        for a, b in zip(arr, arr[1:]):
            labels.append(f"{a+1}-{b}")
        labels.append("60+")
        cat_type = CategoricalDtype(categories=labels, ordered=True)
        df["age_category"] = pd.cut(df["age"], bins=bins, labels=labels, right=True)
        df["age_category"] = df["age_category"].astype(cat_type)
    
        return(df)
    
    def proportion(self,group_list, start=None, end=None, plz_list = None, country_list = None):
        df = self.filter_data(start, end, plz_list, country_list)
        df= df.groupby(group_list, observed=False).size().reset_index(name="count")
        return df
    
    def plz_geo_summary(self, start=None, end=None):
        """
        Liefert ein GeoDataFrame mit count, mean_age, PLZ-Koordinaten
        für den gewünschten Zeitraum.
        """
        df = self.filter_data(start, end)
        df = df.merge(GERMAN_PLZ[["plz", "name"]], on="plz", how="left")
        # Aggregation: Kunden/Eintritte pro PLZ
        summary = df.groupby(["plz", "name"]).agg(
            count=("entry_id", "size"),
            mean_age=("age", "mean")
        ).reset_index()
        summary["mean_age_rounded"] = summary["mean_age"].round(1)  # Durchschnittsalter runden
        total_customer = summary["count"].sum()        # Gesamtkunden
        summary["share"] = summary["count"] / total_customer* 100 
    
        # PLZ-Koordinaten und Shapefile joinen
        #df_plz = pd.read_csv(plz_csv)
        
    
        gdf_merged = GDF.merge(summary, left_on="plz", right_on="plz", how="left")
        gdf_merged = gdf_merged.to_crs(epsg=4326)
    
        return gdf_merged
    