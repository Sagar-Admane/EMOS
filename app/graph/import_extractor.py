import re
import ast

class ImportExtractor:

    def extract_imports(contents: str, language: str):
        if language == "py":
            return ImportExtractor.extract_python_imports(contents)
        if language in  ["js", "ts", "jsx", "tsx"]:
            return ImportExtractor.extract_js_ts_imports(contents)
        
    def extract_python_imports(content: str):
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        
        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def extract_js_ts_imports(contents: str):
        imports = []

        pattern = r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]'

        matches = re.findall(pattern, contents)

        imports.extend(matches)

        return imports
    
