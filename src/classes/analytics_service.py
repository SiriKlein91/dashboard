import pandas as pd
from src.classes.customer_data import CustomerDataFrame
from src.classes.entry_data import EntryDataFrame
from globals import GDF, GERMAN_PLZ, CATEGORY_MAP, BERLIN_BEZIRKE
from pandas.api.types import CategoricalDtype
import numpy as np
import warnings


def map_bezirk(name):
    if isinstance(name, str) and name in BERLIN_BEZIRKE:
        return BERLIN_BEZIRKE[name]
    return "andere deutsche stadt"

class AnalyticsService:
    def __init__(self, customers: CustomerDataFrame, entries: EntryDataFrame):
        self.customers = customers.df
        self.entries = entries.df
        # Mergen nach customer_id für Analysen
        self.merged = self.entries.merge(self.customers, on="customer_id", how="left").drop(columns=["admission_y"]).rename(columns={"admission_x": "admission"})
        self.merged = self.merged.merge(GERMAN_PLZ[["plz", "name"]], on="plz", how="left")
        self.merged["bezirke"] = self.merged["name"].apply(map_bezirk)

        self.merged["bezirke"] = self.merged["bezirke"].fillna("deutsche Städte")
        self.merged = self.create_bins()
     

        self.total_count = self.customers.shape[0]

    def __repr__(self):
        # Wenn die Instanz in der Konsole angezeigt wird
        return repr(self.merged)

    def __str__(self):
        # Wenn print() aufgerufen wird
        return str(self.merged)
   

    def filter_data(self, start=None, end=None, plz_list=None, country_list=None, admission_list=None, bezirke_list= None):
        df = self.merged.copy()

        # Start-/Enddatum prüfen
        if start and end and pd.to_datetime(start) > pd.to_datetime(end):
            raise ValueError(f"Startdatum {start} liegt nach Enddatum {end}.")

        # Filter anwenden
        if start:
            df = df[df["time"] >= pd.to_datetime(start)]
        if end:
            df = df[df["time"] <= pd.to_datetime(end)]
        if plz_list:
            missing_plz = set(plz_list) - set(df["plz"].unique())
            if missing_plz:
                warnings.warn(f"PLZ(s) {missing_plz} existieren nicht im Datensatz.")
            df = df[df["plz"].isin(plz_list)]
        if country_list:
            missing_countries = set(country_list) - set(df["country"].unique())
            if missing_countries:
                warnings.warn(f"Länder {missing_countries} existieren nicht im Datensatz.")
            df = df[df["country"].isin(country_list)]
        if admission_list:
            missing_admissions = set(admission_list) - set(df["admission"].unique())
            if missing_admissions:
                warnings.warn(f"Admission-Kategorien {missing_admissions} existieren nicht im Datensatz.")
            df = df[df["admission"].isin(admission_list)]

        if bezirke_list:
            missing_bezirke = set(bezirke_list) - set(df["bezirke"].unique())
            if missing_bezirke:
                warnings.warn(f"Bezirke {missing_bezirke} existieren nicht im Datensatz.")
            df = df[df["bezirke"].isin(bezirke_list)]

        # Warnung, falls nach allen Filtern keine Daten übrig bleiben
        if df.empty:
            warnings.warn("Der gefilterte DataFrame ist leer. Prüfe die Filtereinstellungen.")

        return df



    def create_bins(self, start = None, end = None, plz_list = None, country_list = None, admission_list = None, dist=5):
        df = self.filter_data(start, end, plz_list, country_list, admission_list)

        if df.empty:
            warnings.warn("Filter führt zu leerem DataFrame. Die Alterskategorie-Spalte wird dennoch erzeugt.", UserWarning)

        if "age" not in df.columns or df["age"].isna().all():
            warnings.warn("create_bins: Spalte 'age' fehlt oder enthält nur NaNs.", UserWarning)
            df["age"] = pd.Series([], dtype=CategoricalDtype(categories=CATEGORY_MAP["age"], ordered=False))

        expected_genders = {"m", "w", "d"}
        if "gender" not in df.columns or not set(df["gender"].dropna()).intersection(expected_genders):
            warnings.warn(f"create_bins: 'gender' enthält keine erwarteten Kategorien {expected_genders}.", UserWarning)
            df["gender"] = pd.Series([], dtype=CategoricalDtype(categories=["m","w","d"], ordered=False))

        if "city" not in df.columns or df["city"].isna().all():
            warnings.warn("create_bins: Spalte 'city' fehlt oder alle Werte NaN, 'origin' wird leer sein.", UserWarning)

        # Altersklassen definieren
        bins = np.arange(5, 65, 5).tolist() + [100]
        labels = CATEGORY_MAP["age_category"]

        cat_type = CategoricalDtype(categories=CATEGORY_MAP["age_category"], ordered=True)
        origin_type = CategoricalDtype(categories= CATEGORY_MAP["origin"], ordered=False)
        if not df.empty:
            df["age_category"] = pd.cut(df["age"], bins=bins, labels=labels, right=True)
            df["age_category"] = df["age_category"].astype(cat_type)
            df["origin"] = np.where(df["city"] == "Berlin", "Berlin", "Tourist")
        else:
            df["age_category"] = pd.Series([], dtype=cat_type)
            df["origin"] = pd.Series([], dtype=origin_type)
    
        return(df)

    
    def create_histogram(self, start=None, end=None, plz_list=None, country_list=None, admission_list = None, bezirke_list= None):

        df = self.filter_data(start, end, plz_list, country_list, admission_list, bezirke_list)
        df = df.drop_duplicates("customer_id")
        labels = CATEGORY_MAP["age_category"]
        cat_type = CategoricalDtype(categories=CATEGORY_MAP["age_category"], ordered=True)
        origin_type = CategoricalDtype(categories= CATEGORY_MAP["origin"], ordered=False)
        # Gruppieren nach Altersklasse, Geschlecht und Herkunft
        grouped = (
            df.groupby(["age_category", "gender", "origin"], observed=False)
            .size()
            .reindex(
                pd.MultiIndex.from_product([labels, df["gender"].unique(), ["Berlin", "Tourist"]],
                                        names=["age_category", "gender", "origin"]),
                fill_value=0
            )
            .rename("count")
            .reset_index()
        )
        if self.total_count == 0:
            warnings.warn("Keine Daten für die Berechnung verfügbar. Prozentwerte werden 0.", UserWarning)
            grouped["percent"] = 0.0
            grouped["gender_total_percent"] = 0.0
        else: 
            grouped["percent"] = (grouped["count"] / self.total_count * 100).round(1)
            # Gesamtverteilung nach Geschlecht
            gender_total = grouped.groupby("gender", observed=False)["count"].sum()
            total_sum = gender_total.sum()
            
            grouped["gender_total_percent"] = grouped["gender"].map(
                (gender_total / total_sum * 100).round(1)
            )

        grouped["age_category"] = grouped["age_category"].astype(cat_type)
        gender_share = grouped.groupby("gender", observed=False)["count"].sum().reset_index()
        gender_share["percent"] = (gender_share["count"] / max(gender_share["count"].sum(), 1) * 100).round(1)


        origin_share = grouped.groupby("origin", observed=False)["count"].sum().reset_index()
        total_origin = origin_share["count"].sum()
        origin_share["percent"] = (origin_share["count"] / max(total_origin, 1) * 100).round(1)

        return grouped, gender_share, origin_share

    
    def proportion(self, group_list, start=None, end=None, plz_list=None, country_list=None, admission_list=None, bezirke_list= None):
        df = self.filter_data(start, end, plz_list, country_list, admission_list, bezirke_list)
        if df.empty:
            warnings.warn("Filter führt zu leerem DataFrame. Ergebnis wird leer zurückgegeben.", UserWarning)

        # Prüfen, ob alle Spalten in group_list existieren
        missing_cols = [col for col in group_list if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Die folgenden Spalten existieren nicht im DataFrame: {missing_cols}")

        if not group_list:
            warnings.warn("group_list ist leer. Rückgabe ist ein Gesamt-Count.", UserWarning)
        
        for col in group_list:
            if col in CATEGORY_MAP:
                allowed = CATEGORY_MAP[col]

                if col not in df.columns:
                    df[col] = pd.Series([pd.NA] * len(df), dtype=pd.CategoricalDtype(categories=allowed, ordered=True))
                else:
                    # Falls Spalte nur NaNs enthält oder existiert
                    df[col] = df[col].astype(pd.CategoricalDtype(categories=allowed, ordered=True))
            else:
                if col not in df.columns:
                    df[col] = pd.Series([pd.NA] * len(df), dtype=object)
        result = df.groupby(group_list, observed=False).size().reset_index(name="count")
        return result
    

    def plz_summary(self, start=None, end=None, plz_list = None, country_list = None, admission_list = None, bezirke_list= None):
        df = self.filter_data(start, end, plz_list, country_list, admission_list, bezirke_list)
        return df.groupby("plz").agg(
            count=("entry_id", "size"),
            mean_age=("age", "mean")
        )
    
    def plz_geo_summary(self, start=None, end=None, admission_list=None, bezirke_list=None):
        df = self.filter_data(start=start, end=end, admission_list=admission_list, bezirke_list=bezirke_list)
        
        summary = df.groupby(["plz", "name"]).agg(
            count=("entry_id", "size"),
            mean_age=("age", "mean")
        ).reset_index()

        summary["mean_age_rounded"] = summary["mean_age"].round(1)
        summary["share"] = summary["count"] / self.total_count * 100

        # Sicherstellen, dass PLZ in beiden DataFrames den gleichen Typ haben
        summary["plz"] = summary["plz"].astype(str)
        GDF["plz"] = GDF["plz"].astype(str)

        # Merge für Choropleth
        gdf_merged = GDF.merge(summary, left_on="plz", right_on="plz", how="left")
    

        # NaNs auffüllen, damit die Choropleth funktioniert
        gdf_merged["count"] = gdf_merged["count"].fillna(0)
        gdf_merged["mean_age_rounded"] = gdf_merged["mean_age_rounded"].fillna(0)
        gdf_merged["share"] = gdf_merged["share"].fillna(0)

        gdf_merged = gdf_merged.to_crs(epsg=4326)
        return gdf_merged
    
    def plz_geo_summary_all_plz(self, start=None, end=None, admission_list=None, bezirke_list=None):
        df = self.plz_geo_summary(start=start, end=end, admission_list=admission_list, bezirke_list=bezirke_list)

        # Sicherstellen, dass alle PLZ angezeigt werden
        all_plz = self.plz_geo_summary(start=None, end=None, admission_list=None, bezirke_list= None)
        df = all_plz.merge(df[["count"]], left_index=True, right_index=True, how="left", suffixes=("", "_filtered"))
        df["count_filtered"] = df["count_filtered"].fillna(0)
        return df
    
    
    
    
    
    def create_loyalty_histogram(self, group_col, start=None, end=None, plz_list =None, country_list = None, admission_list=None, bezirke_list= None):
        
        df = self.filter_data(start, end, plz_list, country_list, admission_list, bezirke_list)
        
        #df["bezirke"] = df["name"].str.contains("Berlin", na=False).replace({True: "Berlin", False: None})
        
        
        
        df = df.groupby(["customer_id", group_col], observed = True).agg(count=("entry_id", "size")).reset_index()
        #df= self.number_of_visits(group_col,start =start, end =end, plz_list = plz_list, country_list=country_list, admission_list=admission_list)
        df["count"] = df["count"].astype(int)
        # Häufigkeiten pro Kategorie
        freq = (
            df.groupby([group_col, "count"], observed=True)
              .size()
              .reset_index(name="freq")
              .sort_values(["count"])
        )
    
        categories = freq[group_col].unique()
        return freq, categories
    

    def create_cohort_table(self, start=None, end=None, plz_list = None, admission_list = None):
        df = self.filter_data(start=start, end=end, plz_list=plz_list,  admission_list = admission_list )

        # Erstbesuch pro Kunde
        df["first_visit"] = df.groupby("customer_id")["time"].transform("min")

        # Monat der Kohorte (zB 2024-01)
        df["cohort_month"] = df["first_visit"].dt.to_period("M")

        # Monat der aktuellen Aktivität
        df["visit_month"] = df["time"].dt.to_period("M")

        # Offset in Monaten
        df["month_offset"] = (df["visit_month"] - df["cohort_month"]).apply(lambda x: x.n)

        # Kunden, die in der Kohorte irgendwann wiedergekommen sind
        cohort_counts = (
            df.groupby(["cohort_month", "month_offset"])["customer_id"]
            .nunique()
            .reset_index()
        )

        # Pivot: Zeilen Kohorten, Spalten Offsets
        pivot = cohort_counts.pivot(
            index="cohort_month",
            columns="month_offset",
            values="customer_id"
        ).fillna(0)

        # Größe der Kohorte (Monat 0)
        cohort_sizes = pivot[0]

        # Relative Retention pro Monat
        retention = pivot.div(cohort_sizes, axis=0).round(3)*100

        return retention


