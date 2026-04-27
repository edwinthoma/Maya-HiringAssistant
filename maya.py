#This File contains the core conversation engine for Maya
from openai import OpenAI
from prompts import (
    SYSTEM_PROMPT,
    EXTRACTION_PROMPT,
    QUESTION_GENERATION_PROMPT,
    INTERVIEW_INTRO_PROMPT,
    NEXT_QUESTION_PROMPT,
    CLOSING_PROMPT
)
from storage import save_candidate_record
import streamlit as st
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def initialize_session():
    #We start with the system prompt so maya knows her role
    if "messages" not in st.session_state:
        st.session_state.messages=[
            {"role":"system","content":SYSTEM_PROMPT} 
        ]
    #Structured Storage for candidate info w extract during conversation
    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info={
            "name":None,
            "email":None,
            "phone_number":None,
            "experience":None,
            "position":None,
            "location":None,
            "tech_stack":None
        }
    #tracks which phase the conversation is currently in .(gathering,questioning,closing)
    if "phase" not in st.session_state:
        st.session_state.phase="gathering"
        
    # All generated technical questions stored here
    if "questions" not in st.session_state:
        st.session_state.questions = []

    # Index of the current question being asked
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0

    # Candidate answers stored in order matching questions list
    if "answers" not in st.session_state:
        st.session_state.answers = []

    # Flag to prevent regenerating questions on every rerun
    if "questions_generated" not in st.session_state:
        st.session_state.questions_generated = False
    
    #Flag to disable input once onversation has ended 
    if "conversation_ended" not in st.session_state:
        st.session_state.conversation_ended= False
        
def get_maya_response(user_input: str) -> str:
    """
    Sends user input + full conversation history to OpenAI.
    Returns Maya's response and updates conversation history.
    """

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        temperature=0.5,
        max_tokens=500
    )

    maya_reply = response.choices[0].message.content

    st.session_state.messages.append({
        "role": "assistant",
        "content": maya_reply
    })

    return maya_reply

def get_opening_greeting() -> str:
    """
    Generates Maya's opening message without appending a fake user message.
    Used only once on app first load.
    We call the API directly here instead of going through get_maya_response()
    because we don't want a user turn in the history — just Maya speaking first.
    """
    opening_instruction = {
        "role": "system",
        "content": "Begin the conversation with your greeting and ask for language preference."
    }

    response = client.chat.completions.create(
        model="gpt-4o",
        # We pass history + a temporary instruction — not appended permanently
        messages=st.session_state.messages + [opening_instruction],
        temperature=0.7,
        max_tokens=200
    )

    maya_reply = response.choices[0].message.content

    # Only append Maya's reply — no user message added
    st.session_state.messages.append({
        "role": "assistant",
        "content": maya_reply
    })

    return maya_reply


def extract_candidate_info() -> dict:
    """
    Silent background API call that reads conversation history
    and extracts structured candidate data as JSON.
    Never shown to the candidate.
    """

    conversation_transcript = ""
    for msg in st.session_state.messages[1:]:
        role = "Candidate" if msg["role"] == "user" else "Maya"
        conversation_transcript += f"{role}: {msg['content']}\n"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": conversation_transcript}
        ],
        # temperature=0 for deterministic JSON output
        temperature=0,
        max_tokens=300
    )

    raw_response = response.choices[0].message.content

    try:
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass

    return st.session_state.candidate_info


def update_candidate_info():
    """
    Runs extraction and merges results into session state.
    Only updates fields that were actually found — never overwrites with null.
    """

    extracted = extract_candidate_info()

    for field, value in extracted.items():
        if value is not None:
            st.session_state.candidate_info[field] = value


def check_info_complete() -> bool:
    """
    Returns True only when all 7 candidate fields are filled.
    This triggers the switch from gathering to questioning phase.
    """
    return all(
        value is not None
        for value in st.session_state.candidate_info.values()
    )


