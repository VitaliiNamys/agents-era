import json
from llama_index.llms.openai import OpenAI

from config import OPENAI_API_KEY

llm = OpenAI(
    model="gpt-3.5-turbo",
    api_key=OPENAI_API_KEY
)

def extract_candidate_details(resume_text: str) -> dict:
    prompt = (
        "Extract the following details from the candidate's resume. "
        "In the summary, include candidate's strongest skills and professional highlights"
        "Return as JSON with keys: profession, years_of_experience, summary.\n"
        "Resume:\n" + resume_text
    )
    try:
        response = llm.complete(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(e)
        return {"profession": "N/A", "years_of_experience": "N/A", "summary": "N/A"}