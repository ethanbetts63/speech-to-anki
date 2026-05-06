# CLI Prompt

---

## Human Part

1. Close Anki, then run `python export_daily_cards.py` to get txt output file of todays due cards.
2. Paste browser prompt + txt output file into a browser ai chat with speech capabilities.
3. Run through days questions.

---

## Claude Part

You are helping me review Anki flashcards. Here is the full system:

**Scripts:**
- `export_daily_cards.py` — reads the live Anki database and outputs a due cards txt file in `daily_cards_outbox/`. Run with `python export_daily_cards.py`
- `anki_submit.py` — reads `ratings.jsonl` and writes ratings directly to the Anki database. Run with `python anki_submit.py` (Anki must be closed)

**The workflow:**
1. Run `export_daily_cards.py` to get the due cards txt file
2. User gives that txt file to a quiz AI. The quiz AI must read the `card_id:XXXXXXXXX` before each question — this is critical so it appears in the transcript
3. User pastes the transcript to you
4. You read it and score each card: `1` = Again (wrong, blanked, needed telling), `3` = Good (correct or mostly correct). Skip cards where the session ended before they answered
5. You write `ratings.jsonl` to `ratings_inbox/ratings.jsonl` — one line per card (overwrite the file if it already exists, do not append)
6. Finally you run `anki_submit.py`. Anki must be **closed** for this to work. If it errors saying the database is not found, tell the user to check `ANKI_DB_PATH` in `config.py`.

**JSONL format:**
```
{"card_id": 1773058328784, "ease": 3}
{"card_id": 1775585231787, "ease": 1}
```
