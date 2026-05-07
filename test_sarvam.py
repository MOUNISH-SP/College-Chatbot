"""
Test Sarvam AI Integration
===========================

This script tests the Sarvam AI API integration with the RAG system.
"""

import os
from dotenv import load_dotenv
from retriever import retrieve_answer

def test_sarvam_integration():
    """Test Sarvam AI integration with debug output"""
    print("🔍 Testing Sarvam AI Integration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    sarvam_api_key = os.getenv("SARVAM_API_KEY")
    print(f"🔑 Sarvam API Key: {'✅ Found' if sarvam_api_key else '❌ Not found'}")
    
    if sarvam_api_key:
        print(f"   Key length: {len(sarvam_api_key)} characters")
        print(f"   Key preview: {sarvam_api_key[:10]}...{sarvam_api_key[-10:]}")
    
    # Test questions
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
            
            # Check if it's from Sarvam AI or fallback
            if "I don't have enough information" in answer or "I couldn't find" in answer:
                print("⚠️  Low confidence - fallback response")
            elif "<div class=" in answer:
                print("🎨 Formatted HTML response (Pinecone fallback)")
            else:
                print("🤖 Likely Sarvam AI response")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_sarvam_integration()
