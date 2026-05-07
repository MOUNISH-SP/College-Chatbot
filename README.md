# 🎓 Kongu Engineering College AI Chatbot

An intelligent AI-powered chatbot system designed specifically for Kongu Engineering College students, featuring advanced document processing, syllabus analysis, and natural language Q&A capabilities.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![MongoDB](https://img.shields.io/badge/MongoDB-5.0%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

### 🤖 AI Chatbot
- **Intelligent Q&A**: Powered by Pinecone vector database and Sarvam AI
- **Context-Aware Responses**: RAG (Retrieval-Augmented Generation) system
- **Natural Language Processing**: Advanced NLP for understanding student queries
- **Real-time Responses**: Fast and accurate answer generation

### 📄 Document Processing Hub
- **Multi-format Support**: PDF, DOCX, TXT, and Image files
- **OCR Integration**: EasyOCR for extracting text from images
- **Smart Text Extraction**: Multiple fallback methods for reliable processing
- **File Management**: Upload, organize, and manage documents efficiently

### 📚 Syllabus Analysis
- **Automatic Extraction**: Course name, code, credits, topics, evaluation criteria
- **Advanced Pattern Recognition**: Handles diverse syllabus formats
- **Indian Engineering Syllabi**: Optimized for Indian educational standards
- **Structured Output**: Clean, organized syllabus information

### 👤 User Management
- **Secure Authentication**: bcrypt password hashing
- **Profile Management**: Personal information and preferences
- **Session Management**: Secure Flask sessions
- **User Dashboard**: Personalized document and Q&A history

### 🎨 Modern UI/UX
- **Responsive Design**: Works on all devices
- **Glassmorphism Design**: Modern, beautiful interface
- **Interactive Elements**: Smooth animations and transitions
- **User-Friendly**: Intuitive navigation and usage

## 🏗️ Architecture

### Backend Technologies
- **Flask**: Web framework for API and routing
- **MongoDB**: NoSQL database for user data, documents, and Q&A history
- **Pinecone**: Vector database for semantic search
- **Sarvam AI**: Natural language processing and response generation

### Frontend Technologies
- **HTML5/CSS3**: Modern semantic markup and styling
- **JavaScript**: Dynamic client-side interactions
- **Bootstrap**: Responsive design framework
- **Glassmorphism UI**: Modern design principles

### AI/ML Components
- **Vector Search**: Pinecone for semantic similarity
- **OCR**: EasyOCR for image text extraction
- **NLP**: Sarvam AI for natural language understanding
- **RAG System**: Retrieval-augmented generation for accurate responses

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running
- Node.js (for frontend dependencies, if needed)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/MOUNISH-SP/College-Chatbot.git
cd College-Chatbot
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Configure MongoDB**
```bash
# Make sure MongoDB is running on localhost:27017
# The database will be created automatically as 'kongu_chatbot'
```

6. **Run the application**
```bash
python app.py
```

7. **Access the application**
```
Open your browser and go to: http://localhost:5000
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# AI Services
SARVAM_API_KEY=your_sarvam_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
GROK_API_KEY=your_grok_api_key_here

# Database
MONGODB_URI=mongodb://localhost:27017/kongu_chatbot

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

### API Keys Setup

1. **Sarvam AI API Key**
   - Visit [Sarvam AI](https://sarvam.ai/)
   - Sign up and get your API key
   - Add it to your `.env` file

2. **Pinecone API Key**
   - Visit [Pinecone](https://www.pinecone.io/)
   - Create an account and get your API key
   - Create an index named `college-chatbot1`
   - Add the API key to your `.env` file

## 📁 Project Structure

```
College-Chatbot/
├── app.py                 # Main Flask application
├── retriever.py           # Pinecone + Sarvam AI integration
├── document_processor.py  # Document processing and OCR
├── auth_db_fixed.py      # User authentication system
├── templates/            # HTML templates
│   ├── index.html        # Main chatbot interface
│   ├── login.html        # Login page
│   ├── signup.html       # Registration page
│   ├── documents.html    # Document management
│   ├── ask_document.html # Document Q&A interface
│   └── profile.html      # User profile
├── pdfs/                 # Sample PDF documents
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
└── README.md            # This file
```

## 🔧 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /signup` - User registration
- `GET /logout` - User logout
- `GET /profile` - User profile
- `POST /update_profile` - Update profile

### Chatbot
- `GET /` - Main chatbot interface
- `POST /home` - Chatbot question processing

### Documents
- `GET /documents` - Document management page
- `POST /upload_document` - Upload new document
- `GET /ask_document/<id>` - Document Q&A interface
- `POST /ask_document_question` - Ask question about document
- `POST /delete_document/<id>` - Delete document

## 🎯 Usage Guide

### For Students
1. **Sign Up**: Create an account with your email and password
2. **Login**: Access the system with your credentials
3. **Chat**: Ask questions about college, courses, and general information
4. **Upload Documents**: Upload syllabi, notes, or study materials
5. **Document Q&A**: Ask specific questions about uploaded documents
6. **Syllabus Analysis**: Automatically extract course information

### For Developers
1. **Extend Features**: Add new AI models or processing capabilities
2. **Customize UI**: Modify templates for different themes
3. **Add APIs**: Integrate with other college systems
4. **Deploy**: Host on cloud platforms for production use

## 🔍 Features in Detail

### Document Processing
- **PDF Processing**: Extract text from PDF files using multiple libraries
- **DOCX Support**: Process Microsoft Word documents
- **Image OCR**: Convert images to text using EasyOCR
- **Fallback Methods**: Multiple extraction techniques for reliability

### Syllabus Analysis
- **Course Information**: Extract course name, code, and credits
- **Topic Extraction**: Identify and organize course topics
- **Evaluation Criteria**: Extract grading and assessment methods
- **Textbook Information**: Extract required and recommended textbooks

### AI Chatbot
- **Vector Search**: Find relevant information using Pinecone
- **Context Understanding**: Process natural language queries
- **Response Generation**: Generate human-like responses
- **Source Attribution**: Show sources for generated answers

## 🛠️ Development

### Adding New Features
1. **Backend**: Add new routes in `app.py`
2. **Database**: Extend models in `auth_db_fixed.py` and `document_processor.py`
3. **Frontend**: Create new templates in the `templates/` folder
4. **AI Integration**: Extend `retriever.py` for new AI capabilities

### Testing
```bash
# Test authentication
python test_auth.py

# Test database connection
python test_mongodb.py

# Test AI integration
python test_sarvam.py

# Debug syllabus analysis
python debug_syllabus.py
```

## 📊 Performance

### Optimizations
- **Database Indexing**: Optimized queries for fast retrieval
- **Caching**: Session management for improved performance
- **Async Processing**: Non-blocking file operations
- **Vector Search**: Fast semantic search with Pinecone

### Scalability
- **Modular Design**: Easy to extend and scale
- **Database Sharding**: Support for large datasets
- **Load Balancing**: Ready for horizontal scaling
- **Cloud Deployment**: Compatible with major cloud platforms

## 🔒 Security

### Implemented Measures
- **Password Hashing**: bcrypt for secure password storage
- **Session Security**: Secure Flask session management
- **Input Validation**: Form validation and sanitization
- **API Key Protection**: Environment variables for sensitive data
- **XSS Protection**: Built-in Flask XSS protection

### Best Practices
- **No Hardcoded Secrets**: All sensitive data in environment variables
- **Secure File Upload**: File type validation and secure storage
- **SQL Injection Prevention**: MongoDB prevents SQL injection
- **HTTPS Ready**: Easy SSL certificate integration

## 🌐 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t college-chatbot .
docker run -p 5000:5000 college-chatbot
```

### Cloud Platforms
- **Heroku**: Easy deployment with Git integration
- **AWS**: Scalable deployment with EC2 and RDS
- **Google Cloud**: Fully managed deployment options
- **Azure**: Enterprise-grade cloud deployment

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Guidelines
- Follow the existing code style
- Add comments for complex logic
- Update documentation for new features
- Test your changes thoroughly

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Sarvam AI** - For providing the amazing AI API
- **Pinecone** - For the powerful vector database
- **Flask** - For the excellent web framework
- **MongoDB** - For the flexible database solution
- **EasyOCR** - For the OCR functionality

## 📞 Contact

- **Project Maintainer**: MOUNISH S P
- **GitHub**: [@MOUNISH-SP](https://github.com/MOUNISH-SP)
- **Email**: [your-email@example.com]

## 🔮 Future Roadmap

### Upcoming Features
- [ ] **Mobile App**: React Native mobile application
- [ ] **Voice Support**: Speech-to-text and text-to-speech
- [ ] **Multi-language**: Support for multiple Indian languages
- [ ] **Analytics**: Advanced usage analytics and insights
- [ ] **Integration**: College ERP system integration
- [ ] **Notifications**: Email and SMS notifications
- [ ] **Collaboration**: Study groups and discussion forums
- [ ] **AI Tutor**: Personalized learning recommendations

### Technical Improvements
- [ ] **Microservices**: Split into microservices architecture
- [ ] **Caching**: Redis for improved performance
- [ ] **Monitoring**: Application performance monitoring
- [ ] **Testing**: Comprehensive test suite
- [ ] **Documentation**: API documentation with Swagger

---

⭐ **Star this repository if it helped you!**

🚀 **Built with ❤️ for Kongu Engineering College students**
