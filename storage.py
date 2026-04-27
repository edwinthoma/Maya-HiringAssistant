# storage.py
# Handles all data persistence for candidate records.

import json
import os
from datetime import datetime
import uuid

# Path to the JSON file where all candidate records are stored
# os.path.dirname(__file__) gets the directory where storage.py lives
# This ensures the file is always created in the project root
STORAGE_FILE = os.path.join(os.path.dirname(__file__), "candidates.json")


def load_existing_records() -> list:
    """
    Reads the existing candidates.json file and returns all records as a list.
    If the file doesn't exist yet, returns an empty list.
    
    Why check if file exists?
    The first time this runs, candidates.json doesn't exist yet.
    Trying to open a non-existent file would crash the app.
    """
    if not os.path.exists(STORAGE_FILE):
        return []
    
    with open(STORAGE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # If the file exists but is corrupted or empty, return empty list
            # This prevents a corrupted file from crashing the entire app
            return []


def save_candidate_record(
    candidate_info: dict,
    questions: list,
    answers: list
) -> str:
    """
    Builds a complete candidate record and appends it to candidates.json.
    Returns the session_id so it can be referenced later if needed.
    
    Parameters:
    - candidate_info: the 7-field dictionary collected during conversation
    - questions: list of technical questions that were asked
    - answers: list of candidate's answers in matching order
    """

    # Generate a unique session ID for this candidate record
    # uuid4() generates a random unique identifier
    # [:8] takes only the first 8 characters — short enough to be readable
    session_id = str(uuid.uuid4())[:8]

    # Build the complete record
    record = {
        "session_id": session_id,
        # datetime.now() gets current date and time
        # strftime formats it as a readable string e.g. "2026-04-28 14:32:11"
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "candidate_info": candidate_info,
        "questions_asked": questions,
        "candidate_answers": answers
    }

    # Load existing records, append the new one, save everything back
    # This is how we accumulate multiple candidates in one file
    existing_records = load_existing_records()
    existing_records.append(record)

    with open(STORAGE_FILE, "w") as f:
        # indent=4 makes the JSON human-readable with proper indentation
        json.dump(existing_records, f, indent=4)

    return session_id