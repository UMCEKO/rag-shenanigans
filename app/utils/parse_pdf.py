import pymupdf
from app.schema.pdf import PageDetails, DocumentDetails
from app.utils.clean_text import clean_text


def parse_pdf(pdf: pymupdf.Document) -> DocumentDetails:
    # The list that will hold the parsed page data.
    page_details_list: list[PageDetails] = []
    print("Parsing pages...")
    # Iterate through all pages and parse them, no need to split a page because it won't go over the 8k token limit anyway.
    for page in pdf: # type: pymupdf.Page
        # We clean up unwanted parts that might mess with embeddings here.
        clean = clean_text(page.get_textpage().extractText())

        page_details_list.append(
            PageDetails(
                page_number=page.number,
                contents=clean
            )
        )
    return DocumentDetails(
        page_count=pdf.page_count,
        document_name=pdf.name,
        pages=page_details_list
    )

