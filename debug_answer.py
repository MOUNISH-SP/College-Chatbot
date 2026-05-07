"""
Debug Answer Generation
======================

Test if the answer generation is working properly.
"""

import os
from retriever import retrieve_answer

# Set environment variables
os.environ["PINECONE_API_KEY"] = os.getenv("pcsk_4RMNQa_PM86YFQPgc1wFNMnCT3iDszDhRh86YGhMQVm7V5RjH7WQpnCYe4qbvUxALm9UQS")
os.environ["GROK_API_KEY"] = os.getenv("GROK_API_KEY", "")

def test_answer_generation():
    """Test answer generation with debug output"""
    print("🔍 Testing Answer Generation...")
    
    test_questions = [
        "What engineering programs are offered?",
        "How are placement opportunities?",
        "What is the admission process?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📍 Test {i}: {question}")
        print("-" * 50)
        
        try:
            answer, confidence, sources = retrieve_answer(question)
            print(f"✅ Answer Generated: {len(answer)} characters")
            print(f"📊 Confidence: {confidence}")
            print(f"📚 Sources: {len(sources)} found")
            print(f"💬 Answer Preview: {answer[:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_answer_generation()
