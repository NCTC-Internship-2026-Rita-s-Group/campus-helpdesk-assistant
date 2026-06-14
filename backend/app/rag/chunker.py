from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextChunker:
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 150):
        # Recursive splitter intelligently breaks text by paragraphs, then sentences, then words
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_loaded_pages(self, loaded_pages: list[dict]) -> list[dict]:
        """
        Takes raw page segments and splits them into clean, overlapping vectors 
        while preserving source metadata parameters.
        """
        processed_chunks = []

        for page in loaded_pages:
            raw_text = page["text"]
            base_metadata = page["metadata"]

            # Generate split sub-strings for this specific page
            split_strings = self.splitter.split_text(raw_text)

            for segment in split_strings:
                processed_chunks.append({
                    "text": segment,
                    "metadata": base_metadata.copy()  # Carry page and source file along
                })

        print(f"[RAG CHUNKER] Sliced pages into {len(processed_chunks)} individual data chunks.")
        return processed_chunks