import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# Set your API key
os.environ["MISTRAL_API_KEY"] = "4dVfoQuBXJAe9nsjZnCAXWR8pbGrC5wV"

# Load HTML content from a file
with open("resources/test_case_1.html", "r", encoding="utf-8") as f:
    html = f.read()

# Natural language instruction
instruction = "Select the dropdown next to 'Country'"

# Prompt template with embedded HTML and instruction
template = """You are an expert in converting natural language into XPath.

You will be given:
- An HTML page (as a string)
- A natural language instruction

Based on the HTML structure, return the most accurate XPath that can fulfill the instruction.

Respond with ONLY the XPath string — no explanations.

HTML:
{html}

Instruction:
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
