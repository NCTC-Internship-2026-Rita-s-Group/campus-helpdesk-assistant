import os
from typing import List, Dict, Any
import pdfplumber

class CampusDocumentProcessor:
    """
    📄 Production-Grade Context-Enriched Ingestion Engine
    Detects data tables and injects page-level metadata headers directly into 
    every isolated row entity to guarantee absolute vector search precision.
    """
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
        """
        Parses a PDF file from disk, programmatically flattens layout tables,
        and builds self-contained, highly searchable data rows.
        """
        structured_pages = []
        try:
            # Initialize pdfplumber structural layout engine
            with pdfplumber.open(file_path) as pdf:
                for idx, page in enumerate(pdf.pages):
                    page_num = idx + 1
                    
                    # 1. Extract regular text fields
                    page_text = page.extract_text() or ""
                    
                    # Identify the main page title or first descriptive line to use as table context
                    raw_lines = [line.strip() for line in page_text.split("\n") if line.strip()]
                    page_context_header = raw_lines[0] if raw_lines else "Institutional Guide Policy"
                    
                    # 2. Extract visual grid tables natively on the active page sheet
                    tables = page.extract_tables()
                    
                    if tables:
                        enriched_table_records = []
                        for table in tables:
                            if len(table) < 2:
                                continue  # Skip empty or corrupted tabular nodes
                            
                            # Capture the top cell row as the immutable column definitions matrix
                            headers = [str(h).strip().replace("\n", " ") if h else f"Column_{i}" for i, h in enumerate(table[0])]
                            
                            # Loop through every data row and map headers directly to cell values
                            for data_row in table[1:]:
                                cleaned_cells = [str(cell).strip().replace("\n", " ") if cell is not None else "" for cell in data_row]
                                if not any(cleaned_cells):
                                    continue  # Skip empty rows
                                    
                                # Zip columns and cells into an explicit standalone string descriptor
                                row_elements = []
                                for header_title, cell_value in zip(headers, cleaned_cells):
                                    if cell_value:
                                        row_elements.append(f"{header_title}: {cell_value}")
                                        
                                if row_elements:
                                    # Inject the page header directly into the row text
                                    enriched_record = f"[Data Record - Context: {page_context_header}]: " + " | ".join(row_elements)
                                    enriched_table_records.append(enriched_record)
                        
                        # Append the processed rows directly back into the page context block
                        if enriched_table_records:
                            page_text += "\n\n### Verified Institutional Data Directory:\n" + "\n".join(enriched_table_records)

                    if page_text.strip():
                        structured_pages.append({
                            "text": page_text,
                            "page": page_num
                        })
            
            print(f"[RAG LOADER] Successfully built context-enriched vectors across {len(structured_pages)} pages.")
            return structured_pages
            
        except Exception as e:
            print(f"❌ Critical layout grid extraction failure: {str(e)}")
            return []

# Shared processing utility instance
document_processor = CampusDocumentProcessor()