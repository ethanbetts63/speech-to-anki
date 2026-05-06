import os

# Edit these to match your setup. (e.g. DECK_NAME = "computer systems")
DECK_NAME = "computer systems"
COLLECTION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collection_inbox", "collection.colpkg")

# Path to your live Anki SQLite database. Anki must be CLOSED when running anki_submit.py.
# Windows: C:\Users\<YourName>\AppData\Roaming\Anki2\<ProfileName>\collection.anki2
# Mac:     ~/Library/Application Support/Anki2/<ProfileName>/collection.anki2
# Linux:   ~/.local/share/Anki2/<ProfileName>/collection.anki2
ANKI_DB_PATH = r"C:\Users\ethan\AppData\Roaming\Anki2\User 1\collection.anki2"

ANKI_URL = "http://localhost:8765"  # used by anki_review.py only
