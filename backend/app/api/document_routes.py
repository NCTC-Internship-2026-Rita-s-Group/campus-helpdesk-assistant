import os
import json
import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text 

from app.database import get_db
from app.rag.document_loader import document_processor
from app.rag.vector_store import vector_memory
from app.rag.chunker import TextChunker
from app.services.storage_service import cloud_storage_manager  # 📁 Managed Local Hard Drive Storage Engine
from app.services.security import verify_admin_clearance         # 🔒 Secured Administrative Gateway Guard
from app.models.db_models import User                           # 🗄️ Ingest User class model definition cleanly

router = APIRouter(prefix="/documents", tags=["Administrative Knowledge Ingestion"])


async def asynchronous_indexing_worker(file_name: str, local_file_path: str):
    """
    ⚙️ Non-Blocking Background Processing Worker
    Reads asset files directly from the local disk vault storage layer,
    extracts structural page metrics, and populates the ChromaDB vector core.
    """
    try:
        print(f"🔄 Background Task Started: Ingesting local file structures for '{file_name}'...")
        print(f"📍 Reading target path: {local_file_path}")
        
        # 1. Extract text and table layers directly from the local drive
        if file_name.lower().endswith(".pdf"):
            structured_pages = document_processor.extract_text_from_pdf(local_file_path)
        else:
            # Fallback treating it as plain text (.txt, .md)
            with open(local_file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
            structured_pages = [{"text": raw_text, "page": 1}] if raw_text.strip() else []

        if not structured_pages:
            print(f"⚠️ Background Task Halted: No text metrics recovered from file '{file_name}'.")
            return

        # 2. Slice structural page segments into high-density context chunks
        chunker = TextChunker()
        processed_chunks = chunker.split_loaded_pages(structured_pages, filename=file_name)
        
        if not processed_chunks:
            print(f"⚠️ Background Task Halted: Chunk splitting yielded zero text layers for '{file_name}'.")
            return

        # 3. Unpack chunk elements and append local file location tracking properties
        text_chunks = [item["text"] for item in processed_chunks]
        metadatas = [
            {
                "source": item["source"], 
                "page": item["page"],
                "local_storage_path": local_file_path  # 🔗 Traceability tracking metric
            } 
            for item in processed_chunks
        ]

        # 4. Write data coordinates directly into local persistent ChromaDB files
        await vector_memory.ingest_document_chunks(
            chunks=text_chunks,
            metadatas=metadatas,
            source_name=file_name
        )
        print(f"✅ Background Task Success: Local asset '{file_name}' indexed completely into vector core.")

    except Exception as e:
        print(f"❌ Background Worker Exception on file '{file_name}': {str(e)}")
        import traceback
        traceback.print_exc()


# 👑 FIX BOUNDARY MATCHING STRATEGY & BLANKET DATA FOR FE ICON RESOLUTION
@router.get("", status_code=status.HTTP_200_OK)
@router.get("/", status_code=status.HTTP_200_OK)
async def list_uploaded_documents(current_admin: User = Depends(verify_admin_clearance)):
    """
    📋 Robust Directory Discovery Registry
    Scans the local directory and blankets individual entries with every key matching
    possibility to guarantee the frontend UI icon compilers execute safely without 'undefined' errors.
    """
    try:
        target_dir = Path(cloud_storage_manager.upload_dir)
        document_records = []
        
        if target_dir.exists():
            for file_item in target_dir.iterdir():
                if file_item.is_file() and file_item.suffix.lower() in ['.pdf', '.txt', '.md', '.json', '.csv']:
                    stats = file_item.stat()
                    file_size_kb = round(stats.st_size / 1024, 2)
                    mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Compute structural file format strings
                    ext_raw = file_item.suffix.lower()                   # e.g., ".pdf"
                    ext_clean = ext_raw.replace(".", "")                 # e.g., "pdf"
                    mime_type = "application/pdf" if ext_clean == "pdf" else "text/plain"
                    readable_size = f"{file_size_kb} KB" if file_size_kb < 1024 else f"{round(file_size_kb/1024, 2)} MB"

                    # 👑 BLANKET MATRIX: Fulfills both 'size' and 'fileSize', and 'type' and 'format' dual-contracts cleanly
                    document_records.append({
                        "id": file_item.name,
                        "filename": file_item.name,
                        "name": file_item.name,
                        "size": readable_size,
                        "fileSize": readable_size,              # 🎨 Restored for admin table data mapping
                        "uploaded_at": mod_time,
                        "timeCreated": mod_time,
                        "updated": mod_time,
                        "status": "synchronized",
                        "type": ext_clean,
                        "file_type": ext_clean,
                        "extension": ext_clean,
                        "ext": ext_clean,
                        "format": ext_clean,                 # 🎨 Restored for admin table file format icon matching
                        "contentType": mime_type,
                        "mimeType": mime_type,
                        "metadata": {
                            "contentType": mime_type,
                            "type": ext_clean,
                            "extension": ext_clean
                        }
                    })

        return document_records

    except Exception as scan_fault:
        print(f"❌ [DOCUMENT DISCOVERY] Folder parsing failure: {str(scan_fault)}")
        return []


@router.post("", status_code=status.HTTP_202_ACCEPTED)
@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_institutional_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_admin: User = Depends(verify_admin_clearance)
):
    """
    📤 Secure Local File Ingestion Gateway
    """
    file_name = file.filename
    if not (file_name.lower().endswith(".pdf") or file_name.lower().endswith(".txt") or file_name.lower().endswith(".md") or file_name.lower().endswith(".json") or file_name.lower().endswith(".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format asset. Please provide standardized text, markdown, csv, or PDF documents."
        )

    try:
        local_file_path = await cloud_storage_manager.upload_file_to_cloud(file)
    except Exception as disk_fault:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record asset onto local server disk storage architecture: {str(disk_fault)}"
        )

    background_tasks.add_task(asynchronous_indexing_worker, file_name, local_file_path)

    return {
        "message": "Document execution context secured in local file storage. Ingestion pipeline scheduled.",
        "file_name": file_name,
        "filename": file_name,
        "local_path": local_file_path,
        "authorized_operator": current_admin.email,  
        "status": "processing"
    }


