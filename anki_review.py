"""
Interactive CLI review session via AnkiConnect.
Shows each card in the terminal and accepts keyboard ratings.
Anki must be open with the AnkiConnect add-on running.

Usage:
    python anki_review.py
    python anki_review.py <deck name>
"""

import requests
import re
import sys
from config import DECK_NAME, ANKI_URL


def anki(action, **params):
    payload = {"action": action, "version": 6, "params": params}
    r = requests.post(ANKI_URL, json=payload)
    result = r.json()
    if result.get("error"):
        raise RuntimeError(f"AnkiConnect error: {result['error']}")
    return result["result"]


def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    return text.strip()


def get_ease(buttons):
    """Prompt the user for a rating and return their choice, or None if they quit."""
    labels = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
    valid = [str(b) for b in buttons]
    prompt = f"  Rate ({', '.join(f'{b}={labels[b]}' for b in buttons if b in labels)}, q=Quit): "
    while True:
        choice = input(prompt).strip().lower()
        if choice == "q":
            return None
        if choice in valid:
            return int(choice)
        print(f"  Enter one of: {', '.join(valid)} or q")


def review_deck(deck_name):
    anki("guiDeckReview", name=deck_name)

    stats = anki("getDeckStats", decks=[deck_name])
    s = stats[str(list(stats.keys())[0])]
    total = s["review_count"] + s["learn_count"] + s["new_count"]
    print(f"\nDeck: {deck_name}")
    print(f"Due: {s['review_count']} review, {s['learn_count']} learning, {s['new_count']} new ({total} total)")
    print("=" * 60)
    print("Commands: 1=Again  2=Hard  3=Good  4=Easy  q=Quit\n")

    reviewed = 0
    while True:
        card = anki("guiCurrentCard")
        if card is None:
            print(f"\nDone! Reviewed {reviewed} cards.")
            break

        fields = card.get("fields", {})
        values = list(fields.values())
        front = clean_html(values[0]["value"] if values else card.get("question", ""))
        print(f"Q: {front}")
        input("  [Press Enter to show answer]")

        back = clean_html(values[1]["value"] if len(values) > 1 else card.get("answer", ""))
        print(f"A: {back}\n")

        ease = get_ease(card.get("buttons", [1, 2, 3, 4]))
        if ease is None:
            print("Quitting.")
            break
        anki("guiAnswerCard", ease=ease)
        reviewed += 1
        print()


if __name__ == "__main__":
    deck = sys.argv[1] if len(sys.argv) >= 2 else DECK_NAME
    try:
        anki("version")
    except Exception:
        print("Error: Can't reach AnkiConnect. Make sure Anki is open.")
        sys.exit(1)
    review_deck(deck)
