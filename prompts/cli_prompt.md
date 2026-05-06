cli prompt


Human Part:
  1. put "collection" file in collection_inbox dir. file must be anki collection package .colpkg with support older media ticked. 

  2. run python anki_due_cards.py to get txt output file of todays due cards. 

  3. paste browser prompt + txt output file into a browser ai chat with speech capabilities. 

  4. run through days questions


Claude Part: 
  You are helping me review Anki flashcards. Here is the full system:

  Folder: C:\Users\ethan\coding\auto_anki\

  Scripts:
  - anki_due_cards.py — reads collection.colpkg from the collection_inbox folder and outputs
  computer systems_due_cards.txt with due cards including card IDs. Run with python
  anki_due_cards.py
  - anki_submit.py — reads ratings.jsonl and submits ratings to Anki via AnkiConnect. Run with
  python anki_submit.py (Anki must be open)

  The workflow:
  1. User exports their Anki collection as a .colpkg file and drops it in auto_anki/collection_inbox/ as
  collection.colpkg
  2. Run anki_due_cards.py to get the due cards txt file
  3. User gives that txt file to a quiz AI. The quiz AI must read the card_id:XXXXXXXXX before each
   question — this is critical so it appears in the transcript
  4. User pastes the transcript to you
  5. You read it and score each card: 1 = Again (wrong, blanked, needed telling), 3 = Good (correct
   or mostly correct). Skip cards where the session ended before they answered
  6. You write ratings.jsonl to C:\Users\ethan\coding\speech_to_anki\ratings_inbox\ratings.jsonl — one line per card (overwrite the file if it already exists, do not append):
  {"card_id": 1234567890, "ease": 3}
  7. Finally you run anki_submit.py if it doesn't work it's likely the user didn't have the anki app open and you should instruct them to do so.

  JSONL format:
  {"card_id": 1773058328784, "ease": 3}
  {"card_id": 1775585231787, "ease": 1}