import pandas as pd
import plotly.express as px

DATA_PATH = "data/customers.csv"

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