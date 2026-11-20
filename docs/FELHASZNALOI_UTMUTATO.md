# Felhasználói útmutató

1. Windows alatt csomagold ki a ZIP-et.
2. Telepíts Python 3.11 vagy újabb verziót a python.org oldalról, és jelöld be az Add Python to PATH opciót.
3. Indítsd a run_keno.bat fájlt.
4. Az Előrejelzés lap automatikusan lezárja a következő napi forecastot.
5. Ha a draws.csv fájlhoz hozzáadod az új, rendezett 20 számos húzást, az Értékelés gomb feldolgozza a korábbi lezárt forecastot, feltölti a Missed Winner és Hibakatalógus lapokat.
6. A Governance lapon challenger készíthető. A Walk-forward lapon a 1000 húzásos kapu dönti el, hogy egyáltalán alkalmas-e előléptetésre.

Az adatbázis: data/keno_v21.sqlite. Frissítés előtt erről és a draws.csv fájlról készíts másolatot.
