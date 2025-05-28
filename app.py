import streamlit as st
import random
from services.llm_service import extract_candidate_details
from services.chroma_service import get_resumes_data

st.set_page_config(
    page_title="Resume Analysis",
    layout="wide"
)

st.title("Resume Analysis")

@st.cache_data(ttl=3600)  # For not to fetch data from the database every time streamlit state updates
def get_cached_resumes():
    return get_resumes_data()

@st.cache_data(show_spinner=False)
def get_record_details(content):
    return extract_candidate_details(content)

display_data = get_cached_resumes()
random.shuffle(display_data)

st.write(f"Total Resumes: {len(display_data)}")

if 'records_to_show' not in st.session_state:
    st.session_state.records_to_show = 10

for i, (doc_id, metadata, content) in enumerate(display_data[:st.session_state.records_to_show]):
    details = get_record_details(content)

    with st.expander(f"Candidate {i+1} | Profession: {details.get('profession', 'N/A')} | Experience: {details.get('years_of_experience', 'N/A')} years | Category: {metadata.get('category', 'Unknown')}"):
        st.markdown(
            f"<div style='margin-top:1em; margin-bottom:1em; color:#fff; background:#333; padding:1em; border-radius:8px;'><b>Summary:</b><br>{details.get('summary', 'N/A')}</div>",
            unsafe_allow_html=True
        )

if st.session_state.records_to_show < len(display_data):
    if st.button('Load More'):
        st.session_state.records_to_show += 10
        st.rerun()

