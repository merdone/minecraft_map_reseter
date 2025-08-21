def parse_quoted_args(text: str):
    parts = []
    current = []
    in_quotes = False
    for char in text:
        if char == '"':
            in_quotes = not in_quotes
            if not in_quotes:
                parts.append("".join(current).strip())
                current = []
        else:
            if in_quotes:
                current.append(char)
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None