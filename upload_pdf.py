import os
import uuid
from typing import List
from pypdf import PdfReader
from pinecone import Pinecone
from tqdm import tqdm


class PDFUploader:
    def __init__(self, api_key: str, index_name: str = "college-chatbot1"):
        self.index_name = index_name
        self.pdf_folder = "pdfs"
        self.chunk_size = 500
        self.chunk_overlap = 100
        self.pc = Pinecone(api_key=api_key)

    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk.strip())

            if end >= len(text):
                break

            start = end - self.chunk_overlap

        return chunks

    def upload_chunks(self, chunks: List[str], filename: str) -> int:
        """Upload chunks to Pinecone using integrated embedding."""
        index = self.pc.Index(self.index_name)
        batch_size = 96
        records = []

        for i, chunk in enumerate(chunks):
            record_id = f"{filename}_{i}_{uuid.uuid4().hex[:8]}"

            records.append({
                "_id": record_id,
                "text": chunk,
                "source_filename": filename,
                "chunk_index": i
            })

        uploaded = 0

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            index.upsert_records(namespace="__default__", records=batch)
            uploaded += len(batch)

        return uploaded

    def process_pdfs(self):
        """Process all PDFs in folder."""
        if not os.path.exists(self.pdf_folder):
            print("pdfs folder not found.")
            return

        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith(".pdf")]

        if not pdf_files:
            print("No PDF files found.")
            return

        print(f"Found {len(pdf_files)} PDF files.")
        total_uploaded = 0

        for file in tqdm(pdf_files, desc="Processing PDFs"):
            path = os.path.join(self.pdf_folder, file)
            print(f"\nProcessing: {file}")

            text = self.extract_text(path)
            if not text:
                print("No text extracted.")
                continue

            chunks = self.chunk_text(text)
            print(f"Generated {len(chunks)} chunks.")

            uploaded = self.upload_chunks(chunks, file)
            print(f"Uploaded {uploaded} chunks.")

            total_uploaded += uploaded

        print("\n=== SUMMARY ===")
        print(f"Total chunks uploaded: {total_uploaded}")


if __name__ == "__main__":
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    if not PINECONE_API_KEY:
        print("ERROR: Set PINECONE_API_KEY in environment.")
        exit(1)

    uploader = PDFUploader(PINECONE_API_KEY)
    uploader.process_pdfs()
