import dash
from dash import dcc, html, Input, Output
import json

# Daten aus deinem Dokument
with open("data/questions.json", "r", encoding="utf-8") as f:
    fragen = json.load(f)



# App initialisieren
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Pitch Dashboard – Fragestellungen"),
    html.Label("Kategorie auswählen:"),
    dcc.Dropdown(
        id="kategorie-dropdown",
        options=[{"label": k, "value": k} for k in fragen.keys()],
        value=list(fragen.keys())[0],  # erste Kategorie als Default
        clearable=False
    ),
    html.Hr(),
    html.Div(id="fragen-output")
])

# Callback: zeigt die Fragen zur gewählten Kategorie
@app.callback(
    Output("fragen-output", "children"),
    Input("kategorie-dropdown", "value")
)
def update_output(kategorie):
    return html.Ul([html.Li(f) for f in fragen[kategorie]])

if __name__ == "__main__":
    app.run(debug=True)
