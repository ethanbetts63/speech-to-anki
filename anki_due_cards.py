"""
Reads the live Anki SQLite database and writes a due cards txt file to
daily_cards_outbox/. The output file is intended to be fed to a browser AI
for a verbal review session. Anki must be closed when running this script.

Usage:
    python anki_due_cards.py
    python anki_due_cards.py <deck name>
    python anki_due_cards.py <deck name> <output.txt>
"""

import sqlite3
import json
import os
import re
import sys
import time
from datetime import datetime
from config import DECK_NAME, ANKI_DB_PATH


def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    return text.strip()


def find_deck_id(cur, deck_name):
    """Return the deck ID for deck_name. Handles both old (JSON blob) and new (decks table) schemas."""
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='decks'")
    if cur.fetchone():
        cur.execute("SELECT id, name FROM decks")
        for did, name in cur.fetchall():
            if name.lower() == deck_name.lower():
                return did
        cur.execute("SELECT id, name FROM decks")
        available = [name for _, name in cur.fetchall()]
        raise ValueError(f"Deck '{deck_name}' not found. Available: {available}")
    else:
        # Older Anki stores deck metadata as a JSON blob in the col table.
        cur.execute("SELECT decks FROM col")
        decks_json = json.loads(cur.fetchone()[0])
        rows = [(int(did), d['name']) for did, d in decks_json.items()]
        for did, name in rows:
            if name.lower() == deck_name.lower():
                return did
        raise ValueError(f"Deck '{deck_name}' not found. Available: {[n for _, n in rows]}")


def calc_days_elapsed(cur):
    """
    Return (days_elapsed, now_ts) using the collection's own timezone offset and
    day-rollover hour so due dates match exactly what Anki shows.
    """
    cur.execute("SELECT crt, conf FROM col")
    crt, conf_raw = cur.fetchone()
    conf = json.loads(conf_raw) if conf_raw else {}

    rollover = conf.get('rollover', 4)        # hour of day Anki considers a new day (default 4am)
    local_offset = conf.get('localOffset', 0) # minutes east of UTC

    now_ts = int(time.time())
    offset_secs = local_offset * 60
    days_elapsed = (now_ts + offset_secs - rollover * 3600) // 86400 \
                 - (crt    + offset_secs - rollover * 3600) // 86400
    return days_elapsed, now_ts


def extract_due_cards(anki_db_path, deck_name, output_path=None):
    if not os.path.exists(anki_db_path):
        print(f"Error: file not found: {anki_db_path}")
        sys.exit(1)

    today = datetime.now().strftime('%Y-%m-%d')

    if output_path is None:
        outbox = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_cards_outbox")
        output_path = os.path.join(outbox, f"{deck_name}_due_cards_{today}.txt")

    conn = sqlite3.connect(anki_db_path)
    cur = conn.cursor()

    deck_id = find_deck_id(cur, deck_name)
    days_elapsed, now_ts = calc_days_elapsed(cur)

    # queue 1 = learning (due by timestamp), queue 2 = review, queue 3 = day-learn relearn
    cur.execute("""
        SELECT c.id, n.flds
        FROM cards c
        JOIN notes n ON c.nid = n.id
        WHERE c.did = ?
          AND (
              (c.queue = 1 AND c.due <= ?)
           OR (c.queue = 2 AND c.due <= ?)
           OR (c.queue = 3 AND c.due <= ?)
          )
        ORDER BY c.due
    """, (deck_id, now_ts, days_elapsed, days_elapsed))

    rows = cur.fetchall()
    conn.close()

    cards = []
    for card_id, flds in rows:
        fields = flds.split('\x1f')
        front = clean_html(fields[0]) if fields else ""
        back  = clean_html(fields[1]) if len(fields) > 1 else ""
        if front or back:
            cards.append((card_id, front, back))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Due Cards: {deck_name} -- {today}\n")
        f.write(f"Total: {len(cards)} cards\n")
        f.write("=" * 60 + "\n\n")
        for i, (card_id, front, back) in enumerate(cards, 1):
            f.write(f"[{i}] card_id:{card_id}\n")
            f.write(f"Q: {front}\n")
            f.write(f"A: {back}\n\n")

    print(f"Extracted {len(cards)} due cards -> {output_path}")
    return output_path


if __name__ == "__main__":
    deck = sys.argv[1] if len(sys.argv) >= 2 else DECK_NAME
    out  = sys.argv[2] if len(sys.argv) >= 3 else None

    extract_due_cards(ANKI_DB_PATH, deck, out)
