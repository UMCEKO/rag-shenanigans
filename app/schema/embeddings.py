from pydantic import BaseModel
from typing_extensions import Union

from app.schema.pdf import PageDetails

Embeddings = list[float]

class EmbeddingInfo(BaseModel):
    embeddings: Embeddings
    page_details: Union[PageDetails]

class EmbeddingResult(BaseModel):
    embedding_info: EmbeddingInfo

class EmbeddedDocumentDetails(BaseModel):
    embedded_pages: list[EmbeddingInfo]
    page_count: int
    document_name: str