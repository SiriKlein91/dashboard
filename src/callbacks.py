
from dash import html, dcc, Input, Output, State, ctx, no_update
from src.classes.plot_service import PlotService
from globals import UBAHN_COLOR_COORDS, BOULDERGYMS
import plotly.graph_objects as go

def register_callbacks(app, plots: PlotService):

    # ---------------------
    # Callback 1: Filter berechnen und in Stores speichern
    # ---------------------
    @app.callback(
        Output("plz-filter-store", "data"),
        Output("selected-points-store", "data"),
        Input("berlin-graph", "clickData"),
        Input("berlin-graph", "selectedData"),
        Input("berlin-graph", "relayoutData"),
        Input("selected-points-store", "data")
    )
    def compute_plz(map_click, map_select, relayoutData, selected_points):
        triggered = ctx.triggered_prop_ids

        

        # --- Hilfsfunktion: sichere PLZ-Extraktion ---
        def extract_plz(point):
            if not point.get("customdata"):
                return None
            for v in reversed(point["customdata"]):
                if isinstance(v, str) and v.strip().isdigit():
                    return v.strip()
            return point.get("location")
        

        if "berlin-graph.relayoutData" in triggered.keys():
            if 'mapbox.center' not in ctx.args_grouping[2]["value"].keys():
                return no_update, no_update
            else:
                return None, None
        
        else:
        # PLZ-Liste
            plz_list = None
            if map_select and "points" in map_select:
                selected_points = [p["pointIndex"] for p in map_select["points"] if extract_plz(p)]

                plz_list = list({extract_plz(p) for p in map_select["points"] if extract_plz(p)})
            elif map_click and "points" in map_click:
                selected_points = map_click["points"][0]["pointIndex"]
                plz = extract_plz(map_click["points"][0])
                plz_list = [plz] if plz else None


        

        return plz_list, selected_points

    @app.callback(
        Output("admission-filter-store", "data"),
        Output("last-admission-click-store", "data"),
        Input("admission-distribution", "clickData"),
        State("last-admission-click-store", "data"),
    )
    def compute_admission(admission_click, last_admission_click):
        triggered = ctx.triggered_id

        admission_list = None
        new_last_admission_click = last_admission_click

        if triggered == "admission-distribution" and admission_click and "points" in admission_click:
            point = admission_click["points"][0]

            label = point.get("label")
            parent = point.get("parent")

            # Nur Parent Ebene soll interaktiv sein
            if not parent:  # parent == "" oder None
                if last_admission_click == label:
                    admission_list = None
                    new_last_admission_click = None
                else:
                    admission_list = [label]
                    new_last_admission_click = label

            else:
                # Child Klicks ignorieren
                return no_update, no_update

        else:
            if last_admission_click:
                admission_list = [last_admission_click]

        return admission_list, new_last_admission_click


    # ---------------------
    # Callback 2: Berlin Map aktualisieren
    # ---------------------
    @app.callback(
        Output("berlin-graph", "figure"),
        Input("admission-filter-store", "data"),
        Input("subway-checklist-id", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("selected-points-store", "data"),
        State("berlin-graph", "figure"),
    )   
    def update_berlin_map(admission_list, selected_subways, start_date, end_date, selected_points, current_fig):

        # -------------------------------
        # 1. Initialisierung: Karte einmal erzeugen
        # -------------------------------
        if current_fig is None:
            fig = plots.density_plot(start=start_date, end=end_date, admission_list=admission_list)

            # Subway Traces setzen
            for ubahn in selected_subways or []:
                color, lon, lat = UBAHN_COLOR_COORDS[ubahn]
                fig.add_trace(go.Scattermapbox(
                    lon=lon, lat=lat, mode="markers+lines",
                    line=dict(width=5, color=color),
                    name=ubahn,
                    showlegend=False,
                    hoverinfo="skip"
                ))

            return fig

        # -------------------------------
        # 2. Figur wiederverwenden
        # -------------------------------
        fig = go.Figure(current_fig)

        # -------------------------------
        # 3. Choropleth Daten aktualisieren (ohne neue Figur zu bauen)
        # -------------------------------
        df = plots.analytics.plz_geo_summary_all_plz(start=start_date, end=end_date, admission_list=admission_list)

      
        # erstes trace ist IMMER das choropleth trace
        choropleth_trace = fig.data[0]

        # z aktualisieren
        choropleth_trace.z = df["count_filtered"]

        # customdata aktualisieren
        choropleth_trace.customdata = df[["name", "count_filtered", "mean_age_rounded", "plz"]].values

        fig.data = tuple([choropleth_trace] + list(fig.data[1:]))

        # -------------------------------
        # 4. Subway Traces neu setzen
        # -------------------------------
        fig.data = tuple([fig.data[0]] + [
            t for t in fig.data[1:]
            if t.name in BOULDERGYMS or t.name in UBAHN_COLOR_COORDS
        ])
        fig.data = tuple([
            t for t in fig.data
            if t.name not in UBAHN_COLOR_COORDS
        ])
        for ubahn in selected_subways or []:
            color, lon, lat = UBAHN_COLOR_COORDS[ubahn]
            fig.add_trace(go.Scattermapbox(
                lon=lon, lat=lat, mode="markers+lines",
                line=dict(width=5, color=color),
                name=ubahn,
                showlegend=False,
                hoverinfo="skip"
            ))
        for t in fig.data[1:]:
            if t.name in BOULDERGYMS or t.name in UBAHN_COLOR_COORDS:
                t.selectedpoints = None
        fig.data[0].selectedpoints = selected_points
        
        return fig


    # ---------------------
    # Callback 3: Histogramm aktualisieren
    # ---------------------
    @app.callback(
        Output("age-distribution", "figure"),
        Input("plz-filter-store", "data"),
        Input("admission-filter-store", "data"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    )
    def update_histogram(plz_list, admission_list, start_date, end_date):
        fig = plots.age_histogram(start=start_date, end=end_date, plz_list=plz_list, admission_list=admission_list)
        return fig

    # ---------------------
    # Callback 4: Sunburst aktualisieren
    # ---------------------
   


    @app.callback(
    Output("admission-distribution", "figure"),
    Input("plz-filter-store", "data"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
    State("admission-distribution", "figure"),
)
    def update_sunburst(plz_list, start_date, end_date, current_fig):


        triggered = ctx.triggered_id
        

        # Wenn der Sunburst selbst geklickt wurde → nicht aktualisieren
        if triggered == "admission-distribution":
            return no_update
        # 1. INITIALER AUFRUF – FIGURE ERZEUGEN
        if current_fig is None:
            fig = plots.sunburst_plot(
                ["admission", "admission_detail"],
                start=start_date,
                end=end_date,
                plz_list=plz_list
            )
            return fig

        # 2. EXISTIERENDE FIG – NUR DATEN AKTUALISIEREN
        fig = go.Figure(current_fig)

        new_fig = plots.sunburst_plot(
            ["admission", "admission_detail"],
            start=start_date,
            end=end_date,
            plz_list=plz_list,
            
        )

        # 3. ERSETZT NUR DEN SUNBURST-TRACE
        # Sunburst ist IMMER der erste Trace
        # 4. Nur den ersten Trace aktualisieren, nicht alle Traces


        if fig.data and new_fig.data:
            #fig.data[0].labels = new_fig.data[0].labels
            #fig.data[0].parents = new_fig.data[0].parents
            fig.data[0].values = new_fig.data[0].values
            fig.data[0].customdata = new_fig.data[0].customdata
            fig.data[0].hovertemplate = new_fig.data[0].hovertemplate

        # 4. LAYOUT ÜBERNEHMEN (Title, Margin, Farben, etc.)
        #fig.update_layout(new_fig.layout)

        return fig
    

    @app.callback(
        Output("loyalty-histogram", "figure"),
        Input("plz-filter-store", "data"),
        Input("admission-filter-store", "data"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("loyalty-store", "data")
    )
    def update_loyalty_histogram(plz_list, admission_list, start_date, end_date, filter):

        
        fig = plots.loyalty_histogram(
            filter,
            start=start_date,
            end=end_date,
            plz_list=plz_list,
            admission_list=admission_list
        )
        return fig
       
    @app.callback(
        Output('loyalty-store', 'data'),
        Input('loyalty-dropdown', 'value')
    )
    def update_output(value):
        return value
    

    
    @app.callback(
        Output("cohort-heatmap", "figure"),
        Input("plz-filter-store", "data"),
        Input("admission-filter-store", "data"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    )
    def update_cohort(plz_list, admission_list, start_date, end_date):
        return plots.cohort_heatmap(start=start_date, end=end_date, plz_list=plz_list, admission_list=admission_list)