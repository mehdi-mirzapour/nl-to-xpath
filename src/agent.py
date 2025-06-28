from dotenv import load_dotenv
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# Load environment variables from .env
load_dotenv()

# Read Mistral API key from .env
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY not set in environment.")

# Set the API key for LangChain use
os.environ["MISTRAL_API_KEY"] = api_key

# Load HTML content from a file
with open("resources/test_case_1.html", "r", encoding="utf-8") as f:
    html = f.read()

# Natural language instruction
instruction = "Select the dropdown next to 'Country'"

# Prompt template with embedded HTML and instruction
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

# Use Mistral's largest available hosted model
llm = ChatMistralAI(model="mistral-large-latest", temperature=0)

# LCEL static flow
chain = (
    {"instruction": RunnableLambda(lambda _: instruction), "html": RunnableLambda(lambda _: html)}
    | prompt
    | llm
)

# Execute the flow
result = chain.invoke({})
print("NL Instruction:", instruction)
print("XPath Output:", result.content.strip())
