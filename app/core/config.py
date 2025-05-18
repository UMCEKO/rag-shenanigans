import os

import dotenv


dotenv.load_dotenv()

# Non-used for now

PORT = int(os.getenv("PORT", "3000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Postgres that supports vector extension

POSTGRES_URL = os.getenv("POSTGRES_URL")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Openai API Key

OPENAI_KEY = os.getenv("OPENAI_API_KEY")