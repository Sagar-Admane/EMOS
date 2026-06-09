import ast

class FunctionExtractor:
    @staticmethod
    def extract_functions(contents: str):
        try:
            tree = ast.parse(contents)
        except SyntaxError:
            return []
        
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        return functions
    
content = """
def login():
    pass

def logout():
    pass
"""

functions = FunctionExtractor.extract_functions(content)

print(functions)