import dash
from src.layout import create_layout
from src import callbacks
from src.classes.customer_data import CustomerDataFrame
from src.classes.entry_data import EntryDataFrame
from src.classes.analytics_service import AnalyticsService
from src.classes.plot_service import PlotService


CUSTOMER_PATH = "data/customers.csv"
ENTRY_PATH = "data/entry.csv"


customers = CustomerDataFrame.from_csv(CUSTOMER_PATH)
entries = EntryDataFrame.from_csv(ENTRY_PATH)

# Analytics- und Plot-Services erzeugen
analytics = AnalyticsService(customers, entries)
plots = PlotService(analytics)

app = dash.Dash(__name__)
app.layout = create_layout()

# Callbacks registrieren
callbacks.register_callbacks(app, plots)

if __name__ == "__main__":
    app.run(debug=True)
