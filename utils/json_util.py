import json
import re

def sanitize_and_validate_json(json_data, return_string=False):
    """
    Sanitizes and validates JSON data, handling Python-specific issues
    like single quotes, tuples, and sets.

    Args:
        json_data: The JSON data (string, dict, or list).
        return_string: If True, return a JSON string. If False (default),
                       return the sanitized Python object.

    Returns:
        The sanitized JSON data (as a Python object or string), or None if invalid.
    """

    def _sanitize_string(text):
        if not isinstance(text, str):
            return text

        text = re.sub(r'[\x00-\x1f\x7f]', '', text)

        replacements = {
            '\\': '\\\\',
            '"': '\\"',
            '\b': '\\b',
            '\f': '\\f',
            '\n': '\\n',
            '\r': '\\r',
            '\t': '\\t',
            "'": '\\"',
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    def _recursive_sanitize(data):
        if isinstance(data, dict):
            return {k: _recursive_sanitize(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [_recursive_sanitize(item) for item in data]
        elif isinstance(data, tuple):
            return [_recursive_sanitize(item) for item in data]
        elif isinstance(data, set):
            return [_recursive_sanitize(item) for item in data]
        elif isinstance(data, str):
            return _sanitize_string(data)
        else:
            return data


    if isinstance(json_data, str):
        sanitized_string = _sanitize_string(json_data)
        try:
            parsed_json = json.loads(sanitized_string)
        except json.JSONDecodeError as e:
            print(f"JSON validation failed: {e}")
            return None
    elif isinstance(json_data, (dict, list, tuple, set)):
        parsed_json = _recursive_sanitize(json_data)
    else:
        print(f"Invalid input type: {type(json_data)}.")
        return None

    sanitized_json = _recursive_sanitize(parsed_json)

    try:

        json_string = json.dumps(sanitized_json)
    except (TypeError, ValueError) as e:
        print(f"Final JSON validation failed: {e}")
        return None

    if return_string:
        return json_string
    else:
        return sanitized_json

def merge_json_recursive(base, update):
    """Recursively merge two JSON-like objects.
    - Dictionaries are merged recursively
    - Lists are concatenated
    - Other types are overwritten by the update value

    Args:
        base: Base JSON-like object
        update: Update JSON-like object to merge into base

    Returns:
        Merged JSON-like object
    """
    if not isinstance(base, dict) or not isinstance(update, dict):
        if isinstance(base, list) and isinstance(update, list):
            return base + update
        return update

    merged = base.copy()
    for key, value in update.items():
        if key in merged:
            merged[key] = merge_json_recursive(merged[key], value)
        else:
            merged[key] = value

    return merged
