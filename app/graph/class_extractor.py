import ast
import re

class ClassExtractor:

    @staticmethod
    def extract_classes(content: str, language: str):

        if language == "py":

            try:
                tree = ast.parse(content)

                return [
                    node.name
                    for node in tree.body
                    if isinstance(node, ast.ClassDef)
                ]

            except SyntaxError:
                return []

        if language in ["js", "ts", "jsx", "tsx"]:

            pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)'

            return re.findall(
                pattern,
                content
            )

        return []