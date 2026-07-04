import os
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from app.config import settings

class VectorStoreEngine:
    """
    🧠 Enterprise Hybrid Vector Storage Core
    Dynamically switches between a local persistent file layer for fast local debugging
    and a hosted HTTP client cluster connection for serverless cloud infrastructure.
    """
    def __init__(self):
        # 1. Instantiate the industry standard local embedding framework
        # This matches your server startup telemetry footprint logs perfectly
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # 2. Check if a dedicated cloud vector cluster endpoint address is provided
        # e.g., CHROMA_SERVER_HOST="https://your-hosted-chroma-instance.com"
        self.cloud_host = os.getenv("CHROMA_SERVER_HOST")
        self.cloud_auth_token = os.getenv("CHROMA_AUTH_TOKEN")
        
        if self.cloud_host:
            print(f"🌐 [VECTOR CORE] Initializing secure cloud client link target: {self.cloud_host}")
            
            headers = {}
            if self.cloud_auth_token:
                headers = {"Authorization": f"Bearer {self.cloud_auth_token}"}
                
            # Establish direct stateless HTTP socket lines to your cloud cluster
            self.client = chromadb.HttpClient(
                host=self.cloud_host,
                headers=headers
            )
        else:
            # Safe local developer workspace tracking path fallback setup
            base_dir = os.path.dirname(os.path.abspath(__file__))
            local_storage_path = os.path.abspath(os.path.join(base_dir, "../../../data/vector_db"))
            os.makedirs(local_storage_path, exist_ok=True)
            
            print(f"💾 [VECTOR CORE] Initializing local development file array block: {local_storage_path}")
            self.client = chromadb.PersistentClient(path=local_storage_path)

        # 3. Mount or acquire our unified helpdesk index reference matrix collection
        self.collection = self.client.get_or_create_collection(
            name="campus_knowledge_base",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"} # Enforces high-precision angular distance search
        )

    async def ingest_document_chunks(self, chunks: List[str], metadatas: List[Dict[str, Any]], source_name: str):
        """
        Writes high-density text layout segments directly into the vector database index.
        """
        try:
            if not chunks:
                return
                
            # Formulate robust unique document identifiers for every sliced index block
            generated_ids = [f"{source_name}_chunk_{idx}" for idx in range(len(chunks))]
            
            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=generated_ids
            )
            print(f"📦 [VECTOR STORE] Successfully synchronized {len(chunks)} text nodes inside the cluster index.")
            
        except Exception as write_fault:
            print(f"❌ [VECTOR STORE] Ingestion matrix commit error: {str(write_fault)}")
            raise write_fault

    def query_semantic_context(self, search_query: str, match_limit: int = 4) -> List[Dict[str, Any]]:
        """
        Executes an vector search against matching text weights inside the core collection.
        Returns a structured array of cited context snippets.
        """
        try:
            results = self.collection.query(
                query_texts=[search_query],
                n_results=match_limit
            )
            
            formatted_contexts = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(documents)
                distances = results["distances"][0] if results.get("distances") else [0.0] * len(documents)
                
                for idx in range(len(documents)):
                    formatted_contexts.append({
                        "text": documents[idx],
                        "metadata": metadatas[idx],
                        "distance": distances[idx]
                    })
                    
            return formatted_contexts
            
        except Exception as query_fault:
            print(f"⚠️ [VECTOR STORE] Semantic lookup bypass encountered: {str(query_fault)}")
            return []

# Unified singleton vector memory engine handle
vector_memory = VectorStoreEngine()