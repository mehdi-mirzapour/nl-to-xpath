import json
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

{{
  "instructions": [
    {{ "original instruction": STRING, "classification": STRING , "waiting_time": Float}},
    ...
  ]
}}

--- Instructions ---
{instructions}
"""

    prompt = PromptTemplate.from_template(template)
    llm = ChatMistralAI(model="mistral-large-latest", temperature=0)

    chain = (
        {"instructions": RunnableLambda(lambda _: instructions)}
        | prompt
        | llm
    )

    result = chain.invoke({})
    result  extract_json_from_codeblock(result.content.strip())
    result = json.loads(result)
    return result


if __name__ == "__main__":
    instruction = """    
- Navigate to the website: https://app.thundercode.ai
- Enter the username (mehdi@proptexx.com) into the email input field.
- Enter the password (9X4RKrkr9p5e3DH) into the password field.
- Click the "Continue" button to log in.
- Wait for 5 seconds to make sure the login process completes and everything loads properly.
- Manually go to the "Company overview" section by changing the URL to: https://app.thundercode.ai/#/organization/overview
- In the Company Overview form, fill in the "Year Founded" field with the value: 2029.
- Click the "Save" button to store the changes.
- Wait for 5 seconds to let the changes persist.
- Navigate to the "Quality Practices" section via direct URL: https://app.thundercode.ai/#/organization/quality-practices
- Fill the "Other Standards" field with the text: ISO 9001, ISO 27002.
- Click the "Save" button again to confirm this information.
- Wait 1 more second, likely to observe the saved result.
- Close the browser.
    """
    output = process_instruction_with_html(instruction)
    print("NL Instruction:", instruction)
    print("XPath Output:", output)
