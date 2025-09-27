from src.classes.analytics_service import AnalyticsService
import plotly.express as px


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