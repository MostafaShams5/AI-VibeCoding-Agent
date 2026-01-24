import re

def extract_code(text):
    pattern = r"```python\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    if "def " in text:
        return text
    return text
