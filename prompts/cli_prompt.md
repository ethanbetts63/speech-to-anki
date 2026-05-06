# CLI Prompt

---

## Human Part

1. Put "collection" file in `collection_inbox` dir. File must be anki collection package `.colpkg` with support older media ticked.
2. Run `python anki_due_cards.py` to get txt output file of todays due cards.
3. Paste browser prompt + txt output file into a browser ai chat with speech capabilities.
4. Run through days questions.

---

## Claude Part

You are helping me review Anki flashcards. Here is the full system:

**Scripts:**
- `anki_due_cards.py` — reads `collection.colpkg` from the `collection_inbox` folder and outputs `computer systems_due_cards.txt` with due cards including card IDs. Run with `python anki_due_cards.py`
- `anki_submit.py` — reads `ratings.jsonl` and submits ratings to Anki via AnkiConnect. Run with `python anki_submit.py` (Anki must be open)

**The workflow:**
1. User exports their Anki collection as a `.colpkg` file and drops it in `collection_inbox/` as `collection.colpkg`
2. Run `anki_due_cards.py` to get the due cards txt file
3. User gives that txt file to a quiz AI. The quiz AI must read the `card_id:XXXXXXXXX` before each question — this is critical so it appears in the transcript
4. User pastes the transcript to you
5. You read it and score each card: `1` = Again (wrong, blanked, needed telling), `3` = Good (correct or mostly correct). Skip cards where the session ended before they answered
6. You write `ratings.jsonl` to `ratings_inbox/ratings.jsonl` — one line per card (overwrite the file if it already exists, do not append)
7. Finally you run `anki_submit.py`. Anki must be **closed** for this to work. If it errors saying the database is not found, tell the user to check `ANKI_DB_PATH` in `config.py`.

**JSONL format:**
```
{"card_id": 1773058328784, "ease": 3}
{"card_id": 1775585231787, "ease": 1}
```
