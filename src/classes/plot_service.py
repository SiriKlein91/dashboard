from src.classes.analytics_service import AnalyticsService
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from globals import DE_STATES, CITY_DIC, BOULDERGYMS



class PlotService:
    def __init__(self, analytics: AnalyticsService):
        self.analytics = analytics




    def density_plot(self, start=None, end=None, admission_list=None):
        df = self.analytics.plz_geo_summary_all_plz(start=start, end=end, admission_list=admission_list)
        

        fig = px.choropleth_mapbox(
            df,
            geojson=df.geometry,
            locations=df.index,
            color="count_filtered",
            hover_name="name",
            hover_data=["mean_age"],
            mapbox_style="carto-positron",
            zoom=10,
            center={"lat": 52.52, "lon": 13.405},
            opacity=0.6,
            color_continuous_scale=px.colors.sequential.Greys
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "PLZ: %{customdata[3]}</br>"
                "Anzahl Kunden: %{customdata[1]}<br>"
                "Durchschnittsalter: %{customdata[2]}<extra></extra>"
            ),
            customdata=df[["name", "count_filtered", "mean_age_rounded", "plz"]].values
        )

        for gym, coords in BOULDERGYMS.items():
            fig.add_trace(go.Scattermapbox(
                lon=[coords[0]],
                lat=[coords[1]],
                mode="markers",
                name=gym,
                marker=dict(size=20, color="red", symbol="circle"),
                showlegend=False,
                hoverinfo="text",
                text=[gym]
            ))

        fig.update_layout(height=600, width=700, margin={"r":0,"t":0,"l":0,"b":0})
        return fig



    
    def age_histogram(self, start=None, end=None, plz_list=None, country_list=None,  admission_list = None, bezirke_list= None):
    # Farben
        color_map = {
            "Berlin": "#33cc33",
            "Tourist": "#ff3399"
        }
        gender_labels = {"m": "Männlich", "w": "Weiblich", "d": "Divers"}
        gender_order = ["m", "w", "d"]

        # Daten vorbereiten
        df_plot, gender_share, origin_share = self.analytics.create_histogram(start, end, plz_list, country_list, admission_list, bezirke_list)
        df_plot["gender"] = pd.Categorical(df_plot["gender"], categories=gender_order, ordered=True)

        categories = df_plot["age_category"].cat.categories


        gender_text = "<br>".join([f"{row.gender}: {row.percent:.1f} %" for _, row in gender_share.iterrows()])
        origin_text = "<br>".join([f'<span style="color:{color_map[row.origin]};">■</span> {row.origin}: {row.percent:.1f} %'
                                for _, row in origin_share.iterrows()])

        # Plot

        fig = px.bar(
            df_plot,
            x="age_category",
            y="percent",
            color="origin",               # stacked nach Herkunft
            facet_col="gender",           # drei Balken nebeneinander für m/w/d
            category_orders={"age_category": categories, "gender": gender_order},
            color_discrete_map=color_map,
            barmode="stack",
            custom_data=["gender", "origin"]  # für Hovertext
        )

        # Hovertext anpassen
        fig.update_traces(
            hovertemplate=
            "Geschlecht: %{customdata[0]}<br>" +
            "Altersklasse: %{x}<br>" +
            "Anteil an Gesamtkunden: %{y:.1f}%<br>" +
            "Herkunft: %{customdata[1]}"
        )
            
        

        

        fig.update_layout(
            title="Altersverteilung nach Geschlecht und Herkunft",
            xaxis_title="Altersgruppen",
            yaxis_title="Prozent der Gesamtpersonen",
            template="plotly_white",
            showlegend=False,  # Legende ausblenden
            annotations=[
                dict(
                    text=f"<b>Gesamtverteilung Geschlecht:</b><br>{gender_text}<br><b>Gesamtverteilung Herkunft:</b><br>{origin_text}",
                    xref="paper", yref="paper",
                    x=0.98, y=0.95,        # rechts oben
                    xanchor="right", yanchor="top",
                    showarrow=False,
                    bordercolor="gray",
                    borderwidth=1,
                    bgcolor="white",
                    font=dict(size=12),
                    align="left"            # Text weiterhin linksbündig innerhalb des Fensters
                )
            ]
        )
        fig.layout.xaxis.title.text = "Männlich"
        fig.layout.xaxis2.title.text = "Weiblich"
        fig.layout.xaxis3.title.text = "Divers"
        return fig


    
    def sunburst_plot(self,group_list, start=None, end= None, plz_list = None, country_list = None, bezirke_list= None, limit = None):
        df= self.analytics.proportion(group_list, start, end, plz_list, country_list, bezirke_list)
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
    
    def loyalty_histogram(self, group_col, start=None, end=None,
                          plz_list=None, country_list=None, admission_list=None, bezirke_list= None):
        
        
    
        freq, categories = self.analytics.create_loyalty_histogram(group_col, start, end, plz_list, country_list, admission_list)
    
        fig = go.Figure()  
        # Jede Kategorie als eigener Trace
        for cat in categories:
            sub = freq[freq[group_col] == cat]
    
            fig.add_trace(go.Bar(
                x=sub["count"],
                y=sub["freq"],
                name=str(cat),
                hovertemplate=(
                    f"{group_col}: {cat}<br>"
                    "Besuche: %{x}<br>"
                    "Anzahl Kunden: %{y}<extra></extra>"
                )
            ))
    
        fig.update_layout(
            title="Häufigkeitsverteilung der Kundenbesuche",
            xaxis_title="Anzahl der Besuche",
            yaxis_title="Häufigkeit",
            bargroupgap=0.1,
            barmode="stack",
            margin=dict(l=40, r=20, t=60, b=40),
        )
    
        return fig
    
    def cohort_heatmap(self, start=None, end=None, plz_list=None, admission_list=None):
        retention = self.analytics.create_cohort_table(start = start, end= end, plz_list=plz_list, admission_list=admission_list)

        fig = go.Figure(
            data=go.Heatmap(
                z=retention.values,
                x=retention.columns.astype(int),
                y=retention.index.astype(str),
                hovertemplate=(
                    "Kohorte: %{y}" +
                    "<br>Monat: %{x}" +
                    "<br>Kundenbindung: %{z} %" +
                    "<extra></extra>"
                ),
                colorscale="Blues"
            )
        )

        fig.update_layout(
            title="Kundenbindungsrate der Neukunden",
            xaxis_title="Monate seit Erstbesuch",
            yaxis_title="Kohortenmonat"
        )

        return fig
