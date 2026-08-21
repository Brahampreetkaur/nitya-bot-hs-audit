"""
HS Call Audit Bot — Streamlit app

Paste an HS call transcript in and get the enhanced audit report back (Mode B).
A second tab exposes the unconnected-patient / call-again check (Mode A).

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

Deploy for a shareable link: push this folder to a GitHub repo, then deploy it on
Streamlit Community Cloud (share.streamlit.io). Set your GEMINI_API_KEY in the
app's Secrets (not in this file) so people using the link don't need their own key.
See README.md for the exact steps.
"""

import streamlit as st
from google import genai
from google.genai import types

from system_prompt import SYSTEM_PROMPT_MODE_A, SYSTEM_PROMPT_MODE_B

st.set_page_config(page_title="HS Call Audit Bot", page_icon="🩺", layout="wide")

DEFAULT_MODEL = "gemini-3.5-flash-lite"


def get_api_key() -> str:
    # Prefer a key set in Streamlit secrets (used for the deployed/shared link).
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return st.session_state.get("api_key_input", "")


with st.sidebar:
    st.header("Settings")
    if "GEMINI_API_KEY" in st.secrets:
        st.success("Gemini API key loaded from app secrets.")
    else:
        st.text_input(
            "Gemini API key",
            type="password",
            key="api_key_input",
            help="Get one from Google AI Studio. For the shared deployed link, "
            "set this in Streamlit secrets instead so people don't paste their own.",
        )
    model = st.text_input(
        "Model",
        value=DEFAULT_MODEL,
        help="Check docs.claude.com/en/docs/about-claude/models for the current "
        "model IDs if this default has aged out.",
    )
    st.divider()
    st.caption(
        "This tool assists a human reviewer — treat its output as a draft audit "
        "to check, not a final word."
    )

st.title("🩺 HS Call Audit Bot")

tab_audit, tab_status = st.tabs(["Generate Audit Report", "Call Connection Check"])

# ---------------------------------------------------------------------------
# Tab 1: paste a transcript, get the enhanced audit report
# ---------------------------------------------------------------------------
with tab_audit:
    st.subheader("Paste the HS call transcript")
    transcript = st.text_area(
        "Transcript",
        height=350,
        placeholder="Paste the full call transcript here...",
        key="transcript_input",
    )
    generate = st.button("Generate Enhanced Audit Report", type="primary")

    if generate:
        api_key = get_api_key()
        if not api_key:
            st.error("Add a Gemini API key in the sidebar first.")
        elif not transcript.strip():
            st.error("Paste a transcript first.")
        else:
            with st.spinner("Auditing the call..."):
                try:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=model,
                        contents=(
                            "Here is the HS call transcript. Produce the full "
                            "enhanced audit report as specified.\n\n---\n\n"
                            f"{transcript}"
                        ),
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT_MODE_B,
                            max_output_tokens=4000,
                        ),
                    )
                    st.session_state["last_report"] = response.text
                except Exception as e:
                    st.error(f"Something went wrong calling the model: {e}")

    if st.session_state.get("last_report"):
        st.divider()
        st.markdown(st.session_state["last_report"])
        st.download_button(
            "Download report as Markdown",
            data=st.session_state["last_report"],
            file_name="hs_call_audit_report.md",
            mime="text/markdown",
        )

# ---------------------------------------------------------------------------
# Tab 2: unconnected-patient / call-again check
# ---------------------------------------------------------------------------
with tab_status:
    st.subheader("Check whether a patient is still unconnected")
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient name/ID", key="patient_name_input")
        existing_patient = st.checkbox("Existing patient", value=True, key="existing_patient_input")
    with col2:
        answered = st.selectbox(
            "Was the current attempt answered?",
            ["No / Not attended", "Yes, attended"],
            key="answered_input",
        )
        transcript_available = st.checkbox(
            "Transcript available for this call", key="transcript_available_input"
        )
    check = st.button("Check Status")

    if check:
        api_key = get_api_key()
        if not api_key:
            st.error("Add a Gemini API key in the sidebar first.")
        else:
            with st.spinner("Checking..."):
                try:
                    client = genai.Client(api_key=api_key)
                    situation = (
                        f"Patient: {patient_name or 'unspecified'}\n"
                        f"Existing patient: {existing_patient}\n"
                        f"Current attempt answered: {answered}\n"
                        f"Transcript available: {transcript_available}\n"
                    )
                    response = client.models.generate_content(
                        model=model,
                        contents=situation,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT_MODE_A,
                            max_output_tokens=300,
                        ),
                    )
                    st.code(response.text)
                except Exception as e:
                    st.error(f"Something went wrong calling the model: {e}")