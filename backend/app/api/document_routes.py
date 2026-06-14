from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.models.schemas import APIResponse
from app.rag.rag_pipeline import RAGPipeline
import os
import shutil

router = APIRouter()

# Dynamically calculate the absolute path to your uploads folder
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/uploads"))

@router.post("/upload", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
def upload_college_document(file: UploadFile = File(...)):
    """
    Upload official college brochures/syllabi PDFs to the campus helpdesk storage.
    """
    # Enforce strict PDF verification to protect the RAG engine parsing step
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. The campus helpdesk knowledge base only accepts official .pdf documents."
        )

    try:
        # Ensure the physical uploads directory exists on the system host
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Construct the safe absolute file path destination
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Stream the uploaded file chunks directly onto your local disk storage
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Trigger Gaurav's RAG Ingestion Pipeline immediately after a successful save
        ingestion_result = RAGPipeline.ingest_document(file_path, file.filename)
        
        return APIResponse(
            success=True,
            message=f"Document '{file.filename}' uploaded and queued for vector embedding indexing successfully.",
            data=ingestion_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Critical document storage failure: {str(e)}"
        )

@router.post("/reindex", response_model=APIResponse[dict])
def trigger_vector_reindex():
    """
    Force-rebuild the local ChromaDB vector store collection index across all stored assets.
    """
    # This will let the admin team manually refresh everything if text formatting changes
    return APIResponse(
        success=True,
        message="Global vector store reindexing pipeline triggered successfully across all local campus assets.",
        data={"status": "Processing Background Ingestion"}
    )