import pytest
import pandas as pd
from src.classes.analytics_service import AnalyticsService
from src.classes.customer_data import CustomerDataFrame
from src.classes.entry_data import EntryDataFrame


@pytest.fixture
def sample_data():
    """Erstellt realistische Testdaten mit echten Kategorien."""
    customers_df = pd.DataFrame({
        "customer_id": [1, 2, 3, 4],
        "admission": ["USC", "Abo", "Tageseintritt", "Sonstige"],
        "age": [25, 35, 45, 55],
        "gender": ["m", "w", "d", "w"],
        "plz": ["10115", "10245", "10317", "10435"],
        "city": ["Berlin", "Berlin", "Hamburg", "Berlin"],
        "country": ["DE", "DE", "DE", "DE"],
        "continent": ["Europe", "Europe", "Europe", "Europe"]
    })

    entries_df = pd.DataFrame({
        "entry_id": [10, 11, 12, 13],
        "customer_id": [1, 2, 3, 4],
        "admission": ["USC", "Abo", "Tageseintritt", "Sonstige"],
        "admission_detail": ["USC", "L-Abo", "Regulär", "Day Pass"],
        "time": pd.to_datetime(["2025-01-01", "2025-02-01", "2025-03-01", "2025-04-01"])
    })

    customers = CustomerDataFrame(customers_df)
    entries = EntryDataFrame(entries_df)
    return AnalyticsService(customers, entries)


def test_merge_correct(sample_data):
    """Testet, ob das Merging von Kunden- und Eintrittsdaten funktioniert."""
    merged = sample_data.merged

    expected_columns = [
        "entry_id", "customer_id", "admission", "admission_detail",
        "time", "age", "gender", "plz", "city", "country", "continent"
    ]
    for col in expected_columns:
        assert col in merged.columns

    assert set(merged["admission"]) == {"USC", "Abo", "Tageseintritt", "Sonstige"}
    assert set(merged["admission_detail"]) == {"USC", "L-Abo", "Regulär", "Day Pass"}

from src.classes.entry_data import EntryDataFrame

def test_entry_dataframe_missing_columns_raises():
    """Wenn Spalten fehlen, sollte ein Fehler geworfen werden."""
    bad_df = pd.DataFrame({"entry_id": [1], "customer_id": [1]})
    with pytest.raises(ValueError, match="Fehlende Spalten"):
        EntryDataFrame(bad_df)


def test_filter_data_no_results(sample_data):
    """Leerer Filter sollte leeres DataFrame zurückgeben."""
    df = sample_data.filter_data(start="2030-01-01", end="2030-12-31")
    assert df.empty

def test_gender_categories_present(sample_data):
    """Alle drei Geschlechter sollen in der Aggregation vorkommen."""
    df_plot, gender_share, origin_share = sample_data.create_bins()
    assert set(gender_share["gender"]) == {"m", "w", "d"}


def test_plz_summary_contains_expected_columns(sample_data):
    result = sample_data.plz_summary()
    assert "count" in result.columns
    assert "mean_age" in result.columns
    assert not result.empty


def test_filter_data_warnings(sample_data):
    analytics = sample_data

    # Startdatum nach Enddatum -> Exception
    with pytest.raises(ValueError):
        analytics.filter_data(start="2024-01-03", end="2024-01-01")

    # Nicht existierende PLZ -> Warning
    with pytest.warns(UserWarning, match="PLZ"):
        analytics.filter_data(plz_list=["99999"])

    # Nicht existierendes Land -> Warning
    with pytest.warns(UserWarning, match="Länder"):
        analytics.filter_data(country_list=["Atlantis"])

    # Nicht existierende Admission -> Warning
    with pytest.warns(UserWarning, match="Admission-Kategorien"):
        analytics.filter_data(admission_list=["Tageseintritt"])

    # Filter, der zu leerem DataFrame führt -> Warning
    with pytest.warns(UserWarning, match="leerer DataFrame"):
        analytics.filter_data(plz_list=["10115"], country_list=["Atlantis"])
