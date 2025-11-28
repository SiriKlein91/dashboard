import pandas as pd

class CustomerDataFrame:
    REQUIRED_COLUMNS = ["customer_id", "admission", "age", "gender", "plz", "city", "country", "continent"]

    def __init__(self, df: pd.DataFrame):
        
        self.df = df.copy()

        # Prüfen, ob alle benötigten Spalten vorhanden sind
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"Fehlende Spalten: {missing_cols}")

        
        self.df["customer_id"] = self.df["customer_id"].astype(int)
        self.df["admission"] = self.df["admission"].astype("category")
        self.df["age"] = self.df["age"].astype(int)
        self.df["gender"] = self.df["gender"].astype("category")
        self.df["plz"] = self.df["plz"].astype(str)
        self.df["city"] = self.df["city"].astype("category")
        self.df["country"] = self.df["country"].astype("category")
        self.df["continent"] = self.df["continent"].astype("category")

    @classmethod
    def from_csv(cls, path: str):
        df = pd.read_csv(path)
        return cls(df)

    def __repr__(self):
        return repr(self.df)

    def __str__(self):
        return str(self.df)