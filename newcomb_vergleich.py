"""
Newcomb-Experiment: Vergleichstabelle

Rechnet automatisch alle Kombinationen aus Trefferquote p und Spielzahl durch
und vergleicht Theorie (Formel) mit Simulation. Speichert die Tabelle zusaetzlich
als CSV-Datei, die sich direkt in Excel oeffnen laesst.

Benoetigt newcomb_experiment.py im selben Ordner.

Starten:
  python3 newcomb_vergleich.py
  python3 newcomb_vergleich.py --wiederholungen 20   (jede Kombination 20-mal, Mittelwerte)
  python3 newcomb_vergleich.py --seed 42          (reproduzierbare Ergebnisse)
  python3 newcomb_vergleich.py --datei meine.csv  (anderer Dateiname)
"""

import argparse
import csv
import random

from newcomb_experiment import erwartungswert, euro, spiele_einmal

P_WERTE = [0.5, 0.6, 0.7]
SPIEL_ZAHLEN = [10, 100, 1000]
STRATEGIEN = ("1-Box", "2-Box")


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
                        # nur bei mehreren Wiederholungen aussagekraeftig:
                        "mittlere_abweichung_prozent": sum(abs(x) for x in abw_prozent) / wiederholungen,
                        "minimum": min(laeufe),
                        "maximum": max(laeufe),
                    }
                )
    return zeilen


def zeige_tabelle(zeilen: list, wiederholungen: int) -> None:
    mehrfach = wiederholungen > 1
    if mehrfach:
        kopf = (
            f"{'p':>4} | {'Spiele':>6} | {'Strategie':<9} | {'Theorie (Ø)':>14} | {'Ø Simulation':>14} | "
            f"{'Ø |Abw.| in %':>13} | {'kleinster':>14} | {'groesster':>14}"
        )
    else:
        kopf = (
            f"{'p':>4} | {'Spiele':>6} | {'Strategie':<9} | {'Theorie (Ø)':>14} | "
            f"{'Simulation (Ø)':>14} | {'Abweichung':>12} | {'in %':>7}"
        )
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
        if mehrfach:
            mittlere = f"{z['mittlere_abweichung_prozent']:.1f}".replace(".", ",")
            print(
                f"{z['p']:>4} | {z['spiele']:>6} | {z['strategie']:<9} | {euro(z['theorie']):>14} | "
                f"{euro(z['simulation']):>14} | {mittlere:>12}% | {euro(z['minimum']):>14} | {euro(z['maximum']):>14}"
            )
        else:
            abw = f"{z['abweichung']:+,.0f}".replace(",", ".")
            prozent = f"{z['abweichung_prozent']:+.1f}".replace(".", ",")
            print(
                f"{z['p']:>4} | {z['spiele']:>6} | {z['strategie']:<9} | {euro(z['theorie']):>14} | "
                f"{euro(z['simulation']):>14} | {abw:>12} | {prozent:>6}%"
            )


def speichere_csv(zeilen: list, dateiname: str, wiederholungen: int) -> None:
    """CSV fuer deutsches Excel: Semikolon als Trenner, Komma als Dezimalzeichen."""

    def zahl(x: float) -> str:
        return f"{x:.2f}".replace(".", ",")

    with open(dateiname, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(
            ["p", "Spiele", "Wiederholungen", "Strategie", "Theorie", "Simulation (Mittelwert)",
             "Abweichung", "Abweichung %", "Mittlere Abweichung % (Betrag)", "Kleinster Lauf", "Groesster Lauf"]
        )
        for z in zeilen:
            w.writerow(
                [
                    zahl(z["p"]),
                    z["spiele"],
                    wiederholungen,
                    z["strategie"],
                    zahl(z["theorie"]),
                    zahl(z["simulation"]),
                    zahl(z["abweichung"]),
                    zahl(z["abweichung_prozent"]),
                    zahl(z["mittlere_abweichung_prozent"]),
                    zahl(z["minimum"]),
                    zahl(z["maximum"]),
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Vergleichstabelle Theorie gegen Simulation")
    parser.add_argument("--seed", type=int, help="Startwert fuer reproduzierbare Zufallszahlen")
    parser.add_argument("--datei", default="newcomb_vergleich.csv", help="Name der CSV-Datei")
    parser.add_argument(
        "--wiederholungen", type=int, default=1, help="Wie oft jede Kombination wiederholt wird (1 bis 100)"
    )
    args = parser.parse_args()

    if not (1 <= args.wiederholungen <= 100):
        parser.error("--wiederholungen muss zwischen 1 und 100 liegen")

    if args.seed is not None:
        random.seed(args.seed)

    print("Newcomb-Experiment: Theorie gegen Simulation")
    print(f"p = {P_WERTE}, Spiele pro Strategie = {SPIEL_ZAHLEN}, Wiederholungen = {args.wiederholungen}\n")

    zeilen = berechne_zeilen(args.wiederholungen)
    zeige_tabelle(zeilen, args.wiederholungen)
    speichere_csv(zeilen, args.datei, args.wiederholungen)

    if args.wiederholungen > 1:
        print("\n'Ø |Abw.| in %' = durchschnittliche Abweichung eines einzelnen Laufs von der Theorie.")
        print("'kleinster' und 'groesster' zeigen, wie stark die Einzelläufe streuen.")
    print(f"\nTabelle gespeichert in: {args.datei} (in Excel oeffnen)")
    print("Tendenziell wird die Abweichung mit mehr Spielen kleiner, einzelne Ausreisser sind aber normal.")


if __name__ == "__main__":
    main()
