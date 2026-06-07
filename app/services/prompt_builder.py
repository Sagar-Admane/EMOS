class PromptBuilder:

    @staticmethod
    def build(query: str, chunks: list):
        context = ""

        for chunk in chunks:
            context+=f"""
File: {chunk["path"]}
Lines: {chunk["start_line"]}-{chunk["end_line"]}

Code: {chunk["text"]}

--------------------------------------------------
"""

        prompt = f"""
You are a senior software engineer.

Answer the question using ONLY the provided code context.

Question:
{query}

Code Context:
{context}

Instructions:
- Be precise.
- Mention relevant files.
- Mention important functions.
- If information is not present, say so.

Answer:
"""

        return prompt