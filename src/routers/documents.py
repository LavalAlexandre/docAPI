from fastapi import APIRouter, HTTPException

from src.data import fake_documents_db
from src.exceptions import DocumentNotFoundError
from src.models import Document, PatientNameResponse
from src.operations.documents import extract_patient_name

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[Document])
async def read_documents() -> list[Document]:
    """Return all documents available in the fake data store."""
    return list(fake_documents_db.values())


@router.get("/{document_id}", response_model=Document)
async def read_document(document_id: str) -> Document:
    """Retrieve a specific document by its ID.
    
    Args:
        document_id: The unique identifier of the document.
        
    Returns:
        The requested document.
        
    Raises:
        HTTPException: 404 if the document is not found.
    """
    if document_id not in fake_documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    return fake_documents_db[document_id]


@router.get("/{document_id}/patient-name", response_model=PatientNameResponse)
async def get_document_patient_name(document_id: str) -> PatientNameResponse:
    """Get the extracted patient name from a document."""
    try:
        name = extract_patient_name(document_id)
        return PatientNameResponse(document_id=document_id, extracted_name=name)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
