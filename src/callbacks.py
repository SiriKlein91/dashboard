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



def register_callbacks2(app, plots: PlotService):

    # Fragenliste rendern
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

    # Graphen erzeugen
    @app.callback(
        Output("graph-output", "children"),
        Input({"type": "frage-button", "kategorie": ALL, "index": ALL}, "n_clicks"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date")
    )
    def display_graph(n_clicks_list, start_date, end_date):
        import dash
        global _last_button
        ctx = dash.callback_context
        if not ctx.triggered:
            return "Bitte wähle eine Frage."

        triggered_id_str = ctx.triggered[0]["prop_id"].split(".")[0]
        
        
        if triggered_id_str.startswith("{"):
            button_id = json.loads(triggered_id_str)  # jetzt ist es ein Dictionary
            _last_button = button_id

        elif triggered_id_str == "date-picker":
            if not _last_button:
                return "Bitte wähle zuerst eine Frage."
            button_id = _last_button

        else:
            return("Unbekannter Trigger")
        
        kategorie = button_id["kategorie"]
        index = int(button_id["index"])
        frage = fragen[kategorie][index]     


        # Routing-Logik: Welche Frage → welcher Plot
        if kategorie == "Kundenverhalten und Zielgruppenanalyse":
            return dcc.Graph(id="density-graph",figure=plots.density_plot(start=start_date, end=end_date))
        else:
            return html.Div(f"Noch kein Plot für: {frage}")

        return html.Div(f"Keine Visualisierung für Kategorie: {kategorie}")
    
    @app.callback(
    Output("ausgabe", "children"),
    Input("density-graph", "clickData"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date")
    )
    def punkt_geklickt(clickData):
        if clickData is None:
            return "Klick auf einen Punkt, um Details zu sehen."
        return json.dumps(clickData, indent=2, ensure_ascii=False)  

