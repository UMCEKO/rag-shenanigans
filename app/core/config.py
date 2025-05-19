import os

import dotenv

dotenv.load_dotenv()

# Postgres that supports vector extension

POSTGRES_URL = os.getenv("POSTGRES_URL")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Openai API Key

OPENAI_KEY = os.getenv("OPENAI_API_KEY")