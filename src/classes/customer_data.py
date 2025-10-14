import pandas as pd

class CustomerDataFrame:
    REQUIRED_COLUMNS = ["customer_id", "admission", "age", "gender", "plz", "city", "country", "continent"]

    def __init__(self, df: pd.DataFrame):
        # DataFrame kopieren, um Seiteneffekte zu vermeiden
        self.df = df.copy()

        # Prüfen, ob alle benötigten Spalten vorhanden sind
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"Fehlende Spalten: {missing_cols}")

        # Optional: Datentypen setzen / konvertieren
        self.df["customer_id"] = self.df["customer_id"].astype(int)
        self.df["admission"] = self.df["admission"].astype("category")
        self.df["age"] = self.df["age"].astype(int)
        self.df["gender"] = self.df["gender"].astype("category")
        self.df["plz"] = self.df["plz"].astype(int)
        self.df["city"] = self.df["city"].astype("category")
        self.df["country"] = self.df["country"].astype("category")
        self.df["continent"] = self.df["continent"].astype("category")

    @classmethod
    def from_csv(cls, path: str):
        df = pd.read_csv(path)
        return cls(df)

    def __repr__(self):
        # Wenn die Instanz in der Konsole angezeigt wird
        return repr(self.df)

    def __str__(self):
        # Wenn print() aufgerufen wird
        return str(self.df)