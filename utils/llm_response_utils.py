import re
import json
import logging

def clean_llm_json(raw):
    """
    Cleans LLM output by removing comments (// ...) and extracting the first valid JSON object found.
    Returns the cleaned JSON string, or None if not found.
    """
    if not raw:
        return None
    
    # Remove comments (// ...)
    cleaned = re.sub(r'//.*', '', raw)
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Try to find the first complete JSON object using a non-greedy approach
    # Look for balanced braces starting from the first '{'
    start_index = cleaned.find('{')
    if start_index == -1:
        logging.info("No opening brace found")
        return None
    
    # Find the matching closing brace
    brace_count = 0
    end_index = start_index
    
    for i in range(start_index, len(cleaned)):
        if cleaned[i] == '{':
            brace_count += 1
        elif cleaned[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_index = i
                break
    
    if brace_count != 0:
        # Braces are not balanced, try a more sophisticated regex as fallback
        # Look for JSON objects that may contain nested structures
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                # Try to parse the matched JSON
                potential_json = match.group(0)
                json.loads(potential_json)
                return potential_json
            except json.JSONDecodeError:
                pass
        
        # If no complete JSON found, try to find incomplete JSON and fix it
        incomplete_match = re.search(r'\{.*', cleaned, re.DOTALL)
        if incomplete_match:
            incomplete_json = incomplete_match.group(0)
            # Try to fix by adding missing braces
            if incomplete_json.count('{') > incomplete_json.count('}'):
                fixed_json = incomplete_json + '}' * (incomplete_json.count('{') - incomplete_json.count('}'))
                try:
                    json.loads(fixed_json)
                    return fixed_json
                except json.JSONDecodeError:
                    pass
        
        return None
    
    # Extract the JSON object
    json_str = cleaned[start_index:end_index + 1]
    
    # Validate that it's proper JSON
    try:
        json.loads(json_str)
        return json_str
    except json.JSONDecodeError:
        # If it's not valid JSON, try to find any JSON object including nested ones
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                potential_json = match.group(0)
                json.loads(potential_json)
                return potential_json
            except json.JSONDecodeError:
                pass
        
        # If still no valid JSON, try to fix common issues like missing closing brace
        if cleaned.count('{') > cleaned.count('}'):
            # Missing closing braces, try to add them
            potential_fix = cleaned + '}' * (cleaned.count('{') - cleaned.count('}'))
            try:
                json.loads(potential_fix)
                return potential_fix
            except json.JSONDecodeError:
                pass
        
        # As a last resort, try to extract a valid JSON structure from what we have
        # Look for patterns like {"key": ["value"]} even if incomplete
        if '"stocks"' in cleaned and '"cryptos"' in cleaned:
            # This looks like a financial response, try to construct valid JSON
            # Use a more robust regex that handles nested brackets
            stocks_match = re.search(r'"stocks":\s*\[[^\]]*(?:\[[^\]]*\][^\]]*)*\]', cleaned)
            cryptos_match = re.search(r'"cryptos":\s*\[[^\]]*(?:\[[^\]]*\][^\]]*)*\]', cleaned)
            
            if stocks_match and cryptos_match:
                potential_json = "{" + stocks_match.group(0) + "," + cryptos_match.group(0) + "}"
                try:
                    json.loads(potential_json)
                    return potential_json
                except json.JSONDecodeError:
                    pass
            
            # If the above fails, try a simpler approach - just find the arrays
            stocks_simple = re.search(r'"stocks":\s*\[[^]]*\]', cleaned)
            cryptos_simple = re.search(r'"cryptos":\s*\[[^]]*\]', cleaned)
            
            if stocks_simple and cryptos_simple:
                potential_json = "{" + stocks_simple.group(0) + "," + cryptos_simple.group(0) + "}"
                try:
                    json.loads(potential_json)
                    return potential_json
                except json.JSONDecodeError:
                    pass
        
        return None

def extract_json_from_streaming_response(response_lines):
    """
    Extract JSON from streaming response lines (like from Ollama).
    Returns concatenated response text and extracted JSON.
    """
    response_text = ""
    
    # First, try to handle the case where the entire response is a single JSON object
    if len(response_lines) == 1:
        try:
            # Try to parse as a single JSON object (non-streaming response)
            obj = json.loads(response_lines[0])
            if 'response' in obj:
                response_text = obj['response']
            else:
                # If it's not a streaming format, treat the entire response as text
                response_text = response_lines[0]
        except json.JSONDecodeError:
            # If it's not valid JSON, treat it as raw text
            response_text = response_lines[0]
    else:
        # Handle streaming response format (multiple lines)
        for line in response_lines:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                if 'response' in obj:
                    response_text += obj['response']
                elif 'content' in obj:
                    # Alternative field name used by some models
                    response_text += obj['content']
            except json.JSONDecodeError:
                # If line is not valid JSON, append it as text
                response_text += line
    
    # Clean up the response text by removing extra whitespace
    response_text = response_text.strip()
    
    # Try to extract JSON from the concatenated response
    json_result = clean_llm_json(response_text)
    
    return response_text, json_result

def validate_and_parse_json(json_str):
    """
    Validate and parse JSON string, returning parsed object or None.
    """
    if not json_str:
        return None
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON: {e}")
        return None 