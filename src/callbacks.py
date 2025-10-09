from dash import html, dcc, Input, Output
from dash.dependencies import ALL
import json
from src.classes.plot_service import PlotService

#Glabale Button Variable
_last_button = None


# Fragen laden
with open("data/questions.json", "r", encoding="utf-8") as f:
    fragen = json.load(f)


def register_callbacks(app, plots: PlotService):
    import dash

    @app.callback(
        Output("fragen-output", "children"),
        Input("kategorie-dropdown", "value")
    )
    def update_questions(kategorie):
        return html.Div([
            html.H2(kategorie),
            html.Div([
                html.Button(
                    f,
                    id={"type": "frage-button", "kategorie": kategorie, "index": str(i)},
                    n_clicks=0,
                    className="frage-btn"
                )
                for i, f in enumerate(fragen[kategorie])
            ])
        ])

    @app.callback(
        Output("graph-output", "children"),
        Input({"type": "frage-button", "kategorie": ALL, "index": ALL}, "n_clicks"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date")
    )
    def display_graph(n_clicks_list, start_date, end_date):
        global _last_button
        ctx = dash.callback_context
        if not ctx.triggered:
            return "Bitte wähle eine Frage."

        triggered_id_str = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if triggered_id_str.startswith("{"):
            button_id = json.loads(triggered_id_str)
            _last_button = button_id
        elif triggered_id_str == "date-picker":
            if not _last_button:
                return "Bitte wähle zuerst eine Frage."
            button_id = _last_button
        else:
            return "Unbekannter Trigger"

        kategorie = button_id["kategorie"]
        index = int(button_id["index"])
        frage = fragen[kategorie][index]

        # Hier eleganter Routing-Switch
        if kategorie == "Kundenverhalten und Zielgruppenanalyse":
            return html.Div([
                dcc.Graph(id="density-graph", figure=plots.density_plot(start=start_date, end=end_date)),
                dcc.Graph(id="age-distribution", figure=plots.age_histogram(start=start_date, end=end_date)),
                #plots.price_pie(start=start_date, end=end_date)
            ])
        else:
            return html.Div(f"Noch kein Plot für: {frage}")
        
    @app.callback(
        Output("age-distribution", "figure"),
        #Output("preis-pie", "figure"),
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
        #pie = plots.price_pie(df_filtered)

        return hist#, pie

    



