import openai
import tiktoken

from app.core.postgres import pg_client
from app.schema.embeddings import Embeddings, EmbeddingInfo, EmbeddedDocumentDetails
from app.schema.pdf import PageDetails, DocumentDetails, BatchedDocumentDetails


def batch_for_embeddings(doc_details: DocumentDetails) -> BatchedDocumentDetails:
    # Here, we split the contents to smaller batches if over the limit in order to comply with Openai max limit of 300.000 tokens per request.
    batches: list[list[PageDetails]] = []
    curr_token_count = 0
    encoding_name = tiktoken.encoding_name_for_model("text-embedding-3-small")
    encoding = tiktoken.get_encoding(encoding_name)
    current_batch: list[PageDetails] = []
    batch_applied = False
    print("Started batching...")
    for page_details in doc_details.pages:
        tokens = encoding.encode(page_details.contents)
        """
        The reason we check for 275k instead of something like 295k is because, 
        well, openai adds a few internal logic tokens probably,
        and this messes it up even if the batch equates to 290k here. 
        For example, when I fed a chunk that equated to 288970 tokens, openai got mad at me saying we requested 303249 tokens.
        Learnt it the hard way... (around 40 minutes wasted here because of that dumb bug)
        """
        if curr_token_count < 275_000:
            # Here, we introduce a new batch since it is too much to handle for one request.
            curr_token_count += len(tokens)
            batch_applied = False
            current_batch.append(page_details)
        else:
            curr_token_count = len(tokens)
            batches.append(current_batch)
            batch_applied = True
            current_batch = [page_details]

    # We add the remaining batch if it has not been appended yet.
    if not batch_applied:
        batches.append(current_batch)

    print(f"There are {len(batches)} batches.")
    return BatchedDocumentDetails(
        document_name=doc_details.document_name,
        page_count=doc_details.page_count,
        batches=batches
    )

def apply_embedded_document_to_db(embedded_document: EmbeddedDocumentDetails):
    cursor = pg_client.cursor()
    cursor.execute("""
        INSERT INTO documents(name, page_count) VALUES (%s, %s) RETURNING id
        """, (embedded_document.name, embedded_document.page_count))
    document_id = cursor.fetchone()[0]
    # Finally, we insert the pages to the database.
    for embedding_info in embedded_document.embedded_pages:
        cursor.execute("""
            INSERT INTO pages(
                page_number,
                document_id, 
                contents, 
                embeddings
                ) VALUES (
                %s,
                %s,
                %s,
                %s
                )
            """, (
            embedding_info.page_details.page_number,
            document_id,
            embedding_info.page_details.contents,
            embedding_info.embeddings
        ))

    cursor.close()
    pg_client.commit()

def convert_batches_to_embedding(doc_details: BatchedDocumentDetails) -> EmbeddedDocumentDetails:
    # Here, we send the text contents to retrieve their embeddings.
    embeddings: list[Embeddings] = []
    for i, batch in enumerate(doc_details.batches):
        print(f"Processing batch {i + 1}")
        embedding_result = openai.embeddings.create(
            model="text-embedding-3-small",
            input=[p.contents for p in batch]
        )
        # Get the embeddings in a list
        dump: list[Embeddings] = [
            embedding_obj["embedding"]
            for embedding_obj in embedding_result.model_dump()["data"]
        ]
        print(f"Successfully processed batch {i + 1}")
        embeddings.extend(dump)

    embedding_info_list: list[EmbeddingInfo] = []

    # We merge the page details with their embeddings to prepare them for db insertion
    for i, embedding in enumerate(embeddings):
        page_details = doc_details.pages[i]
        embedding_info_list.append(
            EmbeddingInfo(
                page_details=page_details,
                embeddings=embedding
            )
        )
    return EmbeddedDocumentDetails(
        document_name=doc_details.document_name,
        page_count=doc_details.page_count,
        embedded_pages=embedding_info_list
    )