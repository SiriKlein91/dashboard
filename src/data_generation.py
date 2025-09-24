import pandas as pd
import numpy as np
import random
from pathlib import Path

def generate_customers(n=1000, seed=42):
    np.random.seed(seed)
    random.seed(seed)

    # Geschlecht
    geschlechter = np.random.choice(
        ["m", "w", "d"],
        size=n,
        p=[0.65, 0.25, 0.10]
    )

    # Alter
    altersgruppen = [
        (14, 19, 0.05),
        (20, 25, 0.20),
        (26, 30, 0.27),
        (31, 35, 0.20),
        (36, 65, 0.28)
    ]

    alter = []
    for low, high, prob in altersgruppen:
        count = int(n * prob)
        ages = np.random.randint(low, high + 1, count)
        alter.extend(ages)

    while len(alter) < n:
        alter.append(np.random.randint(36, 66))
    alter = np.array(alter)
    np.random.shuffle(alter)

    # PLZ
    berlin_plz = [10115, 10243, 10437, 10585, 10785, 10997, 12043, 12435, 13353]
    anhalter_umkreis = [10963, 10961, 10965]
    ausland_plz = ["FR-75001", "US-10001", "ES-08001", "IT-00184", "JP-100-0001"]

    berlin_count = int(n * 0.70)
    ausland_count = n - berlin_count

    anhalter_count = int(berlin_count * 0.35)
    andere_berlin_count = berlin_count - anhalter_count

    plz = []
    plz.extend(np.random.choice(anhalter_umkreis, anhalter_count))
    plz.extend(np.random.choice(berlin_plz, andere_berlin_count))
    plz.extend(np.random.choice(ausland_plz, ausland_count))
    random.shuffle(plz)

    # DataFrame
    df = pd.DataFrame({
        "Alter": alter,
        "Geschlecht": geschlechter,
        "PLZ": plz
    })

    return df

def save_customers(df, path="data/customers.csv"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"Mock-Daten gespeichert unter {path}")

if __name__ == "__main__":
    df = generate_customers(n=1000)
    save_customers(df)

