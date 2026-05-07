import os
import re
import requests
import urllib3
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

# Disable SSL warnings for network bypass
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

THRESHOLD = 0.25
TOP_K = 3


def rewrite_query(query):
    q = query.lower()

    if "department" in q or "programme" in q:
        return query + " BE BTech undergraduate postgraduate courses engineering branches"

    if "placement" in q:
        return query + " placement statistics recruiters internship companies"

    if "admission" in q:
        return query + " admission process eligibility apply application"

    return query


def clean_text(text):
    text = re.sub(r"View Department ➝", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_duplicates(text):
    sentences = text.split(".")
    unique = []

    for s in sentences:
        s = s.strip()
        if s and s not in unique:
            unique.append(s)

    return ". ".join(unique)


def call_sarvam_api(context, question):
    """Call Sarvam AI API with context and question"""
    sarvam_api_key = os.getenv("SARVAM_API_KEY")
    
    if not sarvam_api_key:
        return None, "Sarvam API key not found in .env file"
    
    url = "https://api.sarvam.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {sarvam_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "sarvam-m",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful college enquiry assistant. Answer ONLY using provided context. If answer is not available, say you don't know."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract answer from Sarvam AI response
        if "choices" in result and len(result["choices"]) > 0:
            answer = result["choices"][0]["message"]["content"]
            return answer.strip(), "Success with Sarvam AI"
        else:
            return None, "Invalid response format from Sarvam AI"
            
    except requests.exceptions.RequestException as e:
        return None, f"Sarvam API request failed: {str(e)}"
    except KeyError as e:
        return None, f"Sarvam API response format error: {str(e)}"
    except Exception as e:
        return None, f"Sarvam API error: {str(e)}"


def format_departments(text):
    programs = []
    sentences = text.split("\n")

    for sentence in sentences:
        sentence = sentence.strip()

        if sentence.startswith("B.E") or sentence.startswith("B.Tech") or sentence.startswith("BTech"):
            programs.append(sentence)

    return list(set(programs))


def retrieve_answer(user_question):
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    index = pc.Index("college-chatbot1")

    improved_query = rewrite_query(user_question)

    results = index.search(
        namespace="__default__",
        query={
            "inputs": {"text": improved_query},
            "top_k": TOP_K
        }
    )

    matches = results.get("result", {}).get("hits", [])

    # Add website priority logic
    website_matches = []
    pdf_matches = []

    for match in matches:
        fields = match.get("fields", {})
        source = fields.get("source_filename") or fields.get("url")

        if source and "kongu.ac.in" in source:
            website_matches.append(match)
        else:
            pdf_matches.append(match)

    if website_matches:
        matches = website_matches + pdf_matches

    if not matches:
        return "I couldn't find specific information about that. Could you try asking about departments, admissions, or placements?", 0, []

    best_score = matches[0].get("_score", 0)

    if best_score < THRESHOLD:
        return "I don't have enough information to answer that question accurately. Please visit the official college website or contact administration for details.", best_score, []

    # Combine retrieved chunks into context string
    context_chunks = []
    sources = []

    for match in matches:
        fields = match.get("fields", {})
        text = fields.get("text", "")
        cleaned_text = clean_text(text)
        if cleaned_text:
            context_chunks.append(cleaned_text)

        source = fields.get("source_filename") or fields.get("url")
        if source:
            sources.append(source)

    # Combine all chunks into ONE context string
    context = "\n\n".join(context_chunks)

    # Try to get answer from Sarvam AI
    sarvam_answer, sarvam_error = call_sarvam_api(context, user_question)
    
    if sarvam_answer:
        return sarvam_answer, best_score, list(set(sources))
    else:
        # Fallback to formatted Pinecone answer
        combined_text = remove_duplicates(context)

        if "department" in user_question.lower() or "programme" in user_question.lower():
            programs = format_departments(combined_text)
            if programs:
                # Create horizontal grid layout for programs
                program_html = '<div class="program-grid">'
                for i, program in enumerate(programs):
                    if program.strip():
                        program_html += f'<div class="program-item">• {program.strip()}</div>'
                program_html += '</div>'
                answer = f"Here are the engineering programs available at Kongu Engineering College:\n\n{program_html}"
            else:
                answer = "I found information about various programs. Let me help you with specific details about the department you're interested in."
        else:
            # Format as horizontal bullet points
            sentences = re.split(r'[.!?]+', combined_text)
            bullet_points = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10 and sentence not in bullet_points:
                    bullet_points.append(sentence)
            
            if bullet_points:
                # Add conversational intro based on question type
                q_lower = user_question.lower()
                if "placement" in q_lower:
                    intro = "Based on the latest placement information:"
                elif "admission" in q_lower:
                    intro = "Regarding the admission process:"
                elif "facility" in q_lower:
                    intro = "Here's what I found about campus facilities:"
                else:
                    intro = "Here's the information you requested:"
                
                # Create horizontal bullet layout
                bullet_html = '<div class="bullet-list">'
                for sentence in bullet_points[:5]:
                    bullet_html += f'''
                    <div class="bullet-item">
                        <span class="bullet-icon">•</span>
                        <span class="bullet-content">{sentence}.</span>
                    </div>'''
                bullet_html += '</div>'
                
                answer = f"{intro}\n\n{bullet_html}"
            else:
                answer = "I'd be happy to help you with information about Kongu Engineering College. Could you please specify what you'd like to know about?"

        return answer, best_score, list(set(sources))
