import os
import uuid
import requests
from bs4 import BeautifulSoup
from pinecone import Pinecone
from tqdm import tqdm


URLS = [
    # ABOUT
    "https://kongu.ac.in/aboutkec",
    "https://kongu.ac.in/vision",
    "https://kongu.ac.in/officebearers",
    "https://kongu.ac.in/headoftheinstitution",
    "https://kongu.ac.in/governingcouncil",
    "https://kongu.ac.in/academiccouncil",
    "https://kongu.ac.in/universityranks",
    "https://kongu.ac.in/endownments",
    "https://kongu.ac.in/collegerules",

    # DEPARTMENTS
    "https://kongu.ac.in/ug",
    "https://kongu.ac.in/pg",
    "https://kongu.ac.in/doctoral",
    "https://kongu.ac.in/appliedscience",
    "https://kongu.ac.in/snh",

    # PLACEMENT
    "https://kongu.ac.in/placement",

    # ADMISSION
    "https://kongu.ac.in/admission",

    # CAMPUS LIFE
    "https://kongu.ac.in/campus-life"
]


class WebsiteUploader:
    def __init__(self, api_key, index_name="college-chatbot1"):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.chunk_size = 500
        self.chunk_overlap = 100

    def fetch_and_extract(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style tags
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            # Try to find main content areas
            main_content = ""
            
            # Look for common content containers
            for selector in ['main', 'article', '.content', '#content', '.post-content', '.page-content', '.container', '.row', '.col']:
                content_area = soup.select_one(selector)
                if content_area:
                    main_content = content_area.get_text(separator="\n")
                    break
            
            # If no main content found, use body
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text(separator="\n")
            
            # Clean up text
            lines = main_content.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line and len(line) > 10 and "You need to enable JavaScript" not in line:  # Skip JS message and short lines
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def chunk_text(self, text):
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

    def upload_chunks(self, chunks, source_url):
        index = self.pc.Index(self.index_name)
        batch_size = 96
        records = []

        for i, chunk in enumerate(chunks):
            record_id = f"web_{uuid.uuid4().hex[:10]}"

            records.append({
                "_id": record_id,
                "text": chunk,
                "source_filename": source_url,
                "chunk_index": i
            })

        uploaded = 0

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            index.upsert_records(namespace="__default__", records=batch)
            uploaded += len(batch)

        return uploaded


if __name__ == "__main__":
    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        print("Set PINECONE_API_KEY first.")
        exit(1)

    uploader = WebsiteUploader(api_key)

    total_uploaded = 0

    for url in tqdm(URLS, desc="Scraping Website Pages"):
        print(f"\nProcessing: {url}")
        text = uploader.fetch_and_extract(url)

        if not text:
            print("No text extracted.")
            continue

        print(f"Extracted text length: {len(text)} characters")
        print(f"First 200 characters: {text[:200]}...")

        chunks = uploader.chunk_text(text)
        print(f"Generated {len(chunks)} chunks.")

        uploaded = uploader.upload_chunks(chunks, url)
        print(f"Uploaded {uploaded} chunks.")

        total_uploaded += uploaded

    print("\n=== WEBSITE SUMMARY ===")
    print(f"Total website chunks uploaded: {total_uploaded}")
