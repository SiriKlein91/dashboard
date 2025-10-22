from dash import dcc, html
from src.classes.plot_service import PlotService
from globals import UBAHN_COLOR_COORDS


def create_layout(plots: PlotService):
    start_date = "2024-01-01"
    end_date = "2024-12-31" 
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

        # Main Container dreispaltig
        html.Div([
            # Linke Spalte: Datum + Karte + Checkliste
            html.Div([
                dcc.DatePickerRange(
                    id="date-picker",
                    min_date_allowed="2024-01-01",
                    max_date_allowed="2024-12-31",
                    start_date=start_date,
                    end_date=end_date
                ),
                dcc.Graph(id="berlin-graph", figure=plots.density_plot(start=start_date, end=end_date)),
                html.Div([
                    dcc.Checklist(
                        id="subway-checklist-id",
                        options=[
                            {"label": html.Div(
                                [name],
                                style={"color": color[0], "font-size": 16}  # Farbe pro Linie
                            ), "value": name}
                            for name, color in UBAHN_COLOR_COORDS.items()
                        ],
                        value=[],
                        labelStyle={"display": "inline-flex", "align-items": "center", "margin-right": "10px"}
                    )
                ], className="subway-checklist"),
            ], className="column left-column"),

            # Mittlere Spalte: zwei Grafiken
            html.Div([
                dcc.Graph(id="age-distribution", figure=plots.age_histogram(start=start_date, end=end_date)),
                dcc.Graph(id="admission-distribution", figure=plots.sunburst_plot(["admission", "admission_detail"], start=start_date, end=end_date))
            ], className="column middle-column"),

            # Rechte Spalte: Platzhalter
            html.Div([
                html.Div(id="placeholder-1", className="placeholder-card"),
                html.Div(id="placeholder-2", className="placeholder-card")
            ], className="column right-column"),

        ], className="main-container"),

        html.Footer("Urban Apes Pitch Dashboard © 2025")
    ])


