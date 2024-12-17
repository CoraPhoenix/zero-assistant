import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HUGGINGFACE_INFERENCE_TOKEN = os.getenv("HUGGINGFACE_INFERENCE_TOKEN")
    API_URL_CHAT = "https://api-inference.huggingface.co/models/google/flan-t5-base"
    API_URL_INSTRUCT = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
    #ZERO_CONTEXT = "Your name is Zero, and everyone will call you by this name.\n"
    ZERO_CONTEXT = "<|im_start|>system\nYou are a helpful assistant. Your name is Zero, and everyone will call you by this name.<|im_end|>\n"