import os
from abc import ABC
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class BaseAgent(ABC):
    def __init__(self, model: str):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            max_retries=0,
        )
        self.model = model
