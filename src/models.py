from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI

from dotenv import load_dotenv
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(model="gpt-4", temperature=0)
# model = ChatMistralAI(model="mistral-large-latest", temperature=0)

