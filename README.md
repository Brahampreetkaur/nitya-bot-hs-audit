# HS Call Audit Bot

A small Streamlit app: paste an HS call transcript in, get the enhanced audit report
back. Built from the requirements worked out in the "Ai bot Enhancement" project —
see `system_prompt.py` for the actual logic (that's the file to edit if the checklist,
Platinum script, or scoring rules change).

## What's in here

- `app.py` — the Streamlit UI (two tabs: generate an audit report from a transcript,
  and check whether an unconnected patient should be called again)
- `system_prompt.py` — the two system prompts (Mode A: connection status / retry
  logic, Mode B: full audit report generation). This is the part that encodes the
  business logic — edit the strings here to tune wording, add checklist parameters,
  or update the Platinum script if it changes.
- `requirements.txt` — Python dependencies
- `.streamlit/secrets.toml.example` — template for where your API key goes

## Run it locally in VS Code

1. Open this folder in VS Code.
2. Create a virtual environment and install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Get an API key from console.anthropic.com, then either:
   - copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste your
     key in there, or
   - just paste the key into the sidebar field when the app is running.
4. Start the app:
   ```
   streamlit run app.py
   ```
   It opens at `http://localhost:8501`.

## Get a shareable link (Streamlit Community Cloud)

1. Push this folder to a GitHub repo (make sure `.streamlit/secrets.toml` is NOT
   committed — the `.gitignore` here already excludes it, only the `.example` file
   should go up).
2. Go to share.streamlit.io, sign in, and click "New app."
3. Point it at your repo, branch, and `app.py`.
4. Before (or after) deploying, open the app's **Settings -> Secrets** and paste in:
   ```
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
   This way whoever uses the deployed link doesn't need their own key — they just
   paste a transcript and click the button.
5. Deploy. You'll get a `*.streamlit.app` URL you can hand to the team.

## Notes

- The model ID in the sidebar defaults to `claude-sonnet-4-5-20250929` — if that's
  aged out by the time you're setting this up, check
  docs.claude.com/en/docs/about-claude/models for the current ID and update the
  default in `app.py` (or just type the new one into the sidebar field).
- This produces a *draft* audit report for a human reviewer to check — it's not
  wired into your call/telephony system, and the Mode A "check again in 2 hours"
  logic doesn't run on a timer by itself; something else (a scheduled job, your
  existing call workflow, etc.) needs to call it again at the right time.
- Treat the Platinum component list and checklist rows in `system_prompt.py` as the
  source of truth to keep updated — if the sales script changes, that's the file to edit.
