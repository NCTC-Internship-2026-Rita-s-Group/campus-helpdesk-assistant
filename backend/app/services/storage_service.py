import os
import re
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

class CloudStorageEngine:
    """
    📁 Local Hard Drive Storage Engine
    Streams binary file buffers securely directly to persistent local server disks,
    completely removing dependencies on external cloud provider bucket networks.
    Maintains class matching properties for transparent backward compatibility.
    """
    def __init__(self):
        # 👑 DETERMINISTIC ABSOLUTE ANCHORING
        # Derive paths relative to the project base workspace directory structure dynamically
        base_dir = Path(__file__).resolve().parents[3]  # Drills back up to project root safely
        self.upload_dir = (base_dir / "data" / "uploaded_files").resolve()
        
        # Programmatically guarantee the repository directories exist on your machine drive
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 [STORAGE ENGINE] Secure local file repository initialized at: {self.upload_dir}")

    def _sanitize_filename(self, filename: str) -> str:
        """
        🛡️ Input Sanitization Filter
        Strips away character paths, directory separators, and invalid filesystem tokens.
        """
        if not filename:
            return "unnamed_document.pdf"
            
        pure_path = Path(filename)
        extension = pure_path.suffix.lower()
        base_name = pure_path.stem
        
        # Enforce alphanumeric boundaries with safe system underscores
        clean_base = re.sub(r"[^a-zA-Z0-9_.-]", "_", base_name)
        
        # Truncate string sizes to prevent operating system path buffer exceptions
        return f"{clean_base[:100]}{extension}"

    async def upload_file_to_cloud(self, file: UploadFile, remote_folder: str = "campus_docs") -> str:
        """
        Streams an incoming file binary payload directly to your local storage directory folder.
        Maintains legacy cloud interface signature bindings to prevent breaking downstream endpoints.
        """
        try:
            # 1. Generate clean, sanitized filenames
            safe_name = self._sanitize_filename(file.filename)
            
            # 2. Formulate explicit absolute path mappings on your drive
            target_path = (self.upload_dir / safe_name).resolve()
            
            # 3. PATH TRAVERSAL GUARD (Enterprise Containment Verification)
            # Confirms cryptographically that the target path stays strictly inside our upload folder boundaries
            if not target_path.is_relative_to(self.upload_dir):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Security Exception: Unauthorized directory breakout trajectory vector detected."
                )

            # 4. MEMORY-SAFE BLOCK STREAMING
            # Rewind file memory pointer stream buffer head to zero to guarantee full reads
            await file.seek(0)
            
            # Write stream chunks sequentially onto the physical disk sector path
            with open(target_path, "wb") as disk_file:
                while chunk := await file.read(1024 * 1024):  # Process 1MB block buffers efficiently
                    disk_file.write(chunk)

            print(f"💾 [LOCAL STORAGE] Asset successfully synchronized onto server disk: {safe_name}")
            
            # Return the exact target string path so your downstream RAG ingestion engine knows precisely where to read it
            return str(target_path)

        except HTTPException:
            raise
        except Exception as system_fault:
            print(f"❌ [LOCAL STORAGE] Critical disk write exception caught: {str(system_fault)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Persistent file write block execution failure: {str(system_fault)}"
            )

# Global structural cloud storage service manager instance
cloud_storage_manager = CloudStorageEngine()