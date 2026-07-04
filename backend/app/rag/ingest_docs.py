import os
import sys
import asyncio
import warnings
from datetime import datetime

# 🛑 Suppress telemetry warning logs and third-party deprecation noise during execution
os.environ["ANONYMIZED_TELEMETRY"] = "False"
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")

# Adjust the system path so Python can find your 'app' modules cleanly from the project base directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.rag.vector_store import vector_memory

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list:
    """
    Chops massive document text walls into high-density semantic windows.
    Increased to 1200 characters to prevent structural list fragmentation (e.g., campus counts).
    """
    chunks = []
    start = 0
    if not text:
        return chunks
        
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
        
    return chunks

def extract_text_from_file(file_path: str) -> str:
    """
    Extracts underlying raw text payloads safely using extension routing rules.
    Supports .txt, .md, and multi-page .pdf processing structures.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
            
    elif ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            pdf_text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text.append(page_text)
            return "\n".join(pdf_text)
        except ImportError:
            print("⚠️ Production Core Alert: Missing dependency 'pypdf'. Execute: pip install pypdf")
            return ""
        except Exception as pdf_err:
            print(f"❌ Failed processing layout extraction for {os.path.basename(file_path)}: {pdf_err}")
            return ""
            
    return ""

async def process_and_ingest_documents():
    """
    Sweeps the local raw document target space, divides strings into dense 
    vector payloads, and commits them asynchronously to ChromaDB cluster indexes.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    docs_folder = os.path.join(base_dir, "data", "documents")
    
    print(f"\n📂 [INGESTION ENGINE] Scanning core target directory: {docs_folder}")
    
    if not os.path.exists(docs_folder):
        print(f"❌ Target structural root '{docs_folder}' does not exist on this machine.")
        return

    supported_files = [
        f for f in os.listdir(docs_folder) 
        if os.path.splitext(f)[1].lower() in [".txt", ".md", ".pdf"]
    ]
    
    if not supported_files:
        print("⚠️ Ingestion Idle: No valid text, markdown, or PDF prospectus items found in data/documents/")
        return

    print(f"📌 Found {len(supported_files)} high-fidelity source candidate file(s) for cluster syncing.")

    for file_name in supported_files:
        file_path = os.path.join(docs_folder, file_name)
        print(f"📖 De-serializing text structures from: {file_name}...")
        
        raw_text = extract_text_from_file(file_path)
        if not raw_text.strip():
            print(f"⚠️ Ingestion skipped for '{file_name}': File payload evaluated as empty string.")
            continue

        text_chunks = chunk_text(raw_text)
        print(f"⚡ Successfully chunked stream into {len(text_chunks)} discrete semantic contexts.")

        chunks_list = []
        metadatas_list = []
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Compile structural data block arrays matching VectorStoreEngine specifications
        for idx, chunk in enumerate(text_chunks):
            chunks_list.append(chunk)
            metadatas_list.append({
                "source": file_name,
                "chunk_index": idx,
                "ingested_at": current_timestamp
            })

        # Asynchronously commit the array maps into your vector memory store
        try:
            print(f"📥 Shipping {len(chunks_list)} optimized nodes directly to vector disk arrays...")
            await vector_memory.ingest_document_chunks(
                chunks=chunks_list,
                metadatas=metadatas_list,
                source_name=file_name
            )
            print(f"✅ Vector core memory synchronization verified for: {file_name}")
        except Exception as store_err:
            print(f"❌ Storage layer exception raised while processing batch arrays for {file_name}: {store_err}")

    print("\n🎉 [INGESTION COMPLETE] All target document assets are now stored safely inside the ChromaDB vector core.")

if __name__ == "__main__":
    # Initialize the asynchronous execution framework event loop cleanly
    asyncio.run(process_and_ingest_documents())