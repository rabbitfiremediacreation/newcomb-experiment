"""
Newcomb-Experiment: Vergleichstabelle
Newcomb experiment: comparison table

Rechnet automatisch alle Kombinationen aus Trefferquote p und Spielzahl durch
und vergleicht Theorie (Formel) mit Simulation. Speichert die Tabelle zusaetzlich
als CSV-Datei, die sich direkt in Excel oeffnen laesst.

Automatically runs all combinations of hit rate p and number of games and compares
theory (formula) with simulation. Also saves the table as a CSV file for Excel.

Benoetigt newcomb_experiment.py im selben Ordner. / Needs newcomb_experiment.py in the same folder.

Starten / Run:
  python3 newcomb_vergleich.py                       (fragt die Sprache / asks for the language)
  python3 newcomb_vergleich.py --lang en
  python3 newcomb_vergleich.py --wiederholungen 20   (jede Kombination 20-mal, Mittelwerte)
  python3 newcomb_vergleich.py --repetitions 20 --lang en
  python3 newcomb_vergleich.py --seed 42             (reproduzierbare Ergebnisse / reproducible results)
  python3 newcomb_vergleich.py --datei meine.csv     (anderer Dateiname / other file name)
"""

import argparse
import csv
import random
import sys

import newcomb_experiment as ne
from newcomb_experiment import erwartungswert, euro, spiele_einmal, zahl

P_WERTE = [0.5, 0.6, 0.7]
SPIEL_ZAHLEN = [10, 100, 1000]
STRATEGIEN = ("1-Box", "2-Box")

TEXTS = {
    "de": {
        "description": "Vergleichstabelle Theorie gegen Simulation",
        "title": "Newcomb-Experiment: Theorie gegen Simulation",
        "params": "p = {p}, Spiele pro Strategie = {n}, Wiederholungen = {r}\n",
        "h_p": "p",
        "h_games": "Spiele",
        "h_strategy": "Strategie",
        "h_theory": "Theorie (Ø)",
        "h_sim": "Simulation (Ø)",
        "h_dev": "Abweichung",
        "h_pct": "in %",
        "h_msim": "Ø Simulation",
        "h_mdev": "Ø |Abw.| in %",
        "h_low": "kleinster",
        "h_high": "groesster",
        "foot1": "\n'Ø |Abw.| in %' = durchschnittliche Abweichung eines einzelnen Laufs von der Theorie.",
        "foot2": "'kleinster' und 'groesster' zeigen, wie stark die Einzelläufe streuen.",
        "saved": "\nTabelle gespeichert in: {f} (in Excel oeffnen)",
        "tendency": "Tendenziell wird die Abweichung mit mehr Spielen kleiner, einzelne Ausreisser sind aber normal.",
        "csv": ["p", "Spiele", "Wiederholungen", "Strategie", "Theorie", "Simulation (Mittelwert)",
                "Abweichung", "Abweichung %", "Mittlere Abweichung % (Betrag)", "Kleinster Lauf", "Groesster Lauf"],
        "err_rep": "--wiederholungen muss zwischen 1 und 100 liegen",
        "help_seed": "Startwert fuer reproduzierbare Zufallszahlen / seed for reproducible random numbers",
        "help_file": "Name der CSV-Datei / name of the CSV file",
        "help_rep": "Wie oft jede Kombination wiederholt wird (1 bis 100) / repetitions per combination",
        "help_lang": "Sprache / language: de oder/or en",
    },
    "en": {
        "description": "Comparison table: theory versus simulation",
        "title": "Newcomb experiment: theory versus simulation",
        "params": "p = {p}, games per strategy = {n}, repetitions = {r}\n",
        "h_p": "p",
        "h_games": "Games",
        "h_strategy": "Strategy",
        "h_theory": "Theory (avg.)",
        "h_sim": "Simulation (avg.)",
        "h_dev": "Deviation",
        "h_pct": "in %",
        "h_msim": "Avg. simulation",
        "h_mdev": "Avg |dev.| in %",
        "h_low": "lowest",
        "h_high": "highest",
        "foot1": "\n'Avg |dev.| in %' = average deviation of a single run from the theory.",
        "foot2": "'lowest' and 'highest' show how much the individual runs vary.",
        "saved": "\nTable saved to: {f} (open in Excel)",
        "tendency": "The deviation tends to shrink with more games, but individual outliers are normal.",
        "csv": ["p", "Games", "Repetitions", "Strategy", "Theory", "Simulation (mean)",
                "Deviation", "Deviation %", "Mean deviation % (absolute)", "Lowest run", "Highest run"],
        "err_rep": "--repetitions must be between 1 and 100",
        "help_seed": "seed for reproducible random numbers / Startwert fuer Zufallszahlen",
        "help_file": "name of the CSV file / Name der CSV-Datei",
        "help_rep": "repetitions per combination (1 to 100) / Wiederholungen pro Kombination",
        "help_lang": "language / Sprache: de or/oder en",
    },
}

LANG = "de"


def set_lang(lang: str) -> None:
    global LANG
    LANG = "en" if lang == "en" else "de"
    ne.set_lang(LANG)  # Beträge und Zahlenformat im Hauptskript mitumstellen


def t(key: str, **kwargs):
    text = TEXTS[LANG][key]
    return text.format(**kwargs) if isinstance(text, str) else text


def simuliere(strategie: str, p: float, n: int) -> float:
    """Durchschnittsgewinn ueber n Spiele."""
    return sum(spiele_einmal(strategie, p)["gewinn"] for _ in range(n)) / n


