"""
Newcomb-Experiment: Simulation mit einstellbarer Spielzahl und Trefferquote p

Aufbau:
  - Box B (offen) enthaelt immer 1.000 EUR.
  - Box A (Mystery-Box, verdeckt) enthaelt 1.000.000 EUR, wenn der Praediktor "1-Box" getippt hat,
    sonst ist sie leer.
  - Der Praediktor tippt VOR deiner Wahl und liegt mit Wahrscheinlichkeit p richtig.

Strategien:
  - 1-Box: nur Box A nehmen (die Mystery-Box)
  - 2-Box: Box A und Box B nehmen

Theorie:
  E(1-Box) = 1.000.000 * p + 0 * (1 - p)
  E(2-Box) = 1.000 + 1.000.000 * (1 - p)

Starten:
  python3 newcomb_experiment.py                      (fragt Spielzahl und p ab)
  python3 newcomb_experiment.py --spiele 500 --p 0.7
  python3 newcomb_experiment.py --spiele 500 --p 0.7 --seed 42   (gleiche Zufallszahlen)
"""

import argparse
import random

BOX_A = 1_000_000  # Mystery-Box
BOX_B = 1_000  # offene Box
MIN_SPIELE = 10
MAX_SPIELE = 1000
ZEIGE_SPIELE = 10  # so viele Einzelspiele werden pro Strategie ausgegeben


def euro(betrag: float) -> str:
    """Formatiert einen Betrag deutsch, z. B. 1.000.000 EUR."""
    return f"{betrag:,.0f} EUR".replace(",", ".")


def spiele_einmal(strategie: str, p: float) -> dict:
    """Ein Spiel. Der Praediktor liegt mit Wahrscheinlichkeit p richtig."""
    richtig = random.random() < p
    if strategie == "1-Box":
        vorhersage = "1-Box" if richtig else "2-Box"
    else:
        vorhersage = "2-Box" if richtig else "1-Box"

    box_a = BOX_A if vorhersage == "1-Box" else 0
    gewinn = box_a if strategie == "1-Box" else BOX_B + box_a
    return {"wahl": strategie, "vorhersage": vorhersage, "richtig": richtig, "box_a": box_a, "gewinn": gewinn}


def erwartungswert(strategie: str, p: float) -> float:
    if strategie == "1-Box":
        return BOX_A * p
    return BOX_B + BOX_A * (1 - p)


def zeige_einzelspiele(strategie: str, spiele: list) -> None:
    print(f"\nDie ersten {min(ZEIGE_SPIELE, len(spiele))} Spiele mit {strategie}:")
    print(f"{'Spiel':>5} | {'Vorhersage':<10} | {'Treffer?':<8} | {'Box A':>14} | {'Gewinn':>16}")
    print("-" * 66)
    for nr, s in enumerate(spiele[:ZEIGE_SPIELE], start=1):
        treffer = "ja" if s["richtig"] else "nein"
        print(f"{nr:>5} | {s['vorhersage']:<10} | {treffer:<8} | {euro(s['box_a']):>14} | {euro(s['gewinn']):>16}")


def experiment(n: int, p: float) -> None:
    print(f"\nNewcomb-Experiment: {n} Spiele pro Strategie, Trefferquote p = {p}")
    print("=" * 66)

    ergebnisse = {}
    for strategie in ("1-Box", "2-Box"):
        spiele = [spiele_einmal(strategie, p) for _ in range(n)]
        ergebnisse[strategie] = spiele
        zeige_einzelspiele(strategie, spiele)

    print("\nErgebnis")
    print("=" * 66)
    kopf = f"{'Strategie':<9} | {'Treffer':>9} | {'Theorie (Ø)':>16} | {'Simulation (Ø)':>16} | {'Abweichung':>12}"
    print(kopf)
    print("-" * len(kopf))
    for strategie, spiele in ergebnisse.items():
        treffer = sum(s["richtig"] for s in spiele)
        durchschnitt = sum(s["gewinn"] for s in spiele) / n
        theorie = erwartungswert(strategie, p)
        print(
            f"{strategie:<9} | {treffer:>4}/{n:<4} | {euro(theorie):>16} | "
            f"{euro(durchschnitt):>16} | {durchschnitt - theorie:>+12,.0f}".replace(",", ".")
        )

    besser = "1-Box" if erwartungswert("1-Box", p) > erwartungswert("2-Box", p) else "2-Box"
    print(f"\nIm Erwartungswert ist bei p = {p} die Strategie {besser} besser.")
    print("Kleine Abweichungen zwischen Theorie und Simulation sind normal (Zufall).")


def frage_zahl(text: str, standard, minimum, maximum, typ):
    """Fragt so lange nach, bis eine gueltige Zahl im erlaubten Bereich eingegeben wurde."""
    while True:
        eingabe = input(f"{text} [{standard}]: ").strip().replace(",", ".")
        if eingabe == "":
            return standard
        try:
            wert = typ(eingabe)
        except ValueError:
            print("  Bitte eine Zahl eingeben.")
            continue
        if minimum <= wert <= maximum:
            return wert
        print(f"  Bitte einen Wert zwischen {minimum} und {maximum} eingeben.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Newcomb-Experiment simulieren")
    parser.add_argument("--spiele", type=int, help=f"Anzahl Spiele pro Strategie ({MIN_SPIELE} bis {MAX_SPIELE})")
    parser.add_argument("--p", type=float, help="Trefferquote des Praediktors (0 bis 1)")
    parser.add_argument("--seed", type=int, help="Startwert fuer reproduzierbare Zufallszahlen")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    n = args.spiele
    p = args.p
    if n is None:
        n = frage_zahl(f"Wie viele Spiele ({MIN_SPIELE}-{MAX_SPIELE})?", 100, MIN_SPIELE, MAX_SPIELE, int)
    if p is None:
        p = frage_zahl("Trefferquote p des Praediktors (0 bis 1, z. B. 0.7)?", 0.7, 0.0, 1.0, float)

    if not (MIN_SPIELE <= n <= MAX_SPIELE):
        parser.error(f"--spiele muss zwischen {MIN_SPIELE} und {MAX_SPIELE} liegen")
    if not (0.0 <= p <= 1.0):
        parser.error("--p muss zwischen 0 und 1 liegen")

    experiment(n, p)


if __name__ == "__main__":
    main()
