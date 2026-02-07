import re

def extract_code(text):
    pattern_strict = r"```python\s*(.*?)\s*```"
    match = re.search(pattern_strict, text, re.DOTALL)
    if match:
        return match.group(1)
        
    pattern_loose = r"```\s*(.*?)\s*```"
    match = re.search(pattern_loose, text, re.DOTALL)
    if match:
        return match.group(1)
        
    # Fallback: If no markdown blocks, assume the whole text is code 
    # (but strip thinking process if model is reasoning)
    if "def " in text:
        return text.strip()
        
    return text
