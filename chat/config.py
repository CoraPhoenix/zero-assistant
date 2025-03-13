import os
from data.settings import load_secure_json
from dotenv import load_dotenv

load_dotenv()
settings = load_secure_json("data/settings.data")["ai_settings"]

class Config:
    #ai_settings = load_secure_json("data/ai_settings.json")
    HUGGINGFACE_INFERENCE_TOKEN = os.getenv("HUGGINGFACE_INFERENCE_TOKEN")
    API_URL_INSTRUCT = settings["api_url"]
    ZERO_CONTEXT = settings["context"]