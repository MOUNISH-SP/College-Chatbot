import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from markupsafe import Markup
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from retriever import retrieve_answer
from auth_db_fixed import auth_db
from document_processor import document_processor
from functools import wraps

app = Flask(__name__)

# Configure session
app.secret_key = os.urandom(24)  # Generate secure secret key

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    # Redirect to login if not authenticated
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')
        
        success, user_data, message = auth_db.authenticate_user(email, password)
        
        if success:
            session['user_id'] = user_data['id']
            session['username'] = user_data['username']
            session['email'] = user_data['email']
            session['full_name'] = user_data.get('full_name', '')
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash(message, 'error')
            return render_template('login.html')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name', '')
        
        # Basic validation
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('signup.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return render_template('signup.html')
        
        # Email validation
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            flash('Please enter a valid email address', 'error')
            return render_template('signup.html')
        
        # Create user
        success, message = auth_db.create_user(username, email, password, full_name)
        
        if success:
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    answer = None
    confidence = None
    sources = None
    question = ""

    if request.method == "POST":
        question = request.form["question"]
        answer, confidence, sources = retrieve_answer(question)
        if answer:
            answer = Markup(answer)  # Safe HTML rendering

    # Get user info for display
    user_info = {
        'username': session.get('username', ''),
        'full_name': session.get('full_name', ''),
        'email': session.get('email', '')
    }

    return render_template(
        "index.html",
        answer=answer,
        confidence=confidence,
        sources=sources,
        question=question,
        user=user_info
    )


@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    user_data = auth_db.get_user_by_id(user_id)
    
    if not user_data:
        flash('User not found', 'error')
        return redirect(url_for('home'))
    
    return render_template('profile.html', user=user_data)


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user_id = session.get('user_id')
    full_name = request.form.get('full_name', '')
    
    success, message = auth_db.update_user_profile(user_id, full_name)
    
    if success:
        session['full_name'] = full_name
        flash('Profile updated successfully!', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('profile'))


@app.route('/documents')
@login_required
def documents():
    user_id = session.get('user_id')
    documents = document_processor.get_user_documents(user_id)
    qa_history = document_processor.get_document_qa_history(user_id)
    
    # Get syllabus analyses
    syllabus_analyses = []
    for doc in documents:
        if doc['document_type'] == 'syllabus':
            analysis = document_processor.get_syllabus_analysis(doc['id'])
            if analysis:
                syllabus_analyses.append(analysis)
    
    user_info = {
        'username': session.get('username', ''),
        'full_name': session.get('full_name', ''),
        'email': session.get('email', '')
    }
    
    return render_template('documents.html', 
                         documents=documents, 
                         qa_history=qa_history,
                         syllabus_analyses=syllabus_analyses,
                         user=user_info)


@app.route('/upload_document', methods=['POST'])
@login_required
def upload_document():
    user_id = session.get('user_id')
    
    # Handle both file input methods
    file = None
    if 'document' in request.files and request.files['document'].filename != '':
        file = request.files['document']
    elif 'document_direct' in request.files and request.files['document_direct'].filename != '':
        file = request.files['document_direct']
    
    document_type = request.form.get('document_type', 'general')
    
    if not file:
        flash('No file selected', 'error')
        return redirect(url_for('documents'))
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('documents'))
    
    if not document_processor.allowed_file(file.filename):
        flash('File type not allowed', 'error')
        return redirect(url_for('documents'))
    
    # Save document and extract text
    document_id, message = document_processor.save_document(user_id, file, document_type)
    
    if document_id:
        # If it's a syllabus, analyze it
        if document_type == 'syllabus':
            document = document_processor.documents_collection.find_one({"_id": ObjectId(document_id)})
            if document:
                document_processor.analyze_syllabus(document_id, document.get('extracted_text', ''))
        
        flash('Document uploaded and processed successfully!', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('documents'))


@app.route('/ask_document_question', methods=['POST'])
@login_required
def ask_document_question():
    user_id = session.get('user_id')
    document_id = request.form.get('document_id')
    question = request.form.get('question')
    
    if not document_id or not question:
        flash('Please select a document and enter a question', 'error')
        return redirect(url_for('documents'))
    
    answer, message = document_processor.answer_document_question(user_id, document_id, question)
    
    if answer:
        flash('Question answered successfully!', 'success')
    else:
        flash(f'Failed to answer question: {message}', 'error')
    
    return redirect(url_for('documents'))


@app.route('/ask_document/<document_id>')
@login_required
def ask_document_form(document_id):
    user_id = session.get('user_id')
    
    # Get document info
    documents = document_processor.get_user_documents(user_id)
    target_doc = None
    for doc in documents:
        if doc['id'] == document_id:
            target_doc = doc
            break
    
    if not target_doc:
        flash('Document not found', 'error')
        return redirect(url_for('documents'))
    
    # Get Q&A history for this document
    qa_history = document_processor.get_document_qa_history(user_id, document_id)
    
    user_info = {
        'username': session.get('username', ''),
        'full_name': session.get('full_name', ''),
        'email': session.get('email', '')
    }
    
    return render_template('ask_document.html', 
                         document=target_doc,
                         qa_history=qa_history,
                         user=user_info)


@app.route('/delete_document/<document_id>', methods=['POST'])
@login_required
def delete_document(document_id):
    user_id = session.get('user_id')
    
    success, message = document_processor.delete_document(user_id, document_id)
    
    if success:
        flash('Document deleted successfully', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('documents'))


if __name__ == "__main__":
    app.run(debug=True)
