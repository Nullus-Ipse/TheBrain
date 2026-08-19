"""
app.py

Entry point. Kept intentionally tiny — all real work happens in
core/ (decides outcomes, talks to Gemini) and ui/ (performs it).
Run with: streamlit run app.py
"""

from ui.page import render_page

render_page()