@router.post("/reindex", status_code=status.HTTP_200_OK)
async def clear_and_reindex_campus_knowledge_base(
    current_admin: User = Depends(verify_admin_clearance),  
    db: AsyncSession = Depends(get_db)
):
    """
    🔄 Programmatic Global Vector Re-Indexing Endpoint (FR-08)
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    docs_folder = os.path.join(base_dir, "data", "documents")

    if not os.path.exists(docs_folder):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Core structural data path missing on host instance: {docs_folder}"
        )

    supported_files = [f for f in os.listdir(docs_folder) if os.path.splitext(f)[1].lower() in [".txt", ".md", ".pdf", ".json", ".csv"]]

    if not supported_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reindexing aborted: Local data directory contains no source document assets."
        )

    try:
        total_chunks_synced = 0
        if hasattr(vector_memory, "clear_collection"):
            await vector_memory.clear_collection()

        for file_name in supported_files:
            file_path = os.path.join(docs_folder, file_name)
            
            if file_name.lower().endswith(".pdf"):
                structured_pages = document_processor.extract_text_from_pdf(file_path)
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = f.read()
                structured_pages = [{"text": raw_text, "page": 1}] if raw_text.strip() else []

            if not structured_pages:
                continue

            chunker = TextChunker()
            processed_chunks = chunker.split_loaded_pages(structured_pages, filename=file_name)
            
            if not processed_chunks:
                continue

            text_chunks = [item["text"] for item in processed_chunks]
            metadatas = [{"source": item["source"], "page": item["page"]} for item in processed_chunks]

            await vector_memory.ingest_document_chunks(chunks=text_chunks, metadatas=metadatas, source_name=file_name)
            total_chunks_synced += len(text_chunks)

        # 👑 PRODUCTION SAFETY TRAIL: Employs a text-safe statement block immune to schema mapping discrepancies
        try:
            audit_query = text("""
                INSERT INTO chat_audit_logs (user_query, ai_response, latency_seconds, estimated_tokens, is_safe, triggered_rules)
                VALUES (:user_query, :ai_response, :latency_seconds, :estimated_tokens, :is_safe, :triggered_rules)
            """)
            await db.execute(audit_query, {
                "user_query": "SYSTEM_REINDEX_COMMAND",
                "ai_response": f"Success: Synced {len(supported_files)} files into {total_chunks_synced} nodes.",
                "latency_seconds": 0.0,
                "estimated_tokens": total_chunks_synced,
                "is_safe": True,
                "triggered_rules": "None"
            })
            await db.commit()
        except Exception as e:
            print(f"⚠️ Audit logging trace skipped: {str(e)}")

        return {"success": True, "processed_files_count": len(supported_files), "total_vector_nodes_generated": total_chunks_synced, "operator": current_admin.email}

    except Exception as err:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))