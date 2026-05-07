"""
Document Processing Hub
========================

Handles PDF question answering, syllabus analysis, form filling assistance, and OCR processing.
Stores all processed documents in MongoDB.
"""

import os
import io
import re
import json
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
import PyPDF2
import pdfplumber
try:
    import docx
    python_docx_available = True
except ImportError:
    python_docx_available = False
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

class DocumentProcessor:
    def __init__(self):
        """Initialize document processor with MongoDB connection"""
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/kongu_chatbot")
        self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Extract database name
        if "/" in self.mongo_uri.split("://")[-1]:
            db_name = self.mongo_uri.split("/")[-1].split("?")[0]
        else:
            db_name = "kongu_chatbot"
        
        self.db = self.client[db_name]
        
        # Collections for document processing
        self.documents_collection = self.db["documents"]
        self.document_qa_collection = self.db["document_qa"]
        self.syllabus_collection = self.db["syllabus"]
        self.forms_collection = self.db["forms"]
        
        # Create indexes
        self.documents_collection.create_index("user_id")
        self.documents_collection.create_index("document_type")
        self.document_qa_collection.create_index("document_id")
        self.syllabus_collection.create_index("document_id")
        self.forms_collection.create_index("document_id")
        
        # Allowed file extensions
        self.allowed_extensions = {'pdf', 'docx', 'doc', 'txt', 'jpg', 'jpeg', 'png', 'tiff'}
        
        print(f"✅ Document Processor initialized with database: {db_name}")
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        text = ""
        try:
            # Try with pdfplumber first (better for tables and formatting)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        print(f"Error extracting text from page: {e}")
                        continue
            
            # If pdfplumber didn't work well, try PyPDF2
            if len(text.strip()) < 100:  # If we got very little text
                print("Trying PyPDF2 as fallback...")
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(pdf_reader.pages)):
                        try:
                            page = pdf_reader.pages[page_num]
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                        except Exception as e:
                            print(f"Error with PyPDF2 page {page_num}: {e}")
                            continue
            
            # If still very little text, try OCR
            if len(text.strip()) < 100:
                print("Trying OCR as last resort...")
                try:
                    # Convert PDF to images and do OCR
                    import pdf2image
                    import easyocr
                    
                    images = pdf2image.convert_from_path(file_path)
                    reader = easyocr.Reader(['en'])
                    
                    for image in images:
                        result = reader.readtext(image)
                        page_text = " ".join([detection[1] for detection in result])
                        text += page_text + "\n"
                        
                except ImportError:
                    print("OCR libraries not available, skipping OCR")
                except Exception as e:
                    print(f"OCR failed: {e}")
            
            print(f"PDF extraction completed. Text length: {len(text)} characters")
            return text.strip()
            
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return None
    
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        if not python_docx_available:
            print("python-docx not available, cannot extract from DOCX")
            return None
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return None
    
    def extract_text_from_txt(self, file_path):
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read().strip()
            except Exception as e2:
                print(f"Error extracting TXT text: {e2}")
                return None
    
    def perform_ocr(self, file_path):
        """Perform OCR on image files"""
        try:
            import easyocr
            reader = easyocr.Reader(['en'])
            result = reader.readtext(file_path)
            text = " ".join([detection[1] for detection in result])
            return text.strip()
        except Exception as e:
            print(f"Error performing OCR: {e}")
            return None
    
    def extract_text(self, file_path, file_type):
        """Extract text from various file types"""
        if file_type == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type in ['docx', 'doc']:
            return self.extract_text_from_docx(file_path)
        elif file_type == 'txt':
            return self.extract_text_from_txt(file_path)
        elif file_type in ['jpg', 'jpeg', 'png', 'tiff']:
            return self.perform_ocr(file_path)
        else:
            return None
    
    def save_document(self, user_id, file, document_type="general"):
        """Save document to MongoDB and extract text"""
        try:
            # Generate secure filename
            filename = secure_filename(file.filename)
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
            
            # Save file temporarily
            temp_path = f"temp_{datetime.now().timestamp()}_{filename}"
            file.save(temp_path)
            
            # Extract text
            extracted_text = self.extract_text(temp_path, file_type)
            
            if not extracted_text:
                os.remove(temp_path)
                return None, "Could not extract text from document"
            
            # Create document record
            document = {
                "user_id": user_id,
                "filename": filename,
                "file_type": file_type,
                "document_type": document_type,
                "extracted_text": extracted_text,
                "file_size": os.path.getsize(temp_path),
                "upload_date": datetime.utcnow(),
                "processed": True
            }
            
            # Save to MongoDB
            result = self.documents_collection.insert_one(document)
            document_id = str(result.inserted_id)
            
            # Clean up temporary file
            os.remove(temp_path)
            
            return document_id, "Document uploaded and processed successfully"
            
        except Exception as e:
            # Clean up temporary file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            return None, f"Error processing document: {str(e)}"
    
    def analyze_syllabus(self, document_id, extracted_text):
        """Analyze syllabus document and extract structured information"""
        try:
            # Extract course information
            syllabus_data = {
                "document_id": document_id,
                "course_name": self._extract_course_name(extracted_text),
                "course_code": self._extract_course_code(extracted_text),
                "credits": self._extract_credits(extracted_text),
                "topics": self._extract_topics(extracted_text),
                "evaluation": self._extract_evaluation(extracted_text),
                "textbooks": self._extract_textbooks(extracted_text),
                "analysis_date": datetime.utcnow()
            }
            
            # Save to MongoDB
            result = self.syllabus_collection.insert_one(syllabus_data)
            
            return str(result.inserted_id), syllabus_data
            
        except Exception as e:
            print(f"Error analyzing syllabus: {e}")
            return None, None
    
    def _extract_course_name(self, text):
        """Extract course name from text"""
        # Look for B.E. patterns first (most common in Indian engineering syllabi)
        be_patterns = [
            r'BACHELOR\s+OF\s+ENGINEERING\s+DEGREE\s+IN\s+([^\n]+)',
            r'B\.E\.\s+DEGREE\s+IN\s+([^\n]+)',
            r'B\.TECH\s+DEGREE\s+IN\s+([^\n]+)',
            r'BACHELOR\s+OF\s+TECHNOLOGY\s+IN\s+([^\n]+)',
            r'B\.E\s+IN\s+([^\n]+)',
            r'B\.TECH\s+IN\s+([^\n]+)',
        ]
        
        for pattern in be_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                course_name = match.group(1).strip()
                # Clean up the course name
                course_name = re.sub(r'\s+', ' ', course_name)  # Multiple spaces to single
                course_name = course_name.upper()
                if len(course_name) > 3:
                    return course_name
        
        # Look for department patterns
        dept_patterns = [
            r'DEPARTMENT\s+OF\s+([^\n]+)',
            r'([A-Z\s&]+ENGINEERING)',
            r'([A-Z\s&]+TECHNOLOGY)',
            r'([A-Z\s&]+SCIENCE)',
            r'([A-Z\s&]+COMPUTER)',
            r'([A-Z\s&]+MECHANICAL)',
            r'([A-Z\s&]+CIVIL)',
            r'([A-Z\s&]+ELECTRICAL)',
            r'([A-Z\s&]+ELECTRONICS)',
        ]
        
        for pattern in dept_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                dept_name = match.group(1).strip()
                dept_name = re.sub(r'\s+', ' ', dept_name)
                if len(dept_name) > 5 and len(dept_name) < 50:
                    return dept_name.upper()
        
        # Look for course name in first few lines
        lines = text.split('\n')[:15]  # Check first 15 lines
        for line in lines:
            line = line.strip().upper()
            # Look for engineering-related keywords
            if any(keyword in line for keyword in [
                'ENGINEERING', 'TECHNOLOGY', 'COMPUTER', 'SCIENCE', 
                'MECHANICAL', 'CIVIL', 'ELECTRICAL', 'ELECTRONICS',
                'INFORMATION TECHNOLOGY', 'IT', 'CS', 'CSE', 'ECE', 'EEE'
            ]):
                if len(line) > 10 and len(line) < 100:
                    # Remove common prefixes
                    line = re.sub(r'^(B\.E\.|B\.TECH|BACHELOR|DEGREE|IN)\s*', '', line).strip()
                    if len(line) > 5:
                        return line
        
        # Fallback patterns
        patterns = [
            r'(?i)course\s*name\s*[:\-]?\s*([^\n]+)',
            r'(?i)subject\s*[:\-]?\s*([^\n]+)',
            r'(?i)title\s*[:\-]?\s*([^\n]+)',
            r'(?i)course\s*[:\-]?\s*([^\n]+)',
            r'(?i)program\s*[:\-]?\s*([^\n]+)',
            r'(?i)degree\s*[:\-]?\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                course_name = match.group(1).strip()
                course_name = re.sub(r'\s+', ' ', course_name)
                if len(course_name) > 3:
                    return course_name
        
        return "Course Name Not Found"
    
    def _extract_course_code(self, text):
        """Extract course code from text"""
        patterns = [
            r'(?i)course\s*code\s*[:\-]?\s*([A-Z0-9]+)',
            r'(?i)subject\s*code\s*[:\-]?\s*([A-Z0-9]+)',
            r'(?i)paper\s*code\s*[:\-]?\s*([A-Z0-9]+)',
            r'(?i)code\s*[:\-]?\s*([A-Z0-9]{3,8})',
            r'\b([A-Z]{2,4}\d{3,4})\b',
            r'\b(\d{2,3}[A-Z]{2,4})\b',
            # Common patterns like CS101, ME201, etc.
            r'\b([A-Z]{2,4}\s*\d{3,4})\b',
            r'\b(\d{3,4}\s*[A-Z]{2,4})\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                course_code = match.strip()
                # Remove spaces between letters and numbers
                course_code = re.sub(r'\s+', '', course_code)
                # Validate course code format
                if re.match(r'^[A-Z]{2,4}\d{3,4}$', course_code, re.IGNORECASE) or \
                   re.match(r'^\d{3,4}[A-Z]{2,4}$', course_code, re.IGNORECASE):
                    return course_code.upper()
        
        return "Course Code Not Found"
    
    def _extract_credits(self, text):
        """Extract credits from text"""
        patterns = [
            r'(?i)credits?\s*[:\-]?\s*(\d+)',
            r'(?i)credit\s*hours?\s*[:\-]?\s*(\d+)',
            r'(?i)(\d+)\s*credits?',
            r'(?i)(\d+)\s*credit\s*hours?',
            r'(?i)total\s*credits?\s*[:\-]?\s*(\d+)',
            r'(?i)course\s*credits?\s*[:\-]?\s*(\d+)',
            r'(?i)semester\s*credits?\s*[:\-]?\s*(\d+)',
            # Look for patterns like "3 Credits" or "4 Credit Hours"
            r'(?i)(\d+)\s*(?:credits?|credit\s*hours?)',
            # Look for credit ranges like "3-4 Credits"
            r'(?i)(\d+)\s*[-–]\s*(\d+)\s*credits?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    # For ranges, take the higher value
                    if len(match.groups()) == 2:
                        return max(int(match.group(1)), int(match.group(2)))
                    else:
                        return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return 0
    
    def _extract_topics(self, text):
        """Extract topics from syllabus"""
        topics = []
        
        # Pattern for numbered lists (1., 2., etc.)
        numbered_pattern = r'\n\s*(\d+\.|\d+\)|\d+\.)\s*([^\n]+)'
        numbered_matches = re.findall(numbered_pattern, text)
        for match in numbered_matches:
            topic = match[1].strip()
            if len(topic) > 5 and len(topic) < 200:  # Reasonable length
                topics.append(topic)
        
        # Pattern for bullet points (•, -, *, etc.)
        bullet_patterns = [
            r'\n\s*[•\-\*]\s*([^\n]+)',
            r'\n\s*o\s+([^\n]+)',
            r'\n\s*▪\s*([^\n]+)',
            r'\n\s*→\s*([^\n]+)'
        ]
        
        for pattern in bullet_patterns:
            bullet_matches = re.findall(pattern, text)
            for match in bullet_matches:
                topic = match.strip()
                if len(topic) > 5 and len(topic) < 200 and topic not in topics:
                    topics.append(topic)
        
        # Pattern for alphabetical lists (a., b., etc.)
        alpha_pattern = r'\n\s*([a-zA-Z]\.|\([a-zA-Z]\))\s*([^\n]+)'
        alpha_matches = re.findall(alpha_pattern, text)
        for match in alpha_matches:
            topic = match[1].strip()
            if len(topic) > 5 and len(topic) < 200 and topic not in topics:
                topics.append(topic)
        
        # Look for topic-related keywords
        topic_keywords = [
            r'(?i)(?:unit|module|chapter|topic|section)\s*\d*[:\-]?\s*([^\n]+)',
            r'(?i)(?:introduction|overview|objective|aim|purpose)[:\-]?\s*([^\n]+)',
            r'(?i)(?:syllabus|curriculum|content)[:\-]?\s*([^\n]+)'
        ]
        
        for pattern in topic_keywords:
            matches = re.findall(pattern, text)
            for match in matches:
                topic = match.strip()
                if len(topic) > 5 and len(topic) < 200 and topic not in topics:
                    topics.append(topic)
        
        # Clean up topics
        cleaned_topics = []
        for topic in topics:
            # Remove common prefixes/suffixes
            topic = re.sub(r'^(?:unit|module|chapter|topic|section)\s*\d*[:\-]?\s*', '', topic, flags=re.IGNORECASE)
            topic = re.sub(r'\s*(?:unit|module|chapter|topic|section)\s*$', '', topic, flags=re.IGNORECASE)
            
            # Remove extra whitespace and punctuation
            topic = re.sub(r'\s+', ' ', topic).strip()
            topic = topic.rstrip('.,;:!')
            
            if len(topic) > 5 and topic not in cleaned_topics:
                cleaned_topics.append(topic)
        
        return cleaned_topics[:25]  # Limit to first 25 topics
    
    def _extract_evaluation(self, text):
        """Extract evaluation criteria"""
        evaluation = []
        
        patterns = [
            r'(?i)evaluation\s*(?:scheme|pattern|criteria)?\s*[:\-]?\s*([^\n]+)',
            r'(?i)assessment\s*(?:scheme|pattern|criteria)?\s*[:\-]?\s*([^\n]+)',
            r'(?i)grading\s*(?:scheme|pattern|criteria)?\s*[:\-]?\s*([^\n]+)',
            r'(?i)examination\s*(?:pattern|scheme)?\s*[:\-]?\s*([^\n]+)',
            r'(?i)internal\s*(?:assessment|evaluation|marks?)\s*[:\-]?\s*([^\n]+)',
            r'(?i)external\s*(?:assessment|evaluation|marks?)\s*[:\-]?\s*([^\n]+)',
            r'(?i)continuous\s*(?:assessment|evaluation)\s*[:\-]?\s*([^\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                eval_item = match.strip()
                if len(eval_item) > 10 and eval_item not in evaluation:
                    evaluation.append(eval_item)
        
        # Look for specific evaluation patterns
        eval_patterns = [
            r'(?i)(?:internal|continuous)\s*(?:assessment|evaluation)\s*[:\-]?\s*(\d+%?)',
            r'(?i)(?:external|final|end\s*term)\s*(?:assessment|evaluation|exam)\s*[:\-]?\s*(\d+%?)',
            r'(?i)(?:quiz|assignment|project|practical|lab)\s*[:\-]?\s*(\d+%?)',
            r'(?i)(?:mid\s*term|midterm|semester)\s*(?:exam|test)\s*[:\-]?\s*(\d+%?)',
            r'(?i)(?:attendance|participation)\s*[:\-]?\s*(\d+%?)'
        ]
        
        for pattern in eval_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                eval_item = f"{match.strip()} marks"
                if eval_item not in evaluation:
                    evaluation.append(eval_item)
        
        # Look for percentage-based evaluation
        percentage_pattern = r'(?i)(\d+%?)\s*(?:for|of|in)?\s*([^\n]{5,50})'
        percentage_matches = re.findall(percentage_pattern, text)
        for match in percentage_matches:
            percent, component = match
            eval_item = f"{percent} {component.strip()}"
            if len(eval_item) > 10 and eval_item not in evaluation:
                evaluation.append(eval_item)
        
        return evaluation[:10]  # Limit to first 10 evaluation items
    
    def _extract_textbooks(self, text):
        """Extract textbook information"""
        textbooks = []
        
        patterns = [
            r'(?i)textbook[s]?\s*[:\-]?\s*([^\n]+)',
            r'(?i)reference[s]?\s*(?:book[s]?)?\s*[:\-]?\s*([^\n]+)',
            r'(?i)book[s]?\s*[:\-]?\s*([^\n]+)',
            r'(?i)prescribed\s*(?:book[s]?|text[s]?)\s*[:\-]?\s*([^\n]+)',
            r'(?i)recommended\s*(?:book[s]?|text[s]?)\s*[:\-]?\s*([^\n]+)',
            r'(?i)reading\s*(?:material[s]?|book[s]?)\s*[:\-]?\s*([^\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                textbook = match.strip()
                if len(textbook) > 10 and textbook not in textbooks:
                    textbooks.append(textbook)
        
        # Look for author patterns
        author_patterns = [
            r'(?i)(?:by|author|editor)\s*[:\-]?\s*([^\n,;]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\((?:19|20)\d{2}\)',
            r'([A-Z][a-z]+\s+[A-Z]\.\s*[A-Z][a-z]+)'
        ]
        
        for pattern in author_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                textbook = f"Author: {match.strip()}"
                if len(textbook) > 10 and textbook not in textbooks:
                    textbooks.append(textbook)
        
        # Look for publication patterns
        pub_patterns = [
            r'(?i)(?:publisher|publication)\s*[:\-]?\s*([^\n,;]+)',
            r'(?i)(?:edition|volume|vol\.)\s*[:\-]?\s*([^\n,;]+)',
            r'(?i)(?:isbn|ISSN)\s*[:\-]?\s*([^\n,;]+)'
        ]
        
        for pattern in pub_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                textbook = f"Publication: {match.strip()}"
                if len(textbook) > 10 and textbook not in textbooks:
                    textbooks.append(textbook)
        
        return textbooks[:8]  # Limit to first 8 textbooks
    
    def answer_document_question(self, user_id, document_id, question):
        """Answer questions about uploaded documents"""
        try:
            # Get document from MongoDB
            document = self.documents_collection.find_one({"_id": ObjectId(document_id), "user_id": user_id})
            
            if not document:
                return None, "Document not found"
            
            document_text = document.get("extracted_text", "")
            
            if not document_text:
                return None, "No text found in document"
            
            # Use Sarvam AI to answer question about document
            from retriever import call_sarvam_api
            
            context = f"Document: {document.get('filename', 'Unknown')}\n\n{document_text}"
            
            answer, error = call_sarvam_api(context, question)
            
            if answer:
                # Save Q&A to MongoDB
                qa_record = {
                    "user_id": user_id,
                    "document_id": document_id,
                    "question": question,
                    "answer": answer,
                    "timestamp": datetime.utcnow()
                }
                
                self.document_qa_collection.insert_one(qa_record)
                
                return answer, "Question answered successfully"
            else:
                return None, f"Failed to get answer: {error}"
                
        except Exception as e:
            return None, f"Error answering question: {str(e)}"
    
    def get_user_documents(self, user_id):
        """Get all documents uploaded by user"""
        try:
            documents = list(self.documents_collection.find({"user_id": user_id}).sort("upload_date", -1))
            
            result = []
            for doc in documents:
                result.append({
                    "id": str(doc["_id"]),
                    "filename": doc["filename"],
                    "file_type": doc["file_type"],
                    "document_type": doc["document_type"],
                    "file_size": doc["file_size"],
                    "upload_date": doc["upload_date"],
                    "processed": doc.get("processed", False)
                })
            
            return result
        except Exception as e:
            print(f"Error getting user documents: {e}")
            return []
    
    def get_document_qa_history(self, user_id, document_id=None):
        """Get Q&A history for documents"""
        try:
            query = {"user_id": user_id}
            if document_id:
                query["document_id"] = document_id
            
            qa_history = list(self.document_qa_collection.find(query).sort("timestamp", -1))
            
            result = []
            for qa in qa_history:
                result.append({
                    "id": str(qa["_id"]),
                    "document_id": qa["document_id"],
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "timestamp": qa["timestamp"]
                })
            
            return result
        except Exception as e:
            print(f"Error getting Q&A history: {e}")
            return []
    
    def get_syllabus_analysis(self, document_id):
        """Get syllabus analysis for a document"""
        try:
            syllabus = self.syllabus_collection.find_one({"document_id": document_id})
            
            if syllabus:
                syllabus["_id"] = str(syllabus["_id"])
                return syllabus
            else:
                return None
        except Exception as e:
            print(f"Error getting syllabus analysis: {e}")
            return None
    
    def delete_document(self, user_id, document_id):
        """Delete a document and all related data"""
        try:
            # Delete document
            result = self.documents_collection.delete_one({"_id": ObjectId(document_id), "user_id": user_id})
            
            if result.deleted_count > 0:
                # Delete related Q&A
                self.document_qa_collection.delete_many({"document_id": document_id})
                
                # Delete syllabus analysis
                self.syllabus_collection.delete_many({"document_id": document_id})
                
                return True, "Document deleted successfully"
            else:
                return False, "Document not found"
                
        except Exception as e:
            return False, f"Error deleting document: {str(e)}"
    
    def close_connection(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()

# Global instance
document_processor = DocumentProcessor()
