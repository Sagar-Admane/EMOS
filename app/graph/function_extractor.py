import ast
import re

class FunctionExtractor:
    @staticmethod
    def extract_functions(contents: str, language: str):
        if language == "py":
            return FunctionExtractor.extract_python_function(contents)
        if language == "js" or language == "ts":
            return FunctionExtractor.extract_js_ts_functions(contents)
    
    @staticmethod
    def extract_python_function(contents: str):
        try:
            tree = ast.parse(contents)
        except SyntaxError:
            return []

        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        return functions
    
    @staticmethod
    def extract_js_ts_functions(contents: str):
        patterns = [
            r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'async\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        ]
        
        functions = []

        for pattern in patterns:
            functions.extend(re.findall(pattern, contents))

        return list(set(functions))