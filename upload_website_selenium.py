import os
import uuid
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    
    # OTHERS
    "https://kongu.ac.in/campus-life",
    "https://kongu.ac.in/campus-life",
    "https://cpf-frontend.onrender.com/",
    "https://academic.kongu.edu/",
    "https://coe.kongu.edu/",
    "https://rnd.kongu.edu/",
    "https://iipc.kongu.edu/",
    "https://kongu.irins.org/"
]

class SeleniumWebsiteUploader:
    def __init__(self, api_key, index_name="college-chatbot1"):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.chunk_size = 800
        self.chunk_overlap = 150
        
    def setup_driver(self):
        """Setup Chrome driver with headless options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Please ensure Chrome browser is installed")
            return None

    def fetch_and_extract(self, url, driver):
        """Fetch and extract content using Selenium"""
        try:
            print(f"Loading page: {url}")
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Get page content
            page_source = driver.page_source
            
            # Extract text using similar logic as before
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, "html.parser")
            
            # Remove script and style tags
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            
            # Try to find main content areas
            main_content = ""
            
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
                if line and len(line) > 10 and "You need to enable JavaScript" not in line:
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def chunk_text(self, text):
        """Split text into overlapping chunks"""
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
        """Upload chunks to Pinecone"""
        index = self.pc.Index(self.index_name)
        batch_size = 96
        records = []
        
        for i, chunk in enumerate(chunks):
            record_id = f"web_selenium_{uuid.uuid4().hex[:10]}"
            
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

def main():
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") or "pcsk_4RMNQa_PM86YFQPgc1wFNMnCT3iDszDhRh86YGhMQVm7V5RjH7WQpnCYe4qbvUxALm9UQS"
    
    if not PINECONE_API_KEY:
        print("Set PINECONE_API_KEY first.")
        return
    
    uploader = SeleniumWebsiteUploader(PINECONE_API_KEY)
    driver = uploader.setup_driver()
    
    if not driver:
        print("Failed to setup browser driver")
        return
    
    total_uploaded = 0
    
    try:
        for url in tqdm(URLS, desc="Scraping with Selenium"):
            print(f"\nProcessing: {url}")
            
            text = uploader.fetch_and_extract(url, driver)
            
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
    
    finally:
        driver.quit()
    
    print(f"\n=== SELENIUM WEBSITE SUMMARY ===")
    print(f"Total website chunks uploaded: {total_uploaded}")

if __name__ == "__main__":
    main()
