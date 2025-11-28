import pandas as pd

class EntryDataFrame:
    REQUIRED_COLUMNS = ["entry_id", "customer_id", "admission", "time", "admission_detail"]

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"Fehlende Spalten: {missing_cols}")

        # Optional: Datentypen setzen / konvertieren
        self.df["time"] = pd.to_datetime(self.df["time"])
        self.df["entry_id"] = self.df["entry_id"].astype(int)
        self.df["customer_id"] = self.df["customer_id"].astype(int)
        self.df["admission"] = self.df["admission"].astype("category")
        self.df["admission_detail"] = self.df["admission_detail"].astype("category")

    @classmethod
    def from_csv(cls, path: str):
        df = pd.read_csv(path)
        return cls(df)

    def __repr__(self):
        return repr(self.df)

    def __str__(self):
        return str(self.df)