# Maya — TalentScout Hiring Assistant

> An intelligent AI-powered hiring assistant that conducts initial candidate screenings for TalentScout, a fictional technology recruitment agency. Maya collects candidate information conversationally, validates inputs, and conducts a structured technical interview tailored to each candidate's declared tech stack.

## 🚀 Live Demo

[https://maya-hiring-assistant-952638576426.asia-south1.run.app](https://maya-hiring-assistant-952638576426.asia-south1.run.app)

---

## Project Overview

Maya is a conversational hiring assistant built for TalentScout's candidate screening pipeline. Instead of static forms, Maya conducts a natural, flowing conversation that collects candidate information and dynamically generates technical interview questions based on the candidate's declared tech stack.

Maya is strictly purpose-bound — she will not deviate from her screening role regardless of what the candidate says, ensuring consistent and professional screening sessions every time. The system supports multilingual interactions, experience-adjusted question difficulty, and local candidate record storage.

**Key Capabilities:**
- Conversational collection of candidate details, one at a time
- Dynamic generation of 5–7 tailored technical questions based on tech stack
- One-by-one question delivery for a real interview experience
- Multilingual support — detects and matches candidate's preferred language
- Strict on-topic guardrails
- Full session record saved to local JSON upon screening completion

---

## Installation Instructions

### Prerequisites

- Python 3.9 or higher
- An OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/edwinthoma/Maya-HiringAssistant.git
cd Maya-HiringAssistant
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

You should see `(venv)` in your terminal prompt confirming the environment is active.

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Your API Key

Create a `.env` file in the project root and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 5 — Run the Application

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## Usage Guide

1. **Launch the app** — Maya greets you and asks for your language preference
2. **Choose your language** — Continue in English or state your preferred language. Maya will continue in that language for the rest of the session
3. **Answer Maya's questions** — She collects your information one field at a time:
   - Full Name
   - Email Address
   - Phone Number
   - Years of Experience
   - Desired Position(s)
   - Current Location
   - Tech Stack (programming languages, frameworks, databases, tools, cloud platforms)
4. **Technical Interview** — Once all information is collected, Maya presents 5–7 technical questions one at a time based on your declared stack and experience level
5. **Completion** — After all questions are answered, Maya closes the session and your full record is saved locally
6. **New Session** — Click "Start New Session" to reset and begin a fresh screening

To end the conversation early at any point, type `exit`, `quit`, or `bye`.

---

## Technical Details

### Libraries Used

| Library | Version | Purpose |
|---|---|---|
| `streamlit` | 1.56.0 | Frontend UI and chat interface |
| `openai` | Latest | GPT-4o-mini API calls |
| `python-dotenv` | Latest | Secure API key loading from .env |
| `json` | Built-in | Candidate record storage and prompt response parsing |
| `uuid` | Built-in | Unique session ID generation |
| `re` | Built-in | JSON extraction from LLM responses |

### Model Details

- **Model:** `gpt-4o-mini`
- **Provider:** OpenAI
- **Temperature:** `0.7` for conversational responses, `0.0` for structured JSON extraction
- **Max Tokens:** `200–1000` depending on the task (greeting, extraction, question generation)

### Project Structure

```
maya-of-house-talentscout/
│
├── app.py              # Main Streamlit application — UI and phase routing
├── maya.py             # Core conversation engine — OpenAI calls and session logic
├── prompts.py          # All prompt templates centralized in one place
├── storage.py          # Data persistence — saves candidate records to JSON
├── requirements.txt    # Project dependencies
├── .env                # API key storage 
├── .gitignore          
└── README.md           # Project documentation
```

### Architectural Decisions

**Single LLM with Phase-Based Routing**

Maya uses a single LLM with application-layer phase routing rather than multiple specialized sub-agents. The candidate screening flow is strictly sequential — information gathering must complete before questioning begins.

**Stateful Conversation via Streamlit Session State**

Streamlit reruns the entire script on every user interaction. `st.session_state` is used to persist conversation history, candidate information, phase tracking, question lists, and answer records across reruns. The full conversation history is sent to OpenAI on every API call since the model has no memory between requests.

**Separate Extraction API Call**

A dedicated silent API call runs after every candidate message during the gathering phase. It reads the conversation transcript and returns structured JSON with whatever candidate fields have been mentioned. This runs at `temperature=0` for deterministic output and is never shown to the candidate. This approach is more reliable than regex parsing of conversational text.

**JSON Local Storage **

Candidate records are saved to a local `candidates.json` file. All storage logic is isolated in `storage.py`

---

## Prompt Design

All prompts are centralized in `prompts.py`. This means Maya's behavior can be modified entirely without touching application logic.

### SYSTEM_PROMPT
The master prompt that defines Maya's identity, rules, and behavior for the entire session. Key design decisions:

- **Role-locking** — Maya is given a tightly scoped identity with an explicit sole purpose statement. This overrides the model's general-purpose helpfulness tendency.
- **Sequential collection** — Fields are listed in order with an explicit "one at a time" instruction preventing Maya from asking multiple questions in one message.
- **Silent validation** — Validation rules use the phrase "silently re-ask if invalid, never mention this rule to the candidate" so constraints are enforced without feeling robotic to the candidate.
- **Scripted guardrail redirect** — Maya is given an exact redirect pattern for off-topic inputs ensuring consistent, professional deflection every time.
- **Experience-adjusted difficulty** — Three difficulty tiers (0–2 years, 2–5 years, 5+ years) are defined directly in the prompt so question generation automatically scales without extra code.
- **Multilingual detection** — A single instruction handles the entire multilingual feature by telling Maya to detect and match the candidate's language after the initial language preference question.

### EXTRACTION_PROMPT
Used in a silent background API call after every candidate message during the gathering phase. Designed to return strict JSON only with no explanation and no markdown so the output can be reliably parsed. Runs at `temperature=0` for deterministic output. Returns `null` for any field not yet mentioned — never infers or guesses values.

### QUESTION_GENERATION_PROMPT
Generates exactly 5–7 questions total across all technologies. Explicitly instructs the model not to generate questions per technology separately, preventing question overload. Prohibits generic questions. Returns a JSON array for reliable parsing and indexed storage.

### INTERVIEW_INTRO_PROMPT
Delivered once when transitioning from gathering to questioning phase. Uses a `{first_question}` placeholder injected at runtime so Maya's warm intro flows naturally into the first question without an awkward break.

### NEXT_QUESTION_PROMPT
Handles the transition between questions. Instructs Maya to acknowledge the previous answer briefly and warmly in one sentence without evaluating or judging it, then present the next question. A hard 2–3 sentence limit keeps the interview moving efficiently.

### CLOSING_PROMPT
Final prompt delivered after the last question is answered. Closes the session warmly and professionally without asking further questions. Informs the candidate of next steps and expected response timeline.

---
## Deployment

Maya is deployed on Google Cloud Run using Cloud Build for containerization.

### Infrastructure
| Component | Service |
|---|---|
| Container Registry | Google Artifact Registry |
| Container Build | Google Cloud Build |
| Deployment | Google Cloud Run (asia-south1) |
| Database | Google Firestore (asia-south2) |
| GCP Project | maya-hiringassistant |

### Deploy Your Own Instance

Make sure you have gcloud CLI installed and authenticated, then run:

```bash
gcloud run deploy maya-hiring-assistant \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_openai_key_here
```

### Architecture Note
On Cloud Run, Firebase credentials are not required . GCP authenticates automatically via the attached service account. The GOOGLE_APPLICATION_CREDENTIALS environment variable is only set when running locally.

---

## Challenges & Solutions

**Challenge 1 — Streamlit Script Rerun Causing State Loss**

Streamlit reruns the entire Python script on every user interaction, resetting all variables. Early versions of the app lost conversation history on every message.

*Solution:* All state — conversation history, candidate info, phase, questions, answers — is stored in `st.session_state` with `if not in` guards that prevent reinitialization on reruns. This is the foundation the entire application is built on.

**Challenge 2 — Tech Stack Phase Transition Firing Too Early**

After the candidate provided their tech stack, the app was immediately triggering question generation in the same Streamlit rerun before the candidate could see Maya's acknowledgment message.

*Solution:* After `update_candidate_info()` confirms all fields are complete, the app sets the phase to `"questioning"` and calls `st.rerun()` instead of directly calling `start_interview()`. On the next rerun with `user_input` being `None`, the questioning phase entry block fires cleanly and visibly.

**Challenge 3 — Opening Greeting Appearing as User Message**

The initial trigger used to start Maya's greeting was being appended to conversation history as a user message, causing it to render as a candidate chat bubble on screen.

*Solution:* A dedicated `get_opening_greeting()` function was created that injects a temporary system instruction without appending a user turn to the history. Only Maya's greeting response is appended, keeping the conversation history clean.

**Challenge 4 — Prompt Instructions Leaking into Maya's Questions**

When validation rules were written in parentheses next to field names in the system prompt, Maya was reading them aloud to candidates — for example saying "please make sure your name contains only alphabets."

*Solution:* Validation instructions were rewritten using the phrase "silently re-ask if invalid, never mention this rule to the candidate." This separates the enforcement instruction from Maya's conversational behavior entirely.

