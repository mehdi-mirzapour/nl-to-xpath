import json
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from models import model


def extract_json_from_codeblock(output: str) -> dict:
    """Extract and parse JSON from a code block in LLM output."""
    lines = output.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    json_str = "\n".join(lines)
    return json.loads(json_str)


def classify(instructions: str, model) -> dict:
    """Classify natural language instructions into web automation actions using MistralAI."""
    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not set in environment.")
    os.environ["MISTRAL_API_KEY"] = api_key

    prompt_template = """
You are an intelligent instruction classifier.
Your task is to read a long natural language input where each line represents an instruction to be executed in a web automation context.

For each line, classify it as one of the following actions:
   - page.goto
   - page.fill
   - page.click
   - page.hover
   - page.wait
   - browser.close

Output in JSON format:

{{
  "instructions": [
    {{ "original instruction": STRING, "classification": STRING , "waiting_time": Float }},
    ...
  ]
}}

--- Instructions ---
{instructions}
"""

    prompt = PromptTemplate.from_template(prompt_template)

    chain = (
        {"instructions": RunnableLambda(lambda _: instructions)}
        | prompt
        | model
    )

    raw_output = chain.invoke({})
    parsed_output = extract_json_from_codeblock(raw_output.content.strip())
    return parsed_output


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

    output = classify(instruction, model)
    print("\nOriginal Instructions:\n", instruction.strip())
    print("\nStructured Output:\n", json.dumps(output, indent=2))
