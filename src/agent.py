from dotenv import load_dotenv
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

def extract_json_from_codeblock(output: str) -> str:
    """Remove code block markdown from model output."""
    lines = output.strip().splitlines()
    if lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines)

def process_instruction_with_html(instruction: str, html: str) -> str:
    """Run the instruction + HTML through Mistral and return JSON result."""
    # Load environment variables
    load_dotenv()

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not set in environment.")
    os.environ["MISTRAL_API_KEY"] = api_key

    # Prompt template
    template = """
You are an expert UI assistant that converts natural language commands into web automation steps.

You will be given:
- A web page's full HTML
- A natural language instruction from the user

Your job:
- Translate the instruction into 1 or more steps, each using an action from: "click", "hover", "scroll" — all lowercase.
- Always use "click" for dropdown toggles (e.g., class includes `w-dropdown-toggle`) — never "hover" for those.
- XPaths must be **valid XPath 1.0** and use `//` syntax where needed.
- The output must be ONLY valid JSON (no text or explanation), following this format:

{{
  "steps": [
    {{"action": "click", "xpath": "//div[@id='w-dropdown-toggle-0']"}},
    {{"action": "click", "xpath": "//a[contains(text(), 'AI-Powered Widget')]"}}
  ]
}}

--- Page HTML ---
{html}

--- Command ---
{instruction}
"""
    prompt = PromptTemplate.from_template(template)
    llm = ChatMistralAI(model="mistral-large-latest", temperature=0)

    chain = (
        {"instruction": RunnableLambda(lambda _: instruction), "html": RunnableLambda(lambda _: html)}
        | prompt
        | llm
    )

    result = chain.invoke({})
    return extract_json_from_codeblock(result.content.strip())

if __name__ == "__main__":
    instruction = "Select the dropdown next to 'Country'"
    with open("resources/test_case_1.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    output = process_instruction_with_html(instruction, html)
    print("NL Instruction:", instruction)
    print("XPath Output:", output)
