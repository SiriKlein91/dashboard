from src.classes.analytics_service import AnalyticsService
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from globals import DE_STATES, CITY_DIC, GDF_SUBWAY_EDGES
import itertools



class PlotService:
    def __init__(self, analytics: AnalyticsService):
        self.analytics = analytics




    def density_plot(self, start=None, end=None):
        
        # PLZ-Daten für Choropleth
        df = self.analytics.plz_geo_summary(start, end)

        # Choropleth-Karte
        fig = px.choropleth_mapbox(
            df,
            geojson=df.geometry,
            locations=df.index,
            color="count",
            hover_name="plz",
            hover_data=["mean_age"],
            mapbox_style="carto-positron",
            zoom=10,
            center={"lat": 52.52, "lon": 13.405},
            opacity=0.6,
            color_continuous_scale="Greys"
        )


        colors = {
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

        for line_name, color in colors.items():
            for feature in GDF_SUBWAY_EDGES["features"]:
                if feature["properties"].get("name") == line_name:
                    coords = feature["geometry"]["coordinates"]
                    fig.add_trace(go.Scattermapbox(
                        lon=[c[0] for c in coords],
                        lat=[c[1] for c in coords],
                        mode="lines",
                        line=dict(color=color, width=3),
                        name=line_name,
                        showlegend=False,  # Optional, damit Linie nur einmal im Legendeneintrag auftaucht
                        hoverinfo="skip" 
                    ))
        fig.update_layout(
            height=600,   # Höhe erhöhen
            width=700,    # Breite etwas schmaler
            margin={"r":0,"t":0,"l":0,"b":0}  # Ränder auf 0, damit Karte maximal Platz nutzt
        )
        return fig




    
    def age_histogram(self, start= None, end= None, plz_list= None, country_list = None, dist= 5):
        df = self.analytics.create_bins(start, end, plz_list, country_list, dist)
        categories = df["age_category"].cat.categories

        # Gruppieren und fehlende Kategorien auffüllen
        df_plot = (
        df.groupby(["age_category", "gender"], observed=False)
        .size()
        .unstack(fill_value=0)                # fehlende gender/category-Kombis = 0
        .reindex(categories, fill_value=0)    # alle Alterskategorien sichtbar
        .stack()
        .rename_axis(index=["age_category", "gender"])
        .reset_index(name="count")
        )
        df_plot["age_category"] = pd.Categorical(
            df_plot["age_category"],
            categories=categories,
            ordered=True
        )
        fig = px.bar(
            df_plot,
            x= "age_category",
            y="count",
            color="gender",
            category_orders={"age_category": df["age_category"].cat.categories},
            color_discrete_sequence=["#33ffdd", "#ff00ff", "#ffee00"]
        )
        fig.update_layout(
            title="Altersverteilung",
            xaxis_title="Altersgruppen",
            yaxis_title="Anzahl Personen",
            template="plotly_white"  # clean look
        )

        return fig
    
    def sunburst_plot(self,group_list, start=None, end= None, plz_list = None, country_list = None, limit = None):
        df= self.analytics.proportion(group_list, start, end, plz_list, country_list)
        total = df["count"].sum()
        df["percent_total"] = df["count"] / total * 100
        
        if limit:
            last_col = group_list[-1]
            df = df[df["count"] > 0]

            df[last_col] = df[last_col].astype(str)
        
            # Kleine Gruppen identifizieren
            small = df["percent_total"] < limit
        
            if small.any():
                # Neue Kategorie "Sonstige" einfügen
                df.loc[small, last_col] = "Sonstige"
                df = (df.groupby(group_list,as_index=False, observed=True).agg({"count": "sum"}))
                total = df["count"].sum()
                df["percent_total"] = df["count"] / total * 100

                
        fig = px.sunburst(
            df,
            path=group_list,
            values='count',
            hover_data=["count", "percent_total"]
        )
        #fig.update_traces(hovertemplate="%{label}<br>Anzahl: %{customdata[0]}<br>Prozent Gesamt: %{customdata[1]:.1f}%")
        fig.update_traces(hovertemplate="%{label}<br>Anzahl: %{value}<br>Prozent Parent: %{percentParent:.1%}<br>Prozent Gesamt: %{percentRoot:.1%}")
        return fig
    
    def map_plot(self, group_list, start = None, end = None, plz_list = None, country_list = None):
        df = self.analytics.proportion(group_list, start, end, plz_list, country_list)
        df["size_log"] = np.log1p(df["count"]) 
        df["country"] = df["country"].astype(str)
        df.loc[df[df.loc[:,"country"]== "Deutschland"].index, "country"] = "Germany"


        fig = px.scatter_geo(
            df,
            locations="country",
            locationmode="country names",
            color="continent",
            hover_name="country",
            size="size_log",
            projection="natural earth",
            title="Kundenverteilung weltweit",
            hover_data={
                "count": True,
                "size_log": False,      # wird nicht angezeigt
                "continent": True
            }
        )
        return fig
    
    def germany_map_plot(self, group_list, start = None, end = None, plz_list = None, country_list = None):
        
        df = self.analytics.proportion(group_list, start, end, plz_list, country_list)
        df= df[df["country"] == "Deutschland"]
        city_coords = pd.DataFrame(CITY_DIC).T.reset_index()
        city_coords.columns = ["city", "lat", "lon"]
        df = df.merge(city_coords, on="city", how="left")
        df["size_log"] = np.log1p(df["count"]) 

        # 1. Bundesländergrenzen zuerst (kein Hover)
        choropleth = go.Choropleth(
        geojson=DE_STATES,
        locations=[s["properties"]["name"] for s in DE_STATES["features"]],
        z=[0] * len(DE_STATES["features"]),
        featureidkey="properties.name",
        showscale=False,
        hoverinfo="none",
        marker_line_color="rgba(80,80,80,0.6)",
        marker_line_width=0.6,
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
        )

        # 2. Städtepunkte mit Hovertext (liegen automatisch oben)
        scatter = go.Scattergeo(
            lat=df["lat"],
            lon=df["lon"],
            text=df["city"] + "<br>Kundeneintritte: " + df["count"].astype(str),
            hoverinfo="text",
            marker=dict(
                size=df["size_log"] * 5,
                color=df["size_log"],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Kundenanzahl"),
                line=dict(width=0.5, color="black")
            )
        )

        # 3. Figur aufbauen
        fig = go.Figure()

        fig.add_trace(choropleth)  # Bundesländer zuerst
        fig.add_trace(scatter)     # Städte danach

        # 4. Karteneinstellungen
        fig.update_geos(
            fitbounds="locations",
            visible=False,
            showcountries=False,
            showframe=False,
            showcoastlines=False,
            projection_scale=8.2,
            center=dict(lat=51.163, lon=10.447)
        )

        fig.update_layout(
            title=dict(text="Kundenverteilung in Deutschland", x=0.5, xanchor="center", font=dict(size=18)),
            margin=dict(r=0, l=0, b=0, t=40),
            geo_bgcolor="rgba(0,0,0,0)"
        )
        return fig