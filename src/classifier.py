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

def process_instruction_with_html(instructions: str) -> str:
    """Run the instruction + HTML through Mistral and return JSON result."""
    # Load environment variables
    load_dotenv()

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not set in environment.")
    os.environ["MISTRAL_API_KEY"] = api_key

    # Prompt template
    template = """
You are an intelligent instruction classifier.
Your task is to read a long natural language input where each line represents an instruction to be executed in a web automation context.

For each line, classify it as one of the following actions:
   - page.goto
   - page.fill
   - page.click
   - page.wait
   - browser.close


Output in JSON format:

{
  "instructions": [
    { "original instruction": STRING, "classification": STRING },
    ...
  ]
}

--- Instructions ---
{instructions}
"""
    prompt = PromptTemplate.from_template(template)
    llm = ChatMistralAI(model="mistral-large-latest", temperature=0)

    chain = (
        {"instructions": RunnableLambda(lambda _: instructions), "html": RunnableLambda(lambda _: html)}
        | prompt
        | llm
    )

    result = chain.invoke({})
    return extract_json_from_codeblock(result.content.strip())

if __name__ == "__main__":
    instruction = "Click on 'Integrations'"
    with open("resources/test_case_1.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    output = process_instruction_with_html(instruction, html)
    print("NL Instruction:", instruction)
    print("XPath Output:", output)