def generate_questions() -> list:
    """
    Makes a dedicated API call to generate 5-7 technical questions
    based on the candidate's tech stack.
    Returns a list of question strings.
    
    Why a separate API call?
    Question generation needs precise JSON output and higher token limit.
    Keeping it isolated means we can retry it independently if it fails.
    """

    info = st.session_state.candidate_info
    tech_list = ", ".join(info["tech_stack"]) if isinstance(
        info["tech_stack"], list
    ) else info["tech_stack"]

    # Build context about the candidate for the question generator
    candidate_context = f"""
    Candidate: {info['name']}
    Experience: {info['experience']}
    Desired Position: {info['position']}
    Tech Stack: {tech_list}
    
    Generate 5-7 technical questions for this candidate.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": QUESTION_GENERATION_PROMPT},
            {"role": "user", "content": candidate_context}
        ],
        temperature=0.7,
        max_tokens=800
    )

    raw = response.choices[0].message.content

    try:
        # Extract JSON array from response
        json_match = re.search(r'\[.*\]', raw, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group())
            return questions
    except json.JSONDecodeError:
        pass

    # Fallback — if JSON parsing fails return a safe default list
    return ["Can you walk me through a challenging technical project you've worked on?"]


def start_interview() -> str:
    """
    Called once when all info is collected.
    Generates questions, stores them, and asks the first one through Maya.
    """

    # Generate and store all questions
    questions = generate_questions()
    st.session_state.questions = questions
    st.session_state.questions_generated = True
    st.session_state.phase = "questioning"

    # Build the intro message with the first question injected
    intro_prompt = INTERVIEW_INTRO_PROMPT.format(
        first_question=questions[0]
    )

    # Add intro prompt as system instruction so Maya delivers it naturally
    st.session_state.messages.append({
        "role": "system",
        "content": intro_prompt
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        temperature=0.7,
        max_tokens=300
    )

    maya_reply = response.choices[0].message.content

    st.session_state.messages.append({
        "role": "assistant",
        "content": maya_reply
    })

    return maya_reply


def handle_answer_and_next(user_answer: str) -> str:
    """
    Called during the questioning phase on every user message.
    Saves the answer, moves to the next question or closes the interview.
    
    Parameters:
    - user_answer: what the candidate just typed in response to the question
    """

    # Save the candidate's answer
    st.session_state.answers.append(user_answer)
    st.session_state.current_question_index += 1

    current_index = st.session_state.current_question_index
    total_questions = len(st.session_state.questions)

    if current_index < total_questions:
        # There are more questions — acknowledge answer and ask the next one
        next_question = st.session_state.questions[current_index]

        next_prompt = NEXT_QUESTION_PROMPT.format(
            answer=user_answer,
            next_question=next_question
        )

        st.session_state.messages.append({
            "role": "system",
            "content": next_prompt
        })

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            temperature=0.7,
            max_tokens=300
        )

        maya_reply = response.choices[0].message.content

        st.session_state.messages.append({
            "role": "assistant",
            "content": maya_reply
        })

        return maya_reply

    else:
        # All questions answered — save record and close conversation
        return close_interview()


def close_interview() -> str:
    """
    Called after the final question is answered.
    Saves the complete candidate record to JSON and ends the conversation.
    """

    # Save everything to candidates.json
    session_id = save_candidate_record(
        candidate_info=st.session_state.candidate_info,
        questions=st.session_state.questions,
        answers=st.session_state.answers
    )

    # Add closing instruction for Maya
    st.session_state.messages.append({
        "role": "system",
        "content": CLOSING_PROMPT
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        temperature=0.7,
        max_tokens=300
    )

    maya_reply = response.choices[0].message.content

    st.session_state.messages.append({
        "role": "assistant",
        "content": maya_reply
    })

    # Mark conversation as ended
    st.session_state.phase = "ended"
    st.session_state.conversation_ended = True

    return maya_reply