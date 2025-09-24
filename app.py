import dash
from src.layout import create_layout
from src import callbacks

app = dash.Dash(__name__)
app.layout = create_layout()

# Callbacks registrieren
callbacks.register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
