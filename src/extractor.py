
import json
from dotenv import load_dotenv
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from models import model

def extract_json_from_codeblock(output: str) -> str:
    """Remove code block markdown from model output."""
    lines = output.strip().splitlines()
    if lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines)

def extract_xpath_pattern(instruction: str, html: str, model) -> str:
    """Run the instruction + HTML through Mistral and return JSON result."""
    # Load environment variables
    load_dotenv()
        
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not set in environment.")
    os.environ["MISTRAL_API_KEY"] = api_key

    # Prompt template
    template = """
You are an expert UI assistant that converts natural language commands into web automation step.

You will be given:
- A web page's full HTML
- A natural language instruction from the user

Your job:
- Translate the instruction into one step, each using an action from only both category: "click", "fill" all lowercase.
- Always use "click" for dropdown toggles (e.g., class includes `w-dropdown-toggle`)
- XPaths must be **valid XPath 1.0** and use `//` syntax where needed.
- The output must be ONLY valid JSON (no text or explanation), following this format:

Example 1:
{{"action": "click", "xpath": "//input[@id='username']", fill="username/password"}}

Example 2:
{{"action": "click", "xpath": "//a[contains(text(), 'AI-Powered Widget')]", fill=""}}


--- Page HTML ---
{html}

--- Command ---
{instruction}
"""
    prompt = PromptTemplate.from_template(template)    
    chain = (
        {"instruction": RunnableLambda(lambda _: instruction), "html": RunnableLambda(lambda _: html)}
        | prompt
        | model
    )

    result = chain.invoke({})
    result = extract_json_from_codeblock(result.content.strip())
    if isinstance(result, str):
        result = json.loads(result)
        
    print("JSON Result:", result)
    return result

if __name__ == "__main__":
    instruction = "Click on the 'Login' button."
    with open("resources/test_case_3.html", "r", encoding="utf-8") as f:
        html =f.read()

    output = extract_xpath_pattern(instruction, html, model)
    print("NL Instruction:", instruction)
    print("XPath Output:", output)
