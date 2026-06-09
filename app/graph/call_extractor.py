import ast


class FunctionCallVisitor(ast.NodeVisitor):

    def __init__(self):
        self.calls = []

    def visit_Call(self, node):

        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)

        self.generic_visit(node)


class CallExtractor:

    @staticmethod
    def extract_calls(content: str) -> dict[str, list[str]]:

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
    
content = """
def login():
    verify_token()
    create_session()

def verify_token():
    pass

def create_session():
    pass
"""


print(CallExtractor.extract_calls(content))