class ServiceExtractor:

    @staticmethod
    def extract_service(path: str):

        parts = path.split("/")

        ignored = {
            "controller",
            "controllers",
            "route",
            "routes",
            "middleware",
            "middlewares",
            "config",
            "modals",
            "models",
            "frontend",
            "backend"
        }

        for part in parts:

            if part.lower() not in ignored:
                return part

        return None