import re
from pathlib import Path
import json

import re

def extract_url(text):
    pattern = r'(https?://[^\s\'"]+|localhost:\d+[^\s\'"]*)'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def load_instructions_from_file(json_path: str):
    """Load instruction data from a JSON file."""
    file_path = Path(json_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {json_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f) 

    return data    