from dash import html

def get_content(fragen):
    return html.Div([
        html.H2("Kundenverhalten und Zielgruppenanalyse"),
        html.Ul([html.Li(f) for f in fragen])
    ])