import dash
from dash import dcc, html, Input, Output
from dash.dependencies import ALL
import json

# Fragen aus JSON laden
with open("data/questions.json", "r", encoding="utf-8") as f:
    fragen = json.load(f)

def create_layout():
    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.Img(src="/assets/urban_apes_logo.png"),
                html.H1("PITCH DASHBOARD - FRAGESTELLUNGEN"),
            ], className="header-left"),
            html.Div([
                html.Span(children=[
                    "von ", html.B("Siri Klein"), " - ", html.I("23.09.2025")
                ])
            ], className="header-right")
        ], className="header"),

        # Hauptcontainer mit 2 Spalten
        html.Div([               
            #html.Div([
                dcc.DatePickerRange(
                    id="date-picker",
                    min_date_allowed="2024-01-01",
                    max_date_allowed="2024-12-31",
                    start_date="2024-01-01",
                    end_date="2024-12-31"
                    ),
                html.Div(id="graph-output", className="graph-figure"),
                html.Div(id="ausgabe")  # Platzhalter für den Callback-Output
                #], className="card right-column")

        ], className="main-container"),

        html.Footer("Urban Apes Pitch Dashboard © 2025")
    ])



