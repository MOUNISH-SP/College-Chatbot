"""
Re-analyze Syllabus Documents
===============================

Re-analyze existing syllabus documents with improved extraction algorithms.
"""

import os
from dotenv import load_dotenv
from document_processor import document_processor
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

def reanalyze_syllabus_documents():
    """Re-analyze all syllabus documents with improved extraction"""
    print("🔄 Re-analyzing Syllabus Documents...")
    
    try:
        # Get all syllabus documents
        documents = list(document_processor.documents_collection.find({"document_type": "syllabus"}))
        print(f"📊 Found {len(documents)} syllabus documents to re-analyze")
        
        for doc in documents:
            doc_id = str(doc['_id'])
            filename = doc.get('filename', 'Unknown')
            print(f"\n📄 Re-analyzing: {filename}")
            
            # Delete existing analysis
            document_processor.syllabus_collection.delete_many({"document_id": doc_id})
            print(f"   🗑️ Deleted old analysis")
            
            # Re-analyze with improved extraction
            text = doc.get('extracted_text', '')
            if text:
                analysis_id, syllabus_data = document_processor.analyze_syllabus(doc_id, text)
                
                if analysis_id and syllabus_data:
                    print(f"   ✅ New analysis created: {analysis_id}")
                    print(f"   📚 Course Name: {syllabus_data.get('course_name', 'N/A')}")
                    print(f"   🔢 Course Code: {syllabus_data.get('course_code', 'N/A')}")
                    print(f"   ⭐ Credits: {syllabus_data.get('credits', 0)}")
                    print(f"   📋 Topics: {len(syllabus_data.get('topics', []))}")
                    print(f"   📝 Evaluation: {len(syllabus_data.get('evaluation', []))}")
                    print(f"   📚 Textbooks: {len(syllabus_data.get('textbooks', []))}")
                else:
                    print(f"   ❌ Failed to create analysis")
            else:
                print(f"   ⚠️ No text found for analysis")
        
        print(f"\n🎉 Re-analysis completed!")
        
    except Exception as e:
        print(f"❌ Error re-analyzing syllabus: {e}")
        import traceback
        traceback.print_exc()

def show_current_analyses():
    """Show current syllabus analyses"""
    print("\n📋 Current Syllabus Analyses:")
    print("=" * 50)
    
    try:
        analyses = list(document_processor.syllabus_collection.find({}))
        for analysis in analyses:
            print(f"\n📄 Document ID: {analysis.get('document_id')}")
            print(f"   📚 Course: {analysis.get('course_name', 'N/A')}")
            print(f"   🔢 Code: {analysis.get('course_code', 'N/A')}")
            print(f"   ⭐ Credits: {analysis.get('credits', 0)}")
            print(f"   📋 Topics: {len(analysis.get('topics', []))}")
            
            # Show first few topics
            topics = analysis.get('topics', [])
            if topics:
                print(f"   Sample Topics:")
                for i, topic in enumerate(topics[:3]):
                    print(f"     {i+1}. {topic}")
            
            print(f"   📅 Analyzed: {analysis.get('analysis_date', 'N/A')}")
            print("-" * 30)
    
    except Exception as e:
        print(f"❌ Error showing analyses: {e}")

if __name__ == "__main__":
    reanalyze_syllabus_documents()
    show_current_analyses()
