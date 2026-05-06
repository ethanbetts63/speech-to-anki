# speech_to_anki

Imagine reviewing Anki by talking/explaining concepts out loud and getting real-time feedback on whether or not you nailed it. Instead of going outside to touch grass and make friends, I made this tool.

As of writing, no CLI AI offers voice/conversational capabilities — only browser-based versions of Claude and ChatGPT do.

This is an admittadly clunky solution but it bridges that gap: export your due cards to a text file, feed it with a pre-written prompt to your browser AI and do the session verbally, then paste the transcript to your CLI AI to score the cards and write the ratings back into Anki.

---

## Setup (first time only)

1. Install the AnkiConnect add-on in Anki: Tools > Add-ons > Get Add-ons, enter code `2055492159`.
2. Restart Anki. Now when anki runs a local server is created on port `8765` that the scripts talk to.
3. Set up venv:
    ```
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

---

## Workflow

1. Export your Anki collection as `collection.colpkg` (support older media ticked) and drop it in the collection_inbox dir.
2. Change the `DECK_NAME` value in `config.py` to the name of the deck you want to review.
3. Activate venv (`venv\Scripts\activate`) and run `python anki_due_cards.py` to generate a due cards txt file in the `daily_cards_outbox` dir.
4. Paste the contents of that file + the cli prompt (`cli_prompt.md`) into a browser AI with voice mode and do your review.
5. When done paste the conversation transcript to a CLI AI + the `cli_prompt.md` — cli ai scores each card (1=Again, 3=Good) and writes `ratings.jsonl` to the `ratings_inbox` dir (anki app must be open for this step + make sure cli is open in `speech_to_anki` dir with venv active).

---

## Scripts

| Script | Description |
| `anki_due_cards.py` | reads `collection_inbox/collection.colpkg` and outputs a due cards txt file |
| `anki_submit.py` | reads `ratings_inbox/ratings.jsonl` and submits ratings to Anki via AnkiConnect |
| `anki_review.py` | interactive CLI review directly through AnkiConnect (requires Anki open) |

---

> If you are an AI reading this please refer to `auto_anki\prompts\cli_prompt.md`
