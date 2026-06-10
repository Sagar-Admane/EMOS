class DatabaseExtractor:

    def extract_database(contents: str):
        content = contents.lower()

        if "mongoose.connect" in content:
            return "MongoDB"
        
        if "mongodb" in content:
            return "MongoDB"
        
        if "prismaclient" in content:
            return "Prisma"
        
        if "create_engine" in content:
            return "PostgreSQL"

        if "psycopg2" in content:
            return "PostgreSQL"

        if "sqlite3" in content:
            return "SQLite"
        
        return None