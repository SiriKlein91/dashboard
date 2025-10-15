from dash import html, dcc, Input, Output
from dash.dependencies import ALL
import json
from src.classes.plot_service import PlotService
from globals import FRAGEN

#Glabale Button Variable
_last_button = None




def register_callbacks(app, plots: PlotService):
    import dash


    @app.callback(
        Output("graph-output", "children"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    )
    def display_graph(start_date, end_date):
        global _last_button
        ctx = dash.callback_context
        triggered_id_str = ctx.triggered[0]["prop_id"].split(".")[0]



        return html.Div([
            # Erste Zeile
            html.Div([
                dcc.Graph(id="density-graph", figure=plots.density_plot(start=start_date, end=end_date)),
                dcc.Graph(id="age-distribution", figure=plots.age_histogram(start=start_date, end=end_date))
            ], className="row-container"),

            # Zweite Zeile
            html.Div([
                dcc.Graph(id="country-distribution", figure=plots.map_plot(["continent", "country", "city"], start=start_date, end=end_date)),
                dcc.Graph(id="country-sunburst", figure=plots.sunburst_plot(["continent", "country"], start=start_date, end=end_date))
            ], className="row-container"),

            # Dritte Zeile
            html.Div([
                dcc.Graph(id="germany-distribution", figure=plots.germany_map_plot(["country", "city"], start=start_date, end=end_date)),
                dcc.Graph(id="germany-sunburst", figure=plots.sunburst_plot(["country", "city"], start=start_date, end=end_date, country_list=["Deutschland"], limit=1))
            ], className="row-container"),

            # Letztes Diagramm (volle Breite)
            html.Div([
                dcc.Graph(id="admission-distribution", figure=plots.sunburst_plot(["admission", "admission_detail"], start=start_date, end=end_date))
            ], className="row-container")
        ])
       


    @app.callback(
        Output("age-distribution", "figure"),
        Output("admission-distribution", "figure"),
        Output("country-distribution", "figure"),
        Input("density-graph", "clickData"),
        Input("density-graph", "selectedData"),
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
        hist = plots.age_histogram(start=start_date, end=end_date, plz_list=plz_list)
        sunburst = plots.sunburst_plot(["admission", "admission_detail"], start=start_date, end=end_date, plz_list=plz_list)
        map = plots.map_plot(["continent", "country", "city"], start=start_date, end=end_date)
        germany_map = plots.germany_map_plot(["country", "city"], start=start_date, end=end_date)

        return hist, sunburst, map

    



