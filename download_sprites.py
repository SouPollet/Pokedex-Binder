#!/usr/bin/env python3
"""
Downloads official-artwork sprites for Pokémon #1-251 (Gen I & II)
into a local `sprites/` folder next to this script, named 001.png ... 251.png
to match what pokedex-binder.html expects.

Usage:
    pip install requests
    python download_sprites.py

Re-running is safe: already-downloaded files are skipped.
"""

import os
import time
import requests

TOTAL = 251
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")

PRIMARY_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{id}.png"
FALLBACK_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png"

def download_one(pokemon_id: int, session: requests.Session) -> bool:
    filename = f"{pokemon_id:03d}.png"
    filepath = os.path.join(OUT_DIR, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"  [skip] {filename} already exists")
        return True

    for url_template in (PRIMARY_URL, FALLBACK_URL):
        url = url_template.format(id=pokemon_id)
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code == 200 and resp.content:
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                print(f"  [ok]   {filename}")
                return True
        except requests.RequestException as e:
            print(f"  [warn] {filename} failed on {url_template.split('/')[2]}: {e}")

    print(f"  [FAIL] {filename} — could not download from any source")
    return False

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Saving sprites to: {OUT_DIR}\n")

    session = requests.Session()
    session.headers.update({"User-Agent": "pokedex-binder-sprite-downloader/1.0"})

    failures = []
    for pokemon_id in range(1, TOTAL + 1):
        ok = download_one(pokemon_id, session)
        if not ok:
            failures.append(pokemon_id)
        time.sleep(0.05)  # be polite to the server

    print("\nDone.")
    if failures:
        print(f"{len(failures)} sprite(s) failed: {failures}")
        print("Re-run the script to retry just the missing ones.")
    else:
        print(f"All {TOTAL} sprites downloaded successfully.")

if __name__ == "__main__":
    main()
