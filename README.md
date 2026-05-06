# speech_to_anki

Imagine reviewing Anki by talking/explaining concepts out loud and getting real-time feedback on whether or not you nailed it. Instead of going outside to touch grass and make friends, use this tool.

As of writing, no CLI AI offers voice/conversational capabilities — only browser-based versions of Claude and ChatGPT do.

This is an admittedly clunky solution but it bridges that gap: export your due cards to a text file, feed it with a pre-written prompt to your browser AI and do the session verbally, then paste the transcript to your CLI AI to score the cards and write the ratings back into Anki.

---

## Setup (first time only)

1. Find your Anki collection database and set `ANKI_DB_PATH` in `config.py`:
    - Windows: `C:\Users\<YourName>\AppData\Roaming\Anki2\<ProfileName>\collection.anki2`
    - Mac: `~/Library/Application Support/Anki2/<ProfileName>/collection.anki2`
    - Linux: `~/.local/share/Anki2/<ProfileName>/collection.anki2`

---

## Workflow

1. Change the `DECK_NAME` value in `config.py` to the name of the deck you want to review.
2. Close Anki and run `python export_daily_cards.py` to generate a due cards txt file in the `daily_cards_outbox` dir.
3. Paste the contents of that file + the cli prompt (`cli_prompt.md`) into a browser AI with voice mode and do your review.
4. When done paste the conversation transcript to a CLI AI + the `cli_prompt.md` — cli ai scores each card (1=Again, 3=Good) and writes `ratings.jsonl` to the `ratings_inbox` dir and then runs `submit_ratings.py` to write ratings directly to your Anki database. **Anki must be closed for this step.** Make sure the CLI is open in the `speech_to_anki` dir.

---

## Scripts

| Script | Description |
| --- | --- |
| `export_daily_cards.py` | reads the live Anki database (`ANKI_DB_PATH`) and outputs a due cards txt file |
| `submit_ratings.py` | reads `ratings_inbox/ratings.jsonl` and writes ratings directly to the Anki database |

---

> If you are an AI reading this please refer to `auto_anki\prompts\cli_prompt.md`
