from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Intelligently separates text layout strings by checking structural boundary markers
        character-by-character to prevent data fragmentation.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_loaded_pages(self, loaded_pages: list[dict], filename: str = "Campus Bulletin") -> list[dict]:
        """
        Processes structural page dictionary blocks and creates granular, overlapping vector text chunks
        while binding immutable file and page tracking attributes to each chunk.
        """
        processed_chunks = []

        for page in loaded_pages:
            raw_text = page.get("text", "")
            page_num = page.get("page", 1)

            if not raw_text.strip():
                continue

            # Generate granular split sub-strings for this specific page layout
            split_strings = self.splitter.split_text(raw_text)

            for segment in split_strings:
                processed_chunks.append({
                    "text": segment,
                    "source": filename,  # 🚀 Injects tracking attributes for citation lookups
                    "page": page_num
                })

        print(f"[RAG CHUNKER] Sliced pages array into {len(processed_chunks)} granular context vectors.")
        return processed_chunks