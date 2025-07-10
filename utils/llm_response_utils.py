import re

def clean_llm_json(raw):
    """
    Cleans LLM output by removing comments (// ...) and extracting the first JSON object found.
    Returns the cleaned JSON string, or None if not found.
    """
    # Remove comments (// ...)
    cleaned = re.sub(r'//.*', '', raw)
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    # Extract the first JSON object
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    return match.group(0) if match else None 