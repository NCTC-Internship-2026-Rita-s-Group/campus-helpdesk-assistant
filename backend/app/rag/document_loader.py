import os
from pypdf import PdfReader

class DocumentLoader:
    @staticmethod
    def load_pdf(file_path: str) -> list[dict]:
        """
        Reads a local PDF file and extracts raw text along with page-level metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Target PDF file not found at: {file_path}")

        filename = os.path.basename(file_path)
        extracted_pages = []

        try:
            # Initialize the PyPDF reader instance
            reader = PdfReader(file_path)
            
            # Loop page-by-page through the document
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    extracted_pages.append({
                        "text": text.strip(),
                        "metadata": {
                            "source": filename,
                            "page": page_num
                        }
                    })
            
            print(f"[RAG LOADER] Extracted {len(extracted_pages)} valid pages from {filename}")
            return extracted_pages

        except Exception as e:
            print(f"[RAG LOADER ERROR] Failed parsing {filename}: {str(e)}")
            return []