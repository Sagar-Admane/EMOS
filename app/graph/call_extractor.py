import ast
import re

class FunctionCallVisitor(ast.NodeVisitor):

    def __init__(self):
        self.calls = []

    def visit_Call(self, node):

        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)

        self.generic_visit(node)


class CallExtractor:

    @staticmethod
    def extract_calls(content: str, language: str):

        if language == "py":
            try:
                tree = ast.parse(content)

            except SyntaxError:
                return {}

            function_calls = {}

            for node in tree.body:

                if not isinstance(node, ast.FunctionDef):
                    continue

                function_name = node.name

                visitor = FunctionCallVisitor()

                visitor.visit(node)

                function_calls[function_name] = visitor.calls

            return function_calls
        
        if language in ["js", "ts", "jsx", "tsx"]:
            return CallExtractor.extract_function_Calls_from_js_ts(content)
        
    def extract_function_Calls_from_js_ts(content: str):

        function_pattern = (
            r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{([\s\S]*?)\}'
        )

        functions = re.findall(
            function_pattern,
            content
        )

        result = {}

        for function_name, body in functions:

            calls = re.findall(
                r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                body
            )

            ignored = {
                "if",
                "for",
                "while",
                "switch",
                "catch"
            }

            result[function_name] = [
                call
                for call in calls
                if call not in ignored
            ]

        return result
    
# content = """
# def login():
#     verify_token()
#     create_session()

# def verify_token():
#     pass

# def create_session():
#     pass
# """

# print(CallExtractor.extract_calls(content))