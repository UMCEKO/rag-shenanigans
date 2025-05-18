import psycopg2

from app.core.config import POSTGRES_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

pg_client = psycopg2.connect(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_URL}/{POSTGRES_DB}")


def prep_db():
    cursor = pg_client.cursor()
    cursor.execute("""
    CREATE EXTENSION IF NOT EXISTS vector;
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents(
        id SERIAL PRIMARY KEY,
        name TEXT,
        page_count INTEGER
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pages(
        id SERIAL PRIMARY KEY,
        page_number INTEGER NOT NULL,
        document_id SERIAL REFERENCES documents(id),
        contents TEXT NOT NULL,
        embeddings VECTOR(1536)
    );""")
    pg_client.commit()
    cursor.close()