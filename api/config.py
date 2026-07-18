import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Load DB URL and CORS origins from .env
DATABASE_URL = os.getenv("DATABASE_URL")
CORS_ORIGINS_RAW = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_RAW.split(";") if origin.strip()]

# External Data API Base URL
DATA_API_BASE_URL = os.getenv("DATA_API_BASE_URL", "https://scode-api-126204309825.us-central1.run.app")

# Path to the pickle model file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "Notebooks", "decision_tree_scode.pkl")
