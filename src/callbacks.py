from dash import html, dcc, Input, Output
from dash.dependencies import ALL
import json
from src.classes.plot_service import PlotService

#Glabale Button Variable
_last_button = None




def register_callbacks(app, plots: PlotService):
       
    @app.callback(
        Output("berlin-graph", "clickData"),
        Output("age-distribution", "figure"),
        Output("admission-distribution", "figure"),
        Output("world-graph", "figure"),
        Output("germany-graph", "figure"),
        Output("world-distribution", "figure"),
        Output("germany-distribution", "figure"),
        Input("berlin-graph", "clickData"),
        Input("berlin-graph", "selectedData"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date")
    )
    def update_plots(clickData, selectedData, start_date, end_date):
        # Standard: keine PLZ ausgewählt → gesamte Stadt
        plz_list = None

        # Box- oder Lasso-Select hat Vorrang
        if selectedData:
            plz_list = [point["hovertext"] for point in selectedData["points"]]
        elif clickData:
            plz_list = [clickData["points"][0]["hovertext"]]
        # Plots erzeugen
        berlin_map = plots.density_plot(start=start_date, end=end_date)
        hist = plots.age_histogram(start=start_date, end=end_date, plz_list=plz_list)
        admission = plots.sunburst_plot(["admission", "admission_detail"], start=start_date, end=end_date, plz_list=plz_list)
        world_map = plots.map_plot(["continent", "country", "city"], start=start_date, end=end_date)
        germany_map = plots.germany_map_plot(["country", "city"], start=start_date, end=end_date)
        world_dist = plots.sunburst_plot(["continent", "country"], start=start_date, end=end_date)
        germany_dist = plots.sunburst_plot(["country", "city"], start=start_date, end=end_date, country_list=["Deutschland"], limit=1)

        return berlin_map, hist, admission, world_map, germany_map,world_dist, germany_dist 

    



