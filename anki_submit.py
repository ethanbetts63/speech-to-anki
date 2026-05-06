"""
Reads ratings.jsonl and submits each card rating directly to the Anki SQLite database.
Anki MUST be closed when running this script.

Usage:
    python anki_submit.py
    python anki_submit.py <ratings.jsonl>
"""

import sqlite3
import json
import sys
import os
import time
from config import ANKI_DB_PATH

RATINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ratings_inbox", "ratings.jsonl")


def load_ratings(path):
    ratings = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            ratings[int(entry["card_id"])] = int(entry["ease"])
    return ratings


def get_today(cur):
    cur.execute("SELECT crt, conf FROM col")
    crt, conf_raw = cur.fetchone()
    conf = json.loads(conf_raw) if conf_raw else {}
    rollover = conf.get("rollover", 4)
    local_offset = conf.get("localOffset", 0)
    now_ts = int(time.time())
    offset_secs = local_offset * 60
    today = ((now_ts + offset_secs - rollover * 3600) // 86400
           - (crt    + offset_secs - rollover * 3600) // 86400)
    return today, now_ts


def apply_rating(cur, card_id, ease, today, now_ts, index):
    cur.execute("SELECT queue, ivl, factor, reps, lapses FROM cards WHERE id=?", (card_id,))
    row = cur.fetchone()
    if row is None:
        print(f"  [WARN] card {card_id} not found in database")
        return False

    queue, ivl, factor, reps, lapses = row
    labels = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}

    if ease == 3:  # Good
        if queue == 2:
            new_ivl = max(ivl + 1, round(ivl * factor / 1000.0))
        else:
            new_ivl = max(1, ivl if ivl > 0 else 1)
        new_factor = factor
        new_lapses = lapses
        cur.execute(
            "UPDATE cards SET queue=2, type=2, due=?, ivl=?, factor=?, reps=?, lapses=?, mod=?, usn=-1 WHERE id=?",
            (today + new_ivl, new_ivl, new_factor, reps + 1, new_lapses, now_ts, card_id),
        )

    elif ease == 1:  # Again
        new_factor = max(1300, factor - 200)
        new_ivl = 1
        new_lapses = lapses + 1
        cur.execute(
            "UPDATE cards SET due=?, ivl=?, factor=?, reps=?, lapses=?, mod=?, usn=-1 WHERE id=?",
            (today + new_ivl, new_ivl, new_factor, reps + 1, new_lapses, now_ts, card_id),
        )

    revlog_ivl = new_ivl if ease >= 2 else -new_ivl
    cur.execute(
        "INSERT OR IGNORE INTO revlog (id, cid, usn, ease, ivl, lastIvl, factor, time, type) VALUES (?,?,?,?,?,?,?,?,?)",
        (now_ts * 1000 + index, card_id, -1, ease, revlog_ivl, ivl, factor, 1000, 1),
    )

    print(f"  [{index + 1}] card {card_id} -> {ease} ({labels.get(ease, '?')})")
    return True


def submit_ratings(db_path, jsonl_path):
    ratings = load_ratings(jsonl_path)
    print(f"Loaded {len(ratings)} ratings from {jsonl_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    today, now_ts = get_today(cur)

    succeeded = 0
    for i, (card_id, ease) in enumerate(ratings.items()):
        if apply_rating(cur, card_id, ease, today, now_ts, i):
            succeeded += 1

    cur.execute("UPDATE col SET mod=?, usn=-1", (now_ts,))
    conn.commit()
    conn.close()

    print(f"\nDone. {succeeded}/{len(ratings)} submitted.")


if __name__ == "__main__":
    jsonl = sys.argv[1] if len(sys.argv) >= 2 else RATINGS_PATH

    if not os.path.exists(ANKI_DB_PATH):
        print(f"Error: Anki database not found at {ANKI_DB_PATH}")
        print("Check ANKI_DB_PATH in config.py.")
        sys.exit(1)

    submit_ratings(ANKI_DB_PATH, jsonl)
