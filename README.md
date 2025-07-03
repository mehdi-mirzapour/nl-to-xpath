# NL-to-XPath Project

A prototype converter that transforms natural language commands (e.g., *"Click on 'About Us'"*) into precise XPath expressions. This project is built to support **AI-powered test automation platform** using LangChain and Mistral’s `mistral-large-latest` and OpenAI's `chatgpt-4` models.

---

## Features

- Converts natural language UI instructions into XPath selectors.
- Integrates with Playwright for automating web UI testing.
- Built on top of LangChain and LLMs models.

---

## Requirements

- Python 3.11.13 (or any Python 3.11+ version)
- A `.env` file with your API keys and configurations.
- - The test cases are designed for use with the [`full-stack-fastapi-template`](https://github.com/fastapi/full-stack-fastapi-template.git) repository. It is recommended to clone and install this project to properly run the test cases located in the `resources/test_cases/*.txt` directory.

---

## Setup Instructions

1. **Create and activate a Python environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate   # Windows
   ```

2. **Create a `.env` file** in the root of your project directory and add the following content with your **real API keys**:

   ```env
   MAX_TOKEN_LIMITATION=128000

   OPENAI_API_KEY=sk-your-real-openai-api-key-here
   MISTRAL_API_KEY=your-real-mistral-api-key-here

   PINECONE_API_KEY=your-real-pinecone-api-key-here
   PINECONE_INDEX_NAME=thundercode
   ```

   > **Important:**  
   > - Replace the placeholder values with your actual API keys.  
   > - Keep this file **private** and **do not** commit it to any public repository.  
   

3. **Install dependencies** (if applicable):

   ```bash
   pip install -r requirements.txt
   ```
   Don't forget to

   ```bash
   playwright install
   ```

4. **Run the application** with your input file:

   ```bash
   python src/agentic_app.py path/to/your/input_file.txt
   ```

---

## Notes

- Tested on Python 3.11.13, but should work on any Python 3.11+ version.
- Ensure your API keys have the proper permissions.
- Adjust `MAX_TOKEN_LIMITATION` according to your usage and API limits.

---

## Contributing & Issues

If you encounter any issues or want to contribute, please open an issue or submit a pull request!

---

Thank you for using NL-to-XPath Project!