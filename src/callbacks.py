from dash import html, dcc, Input, Output
from dash.dependencies import ALL
import json

# Plots importieren
from src.plots import kundenverhalten

# Fragen laden
with open("data/questions.json", "r", encoding="utf-8") as f:
    fragen = json.load(f)

def register_callbacks(app):

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
    )
    def display_graph(n_clicks_list):
        import dash
        ctx = dash.callback_context
        if not ctx.triggered:
            return "Bitte wähle eine Frage."

        button_id = eval(ctx.triggered[0]["prop_id"].split(".")[0])
        kategorie = button_id["kategorie"]
        index = int(button_id["index"])
        frage = fragen[kategorie][index]

        # Routing-Logik: Welche Frage → welcher Plot
        if kategorie == "Kundenverhalten und Zielgruppenanalyse":
            return dcc.Graph(figure=kundenverhalten.plot_customer_density_map())
        else:
            return html.Div(f"Noch kein Plot für: {frage}")

        return html.Div(f"Keine Visualisierung für Kategorie: {kategorie}")
