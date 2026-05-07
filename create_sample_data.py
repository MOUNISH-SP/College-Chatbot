import os
import uuid
from pinecone import Pinecone

# Sample college content for testing
SAMPLE_CONTENT = [
    {
        "text": "Kongu Engineering College offers undergraduate programs in Computer Science and Engineering, Electronics and Communication Engineering, Mechanical Engineering, Civil Engineering, Electrical and Electronics Engineering, and Information Technology.",
        "source": "departments_info"
    },
    {
        "text": "The placement cell at Kongu Engineering College has an excellent track record with over 90% of students getting placed in reputed companies. Top recruiters include TCS, Infosys, Wipro, HCL, CTS, and many multinational companies.",
        "source": "placement_info"
    },
    {
        "text": "Admission to Kongu Engineering College is based on merit. Students must have completed 12th grade with Mathematics, Physics, and Chemistry. Admission is through Anna University counseling and management quota.",
        "source": "admission_info"
    },
    {
        "text": "Kongu Engineering College has excellent infrastructure with modern laboratories, well-stocked library, sports facilities, hostel accommodation for both boys and girls, and a spacious campus with green environment.",
        "source": "infrastructure_info"
    },
    {
        "text": "The vision of Kongu Engineering College is to provide quality technical education and develop professionals with ethical values to serve the society and nation.",
        "source": "vision_info"
    }
]

def upload_sample_data():
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") or "pcsk_4RMNQa_PM86YFQPgc1wFNMnCT3iDszDhRh86YGhMQVm7V5RjH7WQpnCYe4qbvUxALm9UQS"
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("college-chatbot1")
    
    records = []
    
    for i, content in enumerate(SAMPLE_CONTENT):
        record_id = f"sample_{i}_{uuid.uuid4().hex[:8]}"
        
        records.append({
            "_id": record_id,
            "text": content["text"],
            "source_filename": content["source"],
            "chunk_index": i
        })
    
    # Upload in batches
    batch_size = 96
    uploaded = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        index.upsert_records(namespace="__default__", records=batch)
        uploaded += len(batch)
    
    print(f"Uploaded {uploaded} sample content chunks to Pinecone.")

if __name__ == "__main__":
    upload_sample_data()
