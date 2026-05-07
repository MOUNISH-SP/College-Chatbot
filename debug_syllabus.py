"""
Debug Syllabus Analysis
========================

Test script to debug syllabus analysis with actual document content.
"""

import os
from dotenv import load_dotenv
from document_processor import document_processor
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

def debug_syllabus_analysis():
    """Debug syllabus analysis with real documents"""
    print("🔍 Debugging Syllabus Analysis...")
    
    # Get all documents from database
    try:
        documents = list(document_processor.documents_collection.find({"document_type": "syllabus"}))
        print(f"📊 Found {len(documents)} syllabus documents")
        
        for doc in documents:
            print(f"\n📄 Analyzing: {doc.get('filename', 'Unknown')}")
            print(f"   Document ID: {doc.get('_id')}")
            print(f"   File Type: {doc.get('file_type')}")
            print(f"   Upload Date: {doc.get('upload_date')}")
            
            # Get extracted text
            text = doc.get('extracted_text', '')
            print(f"   Text Length: {len(text)} characters")
            
            if text:
                print(f"   First 200 chars: {text[:200]}...")
                
                # Test each extraction function
                print("\n🧪 Testing Extraction Functions:")
                
                # Course Name
                course_name = document_processor._extract_course_name(text)
                print(f"   Course Name: {course_name}")
                
                # Course Code
                course_code = document_processor._extract_course_code(text)
                print(f"   Course Code: {course_code}")
                
                # Credits
                credits = document_processor._extract_credits(text)
                print(f"   Credits: {credits}")
                
                # Topics
                topics = document_processor._extract_topics(text)
                print(f"   Topics Found: {len(topics)}")
                for i, topic in enumerate(topics[:5]):
                    print(f"     {i+1}. {topic}")
                
                # Evaluation
                evaluation = document_processor._extract_evaluation(text)
                print(f"   Evaluation Items: {len(evaluation)}")
                for i, eval_item in enumerate(evaluation[:3]):
                    print(f"     {i+1}. {eval_item}")
                
                # Textbooks
                textbooks = document_processor._extract_textbooks(text)
                print(f"   Textbooks Found: {len(textbooks)}")
                for i, book in enumerate(textbooks[:2]):
                    print(f"     {i+1}. {book}")
                
                # Check if analysis already exists
                existing_analysis = document_processor.syllabus_collection.find_one({"document_id": str(doc['_id'])})
                if existing_analysis:
                    print(f"   ✅ Analysis already exists in database")
                else:
                    print(f"   ⚠️ No analysis found - creating new one...")
                    analysis_id, syllabus_data = document_processor.analyze_syllabus(str(doc['_id']), text)
                    if analysis_id:
                        print(f"   ✅ New analysis created: {analysis_id}")
                    else:
                        print(f"   ❌ Failed to create analysis")
                
            else:
                print("   ❌ No text extracted from document")
            
            print("-" * 60)
    
    except Exception as e:
        print(f"❌ Error debugging syllabus: {e}")
        import traceback
        traceback.print_exc()

def show_sample_text():
    """Show sample text from a document for manual inspection"""
    try:
        # Get the most recent syllabus document
        doc = document_processor.documents_collection.find_one({"document_type": "syllabus"})
        if doc:
            text = doc.get('extracted_text', '')
            print(f"\n📄 Sample Text from {doc.get('filename')}:")
            print("=" * 50)
            print(text[:1000])
            print("=" * 50)
            print(f"[Text truncated - Full length: {len(text)} characters]")
        else:
            print("❌ No syllabus documents found")
    except Exception as e:
        print(f"❌ Error showing sample text: {e}")

if __name__ == "__main__":
    debug_syllabus_analysis()
    show_sample_text()
