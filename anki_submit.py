"""
Reads ratings.jsonl and submits each card rating to Anki via AnkiConnect.
Anki must be open with the AnkiConnect add-on running.

Usage:
    python anki_submit.py
    python anki_submit.py <ratings.jsonl>
    python anki_submit.py <ratings.jsonl> <deck name>
"""

import requests
import json
import sys
import os
import time
from config import DECK_NAME, ANKI_URL

RATINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ratings.jsonl")


def anki(action, **params):
    payload = {"action": action, "version": 6, "params": params}
    r = requests.post(ANKI_URL, json=payload)
    result = r.json()
    if result.get("error"):
        raise RuntimeError(f"AnkiConnect error: {result['error']}")
    return result["result"]


def load_ratings(jsonl_path):
    ratings = {}
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            ratings[int(entry["card_id"])] = int(entry["ease"])
    return ratings


def submit_ratings(deck_name, jsonl_path):
    ratings = load_ratings(jsonl_path)
    print(f"Loaded {len(ratings)} ratings from {jsonl_path}")

    anki("guiDeckReview", name=deck_name)
    time.sleep(1)  # give Anki time to open the review screen

    submitted = 0
    remaining = set(ratings.keys())

    while remaining:
        card = anki("guiCurrentCard")
        if card is None:
            print("No current card — review session ended or not active.")
            break

        card_id = card.get("cardId")
        anki("guiShowAnswer")

        if card_id in remaining:
            ease = ratings[card_id]
            labels = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
            anki("guiAnswerCard", ease=ease)
            print(f"  card {card_id} -> {ease} ({labels.get(ease, '?')})")
            remaining.discard(card_id)
            submitted += 1
        else:
            # Card wasn't in the transcript — mark Good and move on.
            anki("guiAnswerCard", ease=3)

        time.sleep(0.1)

    print(f"\nDone. Submitted: {submitted} ratings.")
    if remaining:
        print(f"{len(remaining)} transcript card(s) never appeared in the queue (may already be answered).")
    print("Any remaining due cards are still in your Anki queue.")


if __name__ == "__main__":
    jsonl = sys.argv[1] if len(sys.argv) >= 2 else RATINGS_PATH
    deck  = sys.argv[2] if len(sys.argv) >= 3 else DECK_NAME

    try:
        anki("version")
    except Exception:
        print("Error: Can't reach AnkiConnect. Make sure Anki is open.")
        sys.exit(1)

    submit_ratings(deck, jsonl)
