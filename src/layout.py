#import dash
from dash import dcc, html
import json
from src.classes.plot_service import PlotService
from globals import UBAHN_COLOR_COORDS

# Fragen aus JSON laden
with open("data/questions.json", "r", encoding="utf-8") as f:
    fragen = json.load(f)

def create_layout(plots: PlotService):
    start_date="2024-01-01"
    end_date="2024-12-31" 
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


        


        html.Div([               
                html.Div([
                    dcc.DatePickerRange(
                    id="date-picker",
                    min_date_allowed="2024-01-01",
                    max_date_allowed="2024-12-31",
                    start_date=start_date,
                    end_date=end_date
                    ),
            # Erste Zeile
                    html.Div([
                        dcc.Graph(id="berlin-graph", figure=plots.density_plot(start=start_date, end=end_date)),
                        html.Div([
                            dcc.Checklist(
                                id="subway-checklist-id",
                                options=[
                                    {"label": html.Div(
                                        [name],
                                        style={"color": color[0], "font-size": 20}
                                    ), "value": name}
                                    for name, color in UBAHN_COLOR_COORDS.items()
                                ],
                                value=[],  # oder z. B. ["U1"]
                                labelStyle={"display": "flex", "align-items": "center"}
                            ),
                        ], className="subway-checklist"), 
                        dcc.Graph(id="age-distribution", figure=plots.age_histogram(start=start_date, end=end_date))
                    ], className="row-container"),


                    html.Div([
                        dcc.Graph(id="admission-distribution", figure=plots.sunburst_plot(["admission", "admission_detail"], start=start_date, end=end_date))
                    ], className="row-container")
                ]),
                html.Div(id="ausgabe")  # Platzhalter für den Callback-Output
                #], className="card right-column")

        ], className="main-container"),

        html.Footer("Urban Apes Pitch Dashboard © 2025")
    ])



