# Kenó 2x10 Analytics v2.1.0

Teljes, helyben futó Windows asztali alkalmazás magyar felülettel. Python 3.11+ szükséges a forrásból futtatáshoz.

## Indítás
Dupla kattintás: `run_keno.bat`. Rejtett konzollal: `run_hidden.vbs`.

## Fő funkciók
- draws.csv validáció és SQLite import
- lezárt, reprodukálható forecast teljes 1-80 rangsorral
- 20-as keret és diszjunkt A/B 10-es sor
- automatikus értékelés új húzáskor
- missed-winner és selected-miss diagnosztika
- hibakatalógus és evidence store
- bounded challenger generálás
- 1000 húzásos páros walk-forward, bootstrap CI és promotion gate
- magyar grafikus felület

## Fontos
A program statisztikai elemzőeszköz. Nyereményt nem garantál. Challenger csak a szigorú kapu teljesülése esetén léptethető elő; a jelen verzió automatikusan nem írja felül a championt.
