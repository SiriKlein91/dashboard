from src.classes.analytics_service import AnalyticsService
import plotly.express as px
import pandas as pd


class PlotService:
    def __init__(self, analytics: AnalyticsService):
        self.analytics = analytics

    def density_plot(self, start=None, end=None):
        df = self.analytics.plz_geo_summary(start, end)
        fig = px.choropleth_mapbox(
            df,
            geojson=df.geometry,
            locations=df.index,
            color="count",
            hover_name="plz",
            hover_data=["mean_age"],
            mapbox_style="carto-positron",
            zoom=9,
            center={"lat": 52.52, "lon": 13.405},
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig

    def category_trend_plot(self, start=None, end=None):
        df = self.analytics.visits_by_category(start, end)
        fig = px.line(df, labels={"value": "Besuche", "time": "Monat"})
        return fig
    
    def age_histogram(self, start= None, end= None, plz_list= None, dist= 5):
        df = self.analytics.create_bins(start, end, plz_list, dist)
        categories = df["age_category"].cat.categories

        # Gruppieren und fehlende Kategorien auffüllen
        df_plot = (
        df.groupby(["age_category", "gender"])
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