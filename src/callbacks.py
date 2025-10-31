from dash import html, Input, Output, State, ctx, no_update
from src.classes.plot_service import PlotService
from globals import UBAHN_COLOR_COORDS, BOULDERGYMS
import plotly.graph_objects as go

def register_callbacks(app, plots: PlotService):

    @app.callback(
        Output("berlin-graph", "figure"),
        Output("age-distribution", "figure"),
        Output("admission-distribution", "figure"),
        Output("last-admission-click", "data"),
        Input("subway-checklist-id", "value"),
        Input("berlin-graph", "clickData"),
        Input("berlin-graph", "selectedData"),
        Input("berlin-graph", "relayoutData"),
        Input("admission-distribution", "clickData"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        State("berlin-graph", "figure"),
        State("last-admission-click", "data")
    )
    def update_figures(selected_subways, map_click, map_select, relayoutData, admission_click, start_date, end_date, current_fig, last_click):
        triggered = ctx.triggered_id

        # PLZ-Liste von Karte
        plz_list = None

        if map_select and "points" in map_select: 
            plz_list = [point["customdata"][3] for point in map_select["points"] if "customdata" in point and point["customdata"] is not None] 
        elif map_click and "points" in map_click:
            print(map_click["points"][0]["customdata"])
            plz_list = [map_click["points"][0]["customdata"][3]]

        # Reset über Relayout
        if relayoutData and "xaxis.autorange" in relayoutData:
            plz_list = None
            map_click = None
            map_select = None

        triggered = ctx.triggered_id

    # Standard: kein Admission-Filter
        admission_list = None

        if triggered == "admission-distribution" and admission_click:
            clicked_label = admission_click["points"][0]["label"]
            print(clicked_label)
            # Prüfen: doppelt geklickt → Filter zurücksetzen
            if clicked_label not in ["Abo", "Tageseintritt", "USC"]:
                return no_update, no_update, no_update, no_update
            elif last_click == clicked_label:
                admission_list = None
                last_click = None
            else:
                admission_list = [clicked_label]
                last_click = clicked_label

        
        if current_fig:
            berlin_map = go.Figure(current_fig)
            if triggered in ["subway-checklist-id", "date-picker", "admission-distribution"]:
                # nur dann neu filtern / Basistraces entfernen
                trace_names = [t.name for t in berlin_map.data]
                delete_list = list(set(trace_names) - set(selected_subways or []) - set(BOULDERGYMS.keys()))
                berlin_map.data = tuple(t for t in berlin_map.data if not t.name or t.name not in delete_list)
                # ggf. Admission-Filter auf die Choropleth-Daten anwenden
                df = plots.analytics.plz_geo_summary(start=start_date, end=end_date, admission_list=admission_list)
                berlin_map.data[0].z = df["count"]  # Beispiel: nur Count aktualisieren
                berlin_map.data[0].customdata = df[["name", "count", "mean_age_rounded", "share", "plz"]].values
        else:
            # initiale Map
            berlin_map = plots.density_plot(start=start_date, end=end_date)

        # Subway-Traces hinzufügen
        if selected_subways:
            for ubahn in selected_subways:
                color, lon, lat = UBAHN_COLOR_COORDS[ubahn]
                berlin_map.add_trace(go.Scattermapbox(
                    lon=lon,
                    lat=lat,
                    mode="lines",
                    line=dict(color=color, width=5),
                    name=ubahn,
                    showlegend=False,
                    hoverinfo="skip"
                ))

        # Histogramm reagiert auf PLZ- und Admission-Auswahl
        hist = plots.age_histogram(start=start_date, end=end_date, plz_list=plz_list, admission_list=admission_list)

        # Sunburst nur neu laden, wenn nicht selbst geklickt
        admission_fig = plots.sunburst_plot(["admission", "admission_detail"], start=start_date, end=end_date, plz_list=plz_list) \
            if triggered != "admission-distribution" else no_update

        return berlin_map, hist, admission_fig, last_click


