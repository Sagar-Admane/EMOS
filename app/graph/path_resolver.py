from pathlib import PurePosixPath
from posixpath import normpath

class PathResolver:

    def resolve_imports(current_file_path: str, import_path:str):
        base_path = str(
            PurePosixPath(current_file_path).parent
        )

        return normpath(
            f"{base_path}/{import_path}"
        )