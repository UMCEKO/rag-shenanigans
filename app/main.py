import os.path
import sys

import openai
import pymupdf

from app.core.postgres import prep_db, pg_client
from app.utils.embedding import batch_for_embeddings, convert_batches_to_embedding, apply_embedded_document_to_db
from app.utils.parse_pdf import parse_pdf

MAX_HISTORY = 10

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py embed <path/to/file.pdf>")
        print("  python main.py chat")
        sys.exit(1)

    print("Preparing database...")
    prep_db()

    mode = sys.argv[1].lower()

    valid_modes = ["embed", "chat"]

    if mode not in valid_modes:
        print(f"Invalid mode. Available modes: {", ".join(valid_modes)} ")
        exit(1)

    if mode == "embed":
        target_pdf_path = sys.argv[2]
        if not os.path.exists(target_pdf_path):
            raise Exception("The pdf file was not found.")
        pdf = pymupdf.open(target_pdf_path)
        doc_details = parse_pdf(pdf)
        batched_docs = batch_for_embeddings(doc_details)
        embedded_doc = convert_batches_to_embedding(batched_docs)
        apply_embedded_document_to_db(embedded_doc)
        print(f"Successfully parsed and inserted {len(doc_details.pages)} pages")
    elif mode == "chat":
        cursor = pg_client.cursor()
        cursor.execute("""
        SELECT id, name, page_count FROM documents
        """)
        docs = cursor.fetchall()
        cursor.close()
        if len(docs) == 0:
            print("You do not have any docs converted to embeddings yet. Exiting.")
            exit(0)
        doc_id_list: list[str] = []
        print("----- Available docs -----")
        for doc in docs:
            (document_id, document_name, page_count) = doc
            print(f"{document_id}\t({page_count} pages)\t{document_name}")
            doc_id_list.append(str(document_id))

        current_doc_id: str = ""
        while current_doc_id not in doc_id_list:
            current_doc_id = input("Please select a document (id of the document at the left side): ")
        parsed_doc_id = int(current_doc_id)
        message_history = []

        while True:
            prompt = input("User > ")

            embedding: list[float] = openai.embeddings.create(
                input=prompt,
                model="text-embedding-3-small",
            ).model_dump()["data"][0]["embedding"]

            cursor = pg_client.cursor()

            cursor.execute("""
            SELECT contents, page_number, 1 - (embeddings <=> %s::vector) AS similarity FROM pages WHERE document_id = %s ORDER BY embeddings <=> %s::vector LIMIT 5
            """, (embedding, parsed_doc_id, embedding))


            contents = [f"Similarity: {doc[2]}\nPage: {doc[1]}\nPage Content: {doc[0]}" for doc in cursor.fetchall()]
            context = '\n\n'.join(contents)
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that answers questions based only on the context provided. Be accurate, concise, and do not invent information."
                    },
                    *message_history,
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\n\n\nQuestion: {prompt}"
                    }
                ],
                stream=True
            )
            print(context + "\n\n\n")
            message_history.append({
                "role": "user",
                "content": prompt
            })


            assistant_message = ""
            print("Assistant > ", end=" ", flush=True)
            for chunk in response:
                token = chunk.choices[0].delta.content
                if token:
                    assistant_message += token
                    print(token, end="", flush=True)

            print("\n")
            message_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            if len(message_history) > MAX_HISTORY:
                message_history = message_history[-MAX_HISTORY:]