def berechne_zeilen(wiederholungen: int) -> list:
    zeilen = []
    for p in P_WERTE:
        for n in SPIEL_ZAHLEN:
            for strategie in STRATEGIEN:
                theorie = erwartungswert(strategie, p)
                laeufe = [simuliere(strategie, p, n) for _ in range(wiederholungen)]
                mittel = sum(laeufe) / wiederholungen
                abw_prozent = [(x - theorie) / theorie * 100 for x in laeufe]
                zeilen.append(
                    {
                        "p": p,
                        "spiele": n,
                        "strategie": strategie,
                        "theorie": theorie,
                        "simulation": mittel,
                        "abweichung": mittel - theorie,
                        "abweichung_prozent": (mittel - theorie) / theorie * 100,
                        # nur bei mehreren Wiederholungen aussagekraeftig / only meaningful with several repetitions:
                        "mittlere_abweichung_prozent": sum(abs(x) for x in abw_prozent) / wiederholungen,
                        "minimum": min(laeufe),
                        "maximum": max(laeufe),
                    }
                )
    return zeilen


def zeige_tabelle(zeilen: list, wiederholungen: int) -> None:
    mehrfach = wiederholungen > 1
    # Spalten: (Überschrift, Mindestbreite, linksbündig?)
    if mehrfach:
        spalten = [
            (t("h_p"), 4, False), (t("h_games"), 6, False), (t("h_strategy"), 9, True),
            (t("h_theory"), 14, False), (t("h_msim"), 14, False), (t("h_mdev"), 13, False),
            (t("h_low"), 14, False), (t("h_high"), 14, False),
        ]
    else:
        spalten = [
            (t("h_p"), 4, False), (t("h_games"), 6, False), (t("h_strategy"), 9, True),
            (t("h_theory"), 14, False), (t("h_sim"), 14, False), (t("h_dev"), 12, False),
            (t("h_pct"), 7, False),
        ]
    breiten = [max(b, len(h)) for h, b, _ in spalten]

    def zeile(zellen: list) -> str:
        teile = []
        for zelle, breite, (_, _, links) in zip(zellen, breiten, spalten):
            teile.append(f"{zelle:<{breite}}" if links else f"{zelle:>{breite}}")
        return " | ".join(teile)

    kopf = zeile([h for h, _, _ in spalten])
    print(kopf)
    print("-" * len(kopf))
    letzte_gruppe = None
    for z in zeilen:
        gruppe = (z["p"], z["spiele"])
        if letzte_gruppe is not None and gruppe[0] != letzte_gruppe[0]:
            print("=" * len(kopf))
        elif letzte_gruppe is not None and gruppe != letzte_gruppe:
            print("-" * len(kopf))
        letzte_gruppe = gruppe
        basis = [str(z["p"]), str(z["spiele"]), z["strategie"], euro(z["theorie"]), euro(z["simulation"])]
        if mehrfach:
            mittlere = zahl(z["mittlere_abweichung_prozent"], 1) + "%"
            print(zeile(basis + [mittlere, euro(z["minimum"]), euro(z["maximum"])]))
        else:
            abw = zahl(z["abweichung"], 0, True)
            prozent = zahl(z["abweichung_prozent"], 1, True) + "%"
            print(zeile(basis + [abw, prozent]))


def speichere_csv(zeilen: list, dateiname: str, wiederholungen: int) -> None:
    """CSV fuer Excel. Deutsch: Semikolon und Komma. English: comma and decimal point."""
    trenner = ";" if LANG == "de" else ","

    def num(x: float) -> str:
        text = f"{x:.2f}"
        return text.replace(".", ",") if LANG == "de" else text

    with open(dateiname, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=trenner)
        w.writerow(t("csv"))
        for z in zeilen:
            w.writerow(
                [
                    num(z["p"]),
                    z["spiele"],
                    wiederholungen,
                    z["strategie"],
                    num(z["theorie"]),
                    num(z["simulation"]),
                    num(z["abweichung"]),
                    num(z["abweichung_prozent"]),
                    num(z["mittlere_abweichung_prozent"]),
                    num(z["minimum"]),
                    num(z["maximum"]),
                ]
            )


def frage_sprache() -> str:
    """Fragt die Sprache ab, aber nur in einem normalen Terminal (nicht bei umgeleiteter Eingabe)."""
    if not sys.stdin.isatty():
        return "de"
    try:
        eingabe = input("Sprache / Language (de/en) [de]: ").strip().lower()
    except EOFError:  # Eingabe beendet (Strg+D): Standardsprache / input closed: default language
        return "de"
    return "en" if eingabe.startswith("e") else "de"


def main() -> None:
    set_lang("de")
    parser = argparse.ArgumentParser(description="Vergleichstabelle / comparison table")
    parser.add_argument("--seed", type=int, help=t("help_seed"))
    parser.add_argument("--datei", "--file", default="newcomb_vergleich.csv", help=t("help_file"))
    parser.add_argument("--wiederholungen", "--repetitions", type=int, default=1, help=t("help_rep"))
    parser.add_argument("--lang", choices=["de", "en"], help=t("help_lang"))
    args = parser.parse_args()

    set_lang(args.lang or frage_sprache())

    if not (1 <= args.wiederholungen <= 100):
        parser.error(t("err_rep"))

    if args.seed is not None:
        random.seed(args.seed)

    print(t("title"))
    print(t("params", p=P_WERTE, n=SPIEL_ZAHLEN, r=args.wiederholungen))

    zeilen = berechne_zeilen(args.wiederholungen)
    zeige_tabelle(zeilen, args.wiederholungen)
    speichere_csv(zeilen, args.datei, args.wiederholungen)

    if args.wiederholungen > 1:
        print(t("foot1"))
        print(t("foot2"))
    print(t("saved", f=args.datei))
    print(t("tendency"))


if __name__ == "__main__":
    main()
