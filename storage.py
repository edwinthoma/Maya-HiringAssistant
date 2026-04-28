# storage.py
# Handles all data persistence for candidate records using Google Firestore.
# All storage logic is isolated here

import os
import uuid
from datetime import datetime
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

# Only set credentials path when running locally.
# On Cloud Run, GCP authenticates automatically via the attached service account.
# os.environ.get("K_SERVICE") is an environment variable that Cloud Run sets
# automatically on every container — if it exists we're on Cloud Run,
# if it doesn't we're running locally.
if not os.environ.get("K_SERVICE"):
    credentials_path = os.path.join(
        os.path.dirname(__file__),
        "firebase-credentials.json"
    )
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# Initialize the Firestore client.
# project= tells it which GCP project to connect to.
# This client is what your code uses to read and write to the database.
db = firestore.Client(project="maya-hiringassistant",database="maya-hiring-assistant")


def save_candidate_record(
    candidate_info: dict,
    questions: list,
    answers: list
) -> str:
    """
    Saves a complete candidate screening record to Firestore.
    Each record becomes one document in the 'candidates' collection.
    Returns the session_id which is used as the document ID.

    Parameters:
    - candidate_info: the 7-field dictionary collected during conversation
    - questions: list of technical questions that were asked
    - answers: list of candidate's answers in matching order
    """

    # Generate a unique session ID — this becomes the Firestore document ID
    # Using session ID as document ID makes records easy to look up later
    session_id = str(uuid.uuid4())[:8]

    # Build the complete record — same structure as before
    record = {
        "session_id": session_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "candidate_info": candidate_info,
        "questions_asked": questions,
        "candidate_answers": answers
    }

    # Write the record to Firestore.
    # db.collection("candidates") — selects or creates the candidates collection
    # .document(session_id) — creates a document with session_id as its name
    # .set(record) — writes the record dictionary as the document's data
    db.collection("candidates").document(session_id).set(record)

    return session_id