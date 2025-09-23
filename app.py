import dash
from dash import dcc, html, Input, Output
import json

# Fragen aus JSON laden
with open("data/fragen.json", "r", encoding="utf-8") as f:
    fragen = json.load(f)

app = dash.Dash(__name__)

app.layout = html.Div([
    # Header
    html.Div([
        html.Img(src="/assets/urban_apes_logo.png"),
        html.H1("PITCH DASHBOARD - FRAGESTELLUNGEN"),
        html.Span(children=["von ",html.B("Siri Klein"), " - ", html.I("23.09.2025")])
    ], className="header"),

    # Hauptcontainer
    html.Div([
        html.Div([
            html.Label("KATEGORIE:"),
            dcc.Dropdown(
                id="kategorie-dropdown",
                options=[{"label": k, "value": k} for k in fragen.keys()],
                value=list(fragen.keys())[0],
                clearable=False
            )
        ], className="card"),

        html.Div(id="fragen-output", className="card")
    ], className="main-container"),

    # Footer
    html.Footer("Urban Apes Pitch Dashboard © 2025")
])

@app.callback(
    Output("fragen-output", "children"),
    Input("kategorie-dropdown", "value")
)
def update_output(kategorie):
    return html.Div([
        html.H2(kategorie),
        html.Ul([html.Li(f) for f in fragen[kategorie]])
    ])

if __name__ == "__main__":
    app.run(debug=True)
