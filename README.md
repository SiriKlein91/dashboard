# UrbanApes Dashboard

Ein interaktives Dashboard zur Analyse von Urban-Daten. Das Projekt kombiniert Datenaufbereitung, Visualisierung und interaktive Darstellung, um Einblicke in städtische Muster zu gewinnen. Ziel ist es, technisches Know-how mit gesellschaftlichem Nutzen zu verbinden.

## Features

- Analyse und Visualisierung von städtischen Daten
- Interaktive Dashboards für verschiedene Nutzergruppen
- Datenfilterung nach PLZ, Bezirken, Herkunft und weiteren Kategorien
- Übersichtliche Darstellung von Alters- und Geschlechtsverteilungen

## Projektstruktur

```
Dashboard/
│
├── assets/           # Bilder, Logos, Icons
├── data/             # Rohdaten oder Beispiel-Datensets
├── notebooks/        # Jupyter Notebooks für Exploration & Analysen
├── src/              # Python-Module für Datenaufbereitung und Dashboard-Logik
├── app.py            # Startpunkt der Anwendung
├── requirements.txt  # Abhängigkeiten
└── README.md
```

## Installation

1. Repository klonen:

```bash
git clone https://github.com/SiriKlein91/dashboard.git
cd dashboard
```

2. Virtuelle Umgebung erstellen und aktivieren:

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

## Nutzung

1. Starte das Dashboard:

```bash
python app.py
```

2. Öffne deinen Browser unter `http://localhost:8050` (falls Dash verwendet wird) oder die angegebene Adresse.

3. Nutze die Filter und Auswahlmöglichkeiten, um die Daten interaktiv zu erkunden.



## Kontakt

Bei Fragen oder Feedback: [Siri Klein](https://github.com/SiriKlein91)

