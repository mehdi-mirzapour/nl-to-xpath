import json
from dotenv import load_dotenv
import os
from models import model
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from prompt import PROMPT


def extract_json_from_codeblock(output: str) -> str:
    """Remove code block markdown from model output."""
    lines = output.strip().splitlines()
    if lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    json_str = "\n".join(lines)
    return json.loads(json_str)

def segment(instructions: str, model) -> str:
    """Convert NL input into line-by-line web automation steps using OpenAI."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment.")
    os.environ["OPENAI_API_KEY"] = api_key

    template = PROMPT

    prompt = PromptTemplate.from_template(template)

    chain = (
        {"instructions": RunnableLambda(lambda _: instructions)}
        | prompt
        | model
    )

    result = chain.invoke({})
    result = extract_json_from_codeblock(result.content.strip())
    return result


if __name__ == "__main__":
    instruction = """
open localhost:5173 and then login with user name as `mehdi.mirzapour@gmail.com` and password  as `pass1234`
open localhost:5173/items and click on add items.
"""
    output = segment(instruction, model)
    print("\nOriginal Instruction:\n", instruction.strip())
    print("\nStep-by-step Output:\n", output)
