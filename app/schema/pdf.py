from pydantic import BaseModel

class PageDetails(BaseModel):
    page_number: int
    contents: str

class DocumentDetails(BaseModel):
    document_name: str
    page_count: int
    pages: list[PageDetails]

class BatchedDocumentDetails(BaseModel):
    batches: list[list[PageDetails]]
    page_count: int
    document_name: str

