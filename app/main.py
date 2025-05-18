import os.path
import sys

import pymupdf

from app.core.postgres import prep_db
from app.utils.embedding import batch_for_embeddings, convert_batches_to_embedding, apply_embedded_document_to_db
from app.utils.parse_pdf import parse_pdf


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
        print("Chat mode is not yet implemented")
        sys.exit(0)