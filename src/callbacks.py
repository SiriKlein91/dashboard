from dash import html, Input, Output, State
from src.classes.plot_service import PlotService
from globals import UBAHN_COLOR_COORDS
import plotly.graph_objects as go


def register_callbacks(app, plots: PlotService):

    @app.callback(
        Output("berlin-graph", "figure"),
        Input("subway-checklist-id", "value"),
        State("berlin-graph", "figure")
    )

    def update_berlin_map(selected, current_fig):
        
        
        if current_fig:
            fig = go.Figure(current_fig)
            if fig.data:
                fig.data = [trace for trace in fig.data if trace.name not in UBAHN_COLOR_COORDS.keys() or trace.name in (selected or [])]

        else: 
            start_date="2024-01-01"
            end_date="2024-12-31" 
            fig=plots.density_plot(start=start_date, end=end_date)
        
        if selected:
            for ubahn in selected:
                color = UBAHN_COLOR_COORDS[ubahn][0]
                lon = UBAHN_COLOR_COORDS[ubahn][1]
                lat = UBAHN_COLOR_COORDS[ubahn][2]
                fig.add_trace(go.Scattermapbox(
                    lon=lon,
                    lat=lat,
                    mode="lines",
                    line=dict(color=color, width=3),
                    name=ubahn,
                    showlegend=False,
                    hoverinfo="skip"
                ))
        return fig    
      
    @app.callback(
        Output("berlin-graph", "clickData"),
        Output("age-distribution", "figure"),
        Output("admission-distribution", "figure"),
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
        world_dist = plots.sunburst_plot(["continent", "country"], start=start_date, end=end_date)

        return berlin_map, hist, admission, 

    



