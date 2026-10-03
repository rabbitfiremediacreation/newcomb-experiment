# Newcomb-Experiment

Interaktive Präsentation und Simulation zum Newcomb-Problem (IB Mathematik AI SL).

## Aufbau des Experiments

- **Box A** ist die Mystery-Box. Sie enthält 1.000.000 €, wenn der Prädiktor "1-Box" getippt hat, sonst ist sie leer.
- **Box B** ist offen und enthält immer 1.000 €.
- **1-Box:** nur Box A nehmen. **2-Box:** Box A und Box B nehmen.
- Der Prädiktor tippt vorher und liegt mit Wahrscheinlichkeit **p** richtig.

Erwartungswerte:

```
E(1-Box) = 1.000.000 · p + 0 · (1 − p)
E(2-Box) = 1.000 + 1.000.000 · (1 − p)
```

Ab p > 0,5005 ist 1-Box im Erwartungswert besser.

## Präsentation mit Live-Experiment

Braucht Node.js und Internet (GSAP wird per CDN geladen).

```bash
npm run dev
```

Öffnet die HyperFrames-Präsentation (Standard: http://localhost:3004). Folie 8 enthält das Experiment mit einarmigem Banditen, Diagramm und Auswertung. Die Seite lässt sich auch direkt öffnen: `/composition/experiment.html`.

## Python-Skripte

Brauchen nur Python 3.

```bash
python3 newcomb_experiment.py                       # fragt Spielzahl (10-1000) und p ab
python3 newcomb_experiment.py --spiele 500 --p 0.7  # ohne Nachfragen
python3 newcomb_vergleich.py --wiederholungen 20    # Vergleichstabelle, schreibt eine CSV für Excel
```

Mit `--seed 42` sind die Zufallszahlen reproduzierbar.

## Dateien

| Datei | Inhalt |
|---|---|
| `index.html` | Präsentation (HyperFrames-Slideshow) |
| `experiment.html` | Live-Experiment, auf Folie 8 eingebettet |
| `newcomb_experiment.py` | Simulation mit einstellbarer Spielzahl und p |
| `newcomb_vergleich.py` | Vergleichstabelle für mehrere p-Werte und Spielzahlen |

## Lizenz

MIT, siehe [LICENSE](LICENSE).
