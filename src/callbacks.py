from dash import html, dcc, Input, Output
from dash.dependencies import ALL
import json
from src.classes.plot_service import PlotService


_last_button = None
# Plots importieren

# Fragen laden
with open("data/questions.json", "r", encoding="utf-8") as f:
    fragen = json.load(f)

def register_callbacks(app, plots: PlotService):

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

        #button_id = eval(ctx.triggered[0]["prop_id"].split(".")[0])
        #kategorie = button_id["kategorie"]
        #index = int(button_id["index"])
        #frage = fragen[kategorie][index]
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
            return dcc.Graph(figure=plots.density_plot(start=start_date, end=end_date))
        else:
            return html.Div(f"Noch kein Plot für: {frage}")

        return html.Div(f"Keine Visualisierung für Kategorie: {kategorie}")
