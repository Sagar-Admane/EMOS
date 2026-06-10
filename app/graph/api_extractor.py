import re

class APIExtractor:
    
    def extract_apis(content: str):
        pattern = (
            r'(?:router|app)\.'
            r'(get|post|put|delete|patch)'
            r'\s*\('
            r'\s*[\'"]([^\'"]+)[\'"]'
            r'\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)'
        )

        matches = re.findall(
            pattern,
            content,
            re.IGNORECASE
        )

        apis = []

        for method, path, handler in matches:

            apis.append({
                "method": method.upper(),
                "path": path,
                "handler": handler
            })

        return apis