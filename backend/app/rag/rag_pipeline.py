from app.rag.document_loader import DocumentLoader
from app.rag.chunker import TextChunker
from app.rag.vector_store import CampusVectorStore
from app.services.llm_service import LLMService 

class RAGPipeline:
    @staticmethod
    def ingest_document(file_path: str, filename: str) -> dict:
        try:
            loaded_pages = DocumentLoader.load_pdf(file_path)
            if not loaded_pages:
                return {"filename": filename, "status": "Failed", "detail": "No parseable text content detected."}

            chunker = TextChunker()
            processed_chunks = chunker.split_loaded_pages(loaded_pages)

            vector_db = CampusVectorStore()
            success = vector_db.index_processed_chunks(processed_chunks)

            if success:
                return {
                    "filename": filename,
                    "status": "Successfully Indexed",
                    "chunks_created": len(processed_chunks),
                    "vector_store": "ChromaDB Persistent"
                }
            else:
                return {"filename": filename, "status": "Failed", "detail": "Database engine write error."}

        except Exception as e:
            return {"filename": filename, "status": "Failed", "detail": str(e)}

    # =========================================================================
    # VERIFY THIS METHOD RIGOROUSLY IN YOUR FILE:
    # =========================================================================
    @staticmethod
    def query_knowledge_base(user_query: str) -> dict:
        """
        Queries ChromaDB vector collection for top matches, synthesizes 
        raw data via Anthropic Claude, and formats clean source page citations.
        """
        try:
            vector_db = CampusVectorStore()
            
            # 1. Fetch the 3 most textually similar document fragments from storage
            matched_chunks = vector_db.search_similar_chunks(user_query, n_results=3)
            
            if not matched_chunks:
                return {
                    "answer": "I could not locate any official university documentation matching your request in our knowledge base.",
                    "sources": [],
                    "confidence_score": 0.0
                }
                
            # 2. Combine the texts into a unified structural context window prompt block
            combined_context = "\n\n".join([f"--- Context Segment ---\n{chunk['text']}" for chunk in matched_chunks])
            
            # 3. Call our Claude text synthesizer service layer!
            ai_answer = LLMService.synthesize_answer(user_query, combined_context)
            
            # CRITICAL CHECK: If the AI service returns an operational error or billing apology,
            # drop the confidence score to 0.0 to force LangGraph to escalate the query.
            if "We apologize" in ai_answer or "interruption occurred" in ai_answer:
                confidence = 0.0
            else:
                confidence = 0.95
            
            # 4. Filter out unique source references to ensure clean UI citation maps
            unique_sources = []
            seen_coordinates = set()
            
            for chunk in matched_chunks:
                coordinate = (chunk["source"], chunk["page"])
                if coordinate not in seen_coordinates:
                    seen_coordinates.add(coordinate)
                    unique_sources.append({
                        "document": chunk["source"],
                        "page": chunk["page"]
                    })
                    
            return {
                "answer": ai_answer,
                "sources": unique_sources,
                "confidence_score": confidence
            }
            
        except Exception as e:
            print(f"[RAG PIPELINE RETRIEVAL CRASH] Failed pulling search indexes: {str(e)}")
            return {
                "answer": "An operational failure occurred while trying to process this question.",
                "sources": [],
                "confidence_score": 0.0
            }