"""
Newcomb-Experiment: Simulation mit einstellbarer Spielzahl und Trefferquote p
Newcomb experiment: simulation with adjustable number of games and hit rate p

Aufbau / Setup:
  - Box B (offen) enthaelt immer 1.000 EUR.
    Box B (open) always contains 1,000 EUR.
  - Box A (Mystery-Box, verdeckt) enthaelt 1.000.000 EUR, wenn der Praediktor "1-Box" getippt hat,
    sonst ist sie leer.
    Box A (mystery box, hidden) contains 1,000,000 EUR if the predictor guessed "1-Box", otherwise it is empty.
  - Der Praediktor tippt VOR deiner Wahl und liegt mit Wahrscheinlichkeit p richtig.
    The predictor guesses BEFORE you choose and is right with probability p.

Strategien / Strategies:
  - 1-Box: nur Box A nehmen (die Mystery-Box) / take only Box A (the mystery box)
  - 2-Box: Box A und Box B nehmen / take Box A and Box B

Theorie / Theory:
  E(1-Box) = 1.000.000 * p + 0 * (1 - p)
  E(2-Box) = 1.000 + 1.000.000 * (1 - p)

Starten / Run:
  python3 newcomb_experiment.py                      (fragt Sprache, Spielzahl und p ab / asks for language, games and p)
  python3 newcomb_experiment.py --spiele 500 --p 0.7
  python3 newcomb_experiment.py --games 500 --p 0.7 --lang en
  python3 newcomb_experiment.py --spiele 500 --p 0.7 --seed 42   (gleiche Zufallszahlen / same random numbers)
"""

import argparse
import random
import sys

BOX_A = 1_000_000  # Mystery-Box / mystery box
BOX_B = 1_000  # offene Box / open box
MIN_SPIELE = 10
MAX_SPIELE = 1000
ZEIGE_SPIELE = 10  # so viele Einzelspiele werden pro Strategie ausgegeben / games shown per strategy

LANG = "de"

TEXTS = {
    "de": {
        "description": "Newcomb-Experiment simulieren",
        "first_games": "\nDie ersten {k} Spiele mit {s}:",
        "col_game": "Spiel",
        "col_pred": "Vorhersage",
        "col_hit": "Treffer?",
        "col_box": "Box A",
        "col_gain": "Gewinn",
        "yes": "ja",
        "no": "nein",
        "header": "\nNewcomb-Experiment: {n} Spiele pro Strategie, Trefferquote p = {p}",
        "result": "\nErgebnis",
        "res_strategy": "Strategie",
        "res_hits": "Treffer",
        "res_theory": "Theorie (Ø)",
        "res_sim": "Simulation (Ø)",
        "res_dev": "Abweichung",
        "better": "\nIm Erwartungswert ist bei p = {p} die Strategie {s} besser.",
        "note": "Kleine Abweichungen zwischen Theorie und Simulation sind normal (Zufall).",
        "ask_games": "Wie viele Spiele ({a}-{b})?",
        "ask_p": "Trefferquote p des Praediktors (0 bis 1, z. B. 0.7)?",
        "need_number": "  Bitte eine Zahl eingeben.",
        "need_range": "  Bitte einen Wert zwischen {a} und {b} eingeben.",
        "err_games": "--spiele muss zwischen {a} und {b} liegen",
        "err_p": "--p muss zwischen 0 und 1 liegen",
        "help_games": "Anzahl Spiele pro Strategie ({a} bis {b}) / number of games per strategy",
        "help_p": "Trefferquote des Praediktors (0 bis 1) / hit rate of the predictor",
        "help_seed": "Startwert fuer reproduzierbare Zufallszahlen / seed for reproducible random numbers",
        "help_lang": "Sprache / language: de oder/or en",
    },
    "en": {
        "description": "Simulate the Newcomb experiment",
        "first_games": "\nThe first {k} games with {s}:",
        "col_game": "Game",
        "col_pred": "Prediction",
        "col_hit": "Hit?",
        "col_box": "Box A",
        "col_gain": "Winnings",
        "yes": "yes",
        "no": "no",
        "header": "\nNewcomb experiment: {n} games per strategy, hit rate p = {p}",
        "result": "\nResult",
        "res_strategy": "Strategy",
        "res_hits": "Hits",
        "res_theory": "Theory (avg.)",
        "res_sim": "Simulation (avg.)",
        "res_dev": "Deviation",
        "better": "\nIn terms of expected value, {s} is the better strategy at p = {p}.",
        "note": "Small deviations between theory and simulation are normal (chance).",
        "ask_games": "How many games ({a}-{b})?",
        "ask_p": "Hit rate p of the predictor (0 to 1, e.g. 0.7)?",
        "need_number": "  Please enter a number.",
        "need_range": "  Please enter a value between {a} and {b}.",
        "err_games": "--games must be between {a} and {b}",
        "err_p": "--p must be between 0 and 1",
        "help_games": "number of games per strategy ({a} to {b}) / Anzahl Spiele pro Strategie",
        "help_p": "hit rate of the predictor (0 to 1) / Trefferquote des Praediktors",
        "help_seed": "seed for reproducible random numbers / Startwert fuer Zufallszahlen",
        "help_lang": "language / Sprache: de or/oder en",
    },
}


