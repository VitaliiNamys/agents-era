from dotenv import load_dotenv
import os

load_dotenv()

DB_PERSIST_DIR = os.path.abspath("./chroma_db")
DB_COLLECTION_NAME = "resumes"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
