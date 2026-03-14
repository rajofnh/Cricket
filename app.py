import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai

# --- CONFIGURATION ---
## GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
## CRICKET_API_KEY = "YOUR_CRICKET_DATA_API_KEY"

GEMINI_API_KEY = st.secrets["gemini_api_key"]
CRICKET_API_KEY = st.secrets["cricket_api_key"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview') # Updated model ID

# --- UI STYLING ---
st.set_page_config(page_title="AI Cricket Strategy Suite", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; border-radius: 10px; padding: 15px; border: 1px solid #4B5563; }
    .audit-box { padding: 20px; border-radius: 10px; margin-top: 20px; }
    .green-flag { background-color: #064e3b; border: 1px solid #10b981; color: #34d399; }
    .red-flag { background-color: #7f1d1d; border: 1px solid #ef4444; color: #f87171; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA AGENT ---
def get_match_history(team_name):
    """
    Mocking data retrieval for demonstration. 
    In production, use: requests.get(f"https://api.cricapi.com/v1/series?apikey={CRICKET_API_KEY}")
    """
    # Simulated last 5 matches: W=Win, L=Loss
    data = {
        "India": ["W", "W", "L", "W", "W"],
        "Australia": ["L", "W", "W", "L", "W"],
        "England": ["L", "L", "W", "L", "L"],
        "Pakistan": ["W", "L", "L", "W", "L"]
    }
    return data.get(team_name, ["L", "L", "L", "L", "L"])

# --- ANALYST AGENT ---
def analyst_agent(team1, team2, h1, h2):
    t1_wins = h1.count("W")
    t2_wins = h2.count("W")
    
    prompt = f"""
    Analyze a cricket match between {team1} and {team2}.
    {team1} last 5 matches: {h1} ({t1_wins} wins)
    {team2} last 5 matches: {h2} ({t2_wins} wins)
    
    1. Predict winning probability (%) for both.
    2. Provide a 2-sentence tactical reason.
    3. Suggest 3 specific steps for the losing team to pivot.
    """
    response = model.generate_content(prompt)
    return response.text

# --- AUDITOR AGENT ---
def auditor_agent(analyst_output, raw_data):
    prompt = f"""
    You are an Audit AI. Check if the Analyst Hallucinated.
    RAW DATA: {raw_data}
    ANALYST OUTPUT: {analyst_output}
    
    If the Analyst mentioned match results NOT in the raw data, it's a hallucination.
    Return ONLY 'PASS' or 'FAIL' followed by a brief reason.
    """
    response = model.generate_content(prompt)
    return response.text

# --- MAIN UI ---
st.title("🏏 AI Cricket Strategy & Audit Suite")
st.subheader("Predictive Analytics & Integrity Verification")

col1, col2 = st.columns(2)
with col1:
    t1 = st.selectbox("Select Team 1", ["India", "Australia", "England", "Pakistan"])
with col2:
    t2 = st.selectbox("Select Team 2", ["Australia", "India", "England", "Pakistan"])

if st.button("Run AI Analysis"):
    h1 = get_match_history(t1)
    h2 = get_match_history(t2)
    
    # Run Agent 1
    with st.spinner("Analyst Agent thinking..."):
        analysis = analyst_agent(t1, t2, h1, h2)
    
    # Display Stats
    c1, c2 = st.columns(2)
    c1.metric(f"{t1} Form (Last 5)", f"{h1.count('W')}- {h1.count('L')}")
    c2.metric(f"{t2} Form (Last 5)", f"{h2.count('W')}- {h2.count('L')}")
    
    st.markdown("### 📊 Strategic Forecast")
    st.write(analysis)
    
    # Run Agent 2 (Audit)
    st.divider()
    with st.spinner("Auditor Agent verifying facts..."):
        raw_context = f"{t1}: {h1}, {t2}: {h2}"
        audit_results = auditor_agent(analysis, raw_context)
    
    is_hallucinated = "FAIL" in audit_results.upper()
    flag_class = "red-flag" if is_hallucinated else "green-flag"
    flag_text = "🚩 HALLUCINATION DETECTED" if is_hallucinated else "✅ AUTHENTIC DATA"
    
    st.markdown(f"""
        <div class="audit-box {flag_class}">
            <h4>{flag_text}</h4>
            <p>{audit_results}</p>
        </div>
    """, unsafe_allow_html=True)