def set_lang(lang: str) -> None:
    """Stellt die Sprache ein ('de' oder 'en'). / Sets the language ('de' or 'en')."""
    global LANG
    LANG = "en" if lang == "en" else "de"


def t(key: str, **kwargs) -> str:
    return TEXTS[LANG][key].format(**kwargs)


def zahl(wert: float, stellen: int = 0, vorzeichen: bool = False) -> str:
    """Formatiert eine Zahl: Deutsch 1.000,5 / Englisch 1,000.5."""
    flags = "+" if vorzeichen else ""
    text = f"{wert:{flags},.{stellen}f}"
    if LANG == "de":
        text = text.replace(",", "_").replace(".", ",").replace("_", ".")
    return text


def euro(betrag: float) -> str:
    """Formatiert einen Betrag, z. B. 1.000.000 EUR (de) oder 1,000,000 EUR (en)."""
    return f"{zahl(betrag)} EUR"


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
    print(t("first_games", k=min(ZEIGE_SPIELE, len(spiele)), s=strategie))
    print(
        f"{t('col_game'):>5} | {t('col_pred'):<10} | {t('col_hit'):<8} | {t('col_box'):>14} | {t('col_gain'):>16}"
    )
    print("-" * 66)
    for nr, s in enumerate(spiele[:ZEIGE_SPIELE], start=1):
        treffer = t("yes") if s["richtig"] else t("no")
        print(f"{nr:>5} | {s['vorhersage']:<10} | {treffer:<8} | {euro(s['box_a']):>14} | {euro(s['gewinn']):>16}")


def experiment(n: int, p: float) -> None:
    print(t("header", n=n, p=p))
    print("=" * 66)

    ergebnisse = {}
    for strategie in ("1-Box", "2-Box"):
        spiele = [spiele_einmal(strategie, p) for _ in range(n)]
        ergebnisse[strategie] = spiele
        zeige_einzelspiele(strategie, spiele)

    print(t("result"))
    print("=" * 66)
    breite = max(16, len(t("res_theory")), len(t("res_sim")))
    kopf = (
        f"{t('res_strategy'):<9} | {t('res_hits'):>9} | {t('res_theory'):>{breite}} | "
        f"{t('res_sim'):>{breite}} | {t('res_dev'):>12}"
    )
    print(kopf)
    print("-" * len(kopf))
    for strategie, spiele in ergebnisse.items():
        treffer = sum(s["richtig"] for s in spiele)
        durchschnitt = sum(s["gewinn"] for s in spiele) / n
        theorie = erwartungswert(strategie, p)
        print(
            f"{strategie:<9} | {treffer:>4}/{n:<4} | {euro(theorie):>{breite}} | "
            f"{euro(durchschnitt):>{breite}} | {zahl(durchschnitt - theorie, vorzeichen=True):>12}"
        )

    besser = "1-Box" if erwartungswert("1-Box", p) > erwartungswert("2-Box", p) else "2-Box"
    print(t("better", p=p, s=besser))
    print(t("note"))


def frage_zahl(text: str, standard, minimum, maximum, typ):
    """Fragt so lange nach, bis eine gueltige Zahl im erlaubten Bereich eingegeben wurde."""
    while True:
        eingabe = input(f"{text} [{standard}]: ").strip().replace(",", ".")
        if eingabe == "":
            return standard
        try:
            wert = typ(eingabe)
        except ValueError:
            print(t("need_number"))
            continue
        if minimum <= wert <= maximum:
            return wert
        print(t("need_range", a=minimum, b=maximum))


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
    parser = argparse.ArgumentParser(description="Newcomb-Experiment / Newcomb experiment")
    parser.add_argument("--spiele", "--games", type=int, help=t("help_games", a=MIN_SPIELE, b=MAX_SPIELE))
    parser.add_argument("--p", type=float, help=t("help_p"))
    parser.add_argument("--seed", type=int, help=t("help_seed"))
    parser.add_argument("--lang", choices=["de", "en"], help=t("help_lang"))
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    n = args.spiele
    p = args.p
    set_lang(args.lang or (frage_sprache() if (n is None or p is None) else "de"))

    if n is None:
        n = frage_zahl(t("ask_games", a=MIN_SPIELE, b=MAX_SPIELE), 100, MIN_SPIELE, MAX_SPIELE, int)
    if p is None:
        p = frage_zahl(t("ask_p"), 0.7, 0.0, 1.0, float)

    if not (MIN_SPIELE <= n <= MAX_SPIELE):
        parser.error(t("err_games", a=MIN_SPIELE, b=MAX_SPIELE))
    if not (0.0 <= p <= 1.0):
        parser.error(t("err_p"))

    experiment(n, p)


if __name__ == "__main__":
    main()
