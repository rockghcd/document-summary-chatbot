"""
Document Summary Chatbot - Main Application
A Flask-based web application for document summarization using AI and vector database
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import our utility modules
from utils.document_processor import DocumentProcessor
from utils.ai_processor import AIProcessor

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize AI processor
try:
    ai_processor = AIProcessor()
    print("✅ AI processor initialized successfully")
    if ai_processor.use_vector_db:
        print("✅ Vector database integration enabled")
    else:
        print("⚠️ Vector database not available - using fallback mode")
except Exception as e:
    print(f"❌ Error initializing AI processor: {e}")
    ai_processor = None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    vector_stats = ai_processor.get_vector_stats() if ai_processor else {'vector_db_available': False}
    
    return jsonify({
        'status': 'healthy', 
        'message': 'Document Summary Chatbot is running!',
        'version': '1.0.0',
        'ai_available': ai_processor is not None,
        'vector_db_available': vector_stats.get('vector_db_available', False),
        'vector_stats': vector_stats
    })

@app.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload and processing"""
    try:
        # Check if file was uploaded
        if 'document' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['document']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not DocumentProcessor.allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF, DOCX, and TXT files are allowed.'}), 400
        
        # Validate file size
        if not DocumentProcessor.validate_file_size(len(file.read())):
            return jsonify({'error': 'File too large. Maximum size is 10MB.'}), 400
        
        # Reset file pointer
        file.seek(0)
        
        # Generate unique filename and document ID
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        document_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(file_path)
        
        try:
            # Process document
            text, file_extension = DocumentProcessor.process_document(file_path, file.content_type)
            
            # Generate summary using AI with vector storage
            if ai_processor:
                summary = ai_processor.generate_summary(text, document_id=document_id)
            else:
                return jsonify({'error': 'AI service is not available. Please check your OpenAI API key.'}), 500
            
            # Clean up uploaded file
            os.remove(file_path)
            
            # Return results
            return jsonify({
                'summary': summary,
                'originalText': text[:500] + ('...' if len(text) > 500 else ''),
                'filename': filename,
                'fileType': file_extension,
                'documentId': document_id,
                'vectorDbEnabled': ai_processor.use_vector_db if ai_processor else False
            })
            
        except Exception as e:
            # Clean up file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat questions about documents"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        question = data.get('question')
        document_text = data.get('documentText')
        document_id = data.get('documentId')
        
        print(f"Chat request - Question: {question}")
        print(f"Chat request - Document ID: {document_id}")
        print(f"Chat request - Has document text: {bool(document_text)}")
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Generate answer using AI with vector search
        if ai_processor:
            answer = ai_processor.answer_question(
                question=question,
                document_text=document_text,
                document_id=document_id
            )
            return jsonify({'answer': answer})
        else:
            return jsonify({'error': 'AI service is not available. Please check your OpenAI API key.'}), 500
            
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search_documents():
    """Search across all documents in the vector database"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        query = data.get('query')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        if ai_processor and ai_processor.use_vector_db:
            results = ai_processor.search_documents(query, top_k=top_k)
            return jsonify({'results': results})
        else:
            return jsonify({'error': 'Vector database is not available'}), 500
            
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/documents/<document_id>/chunks', methods=['GET'])
def get_document_chunks(document_id):
    """Get all chunks for a specific document"""
    try:
        if ai_processor and ai_processor.use_vector_db:
            chunks = ai_processor.get_document_chunks(document_id)
            return jsonify({'chunks': chunks})
        else:
            return jsonify({'error': 'Vector database is not available'}), 500
            
    except Exception as e:
        print(f"Get chunks error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document from the vector database"""
    try:
        if ai_processor and ai_processor.use_vector_db:
            success = ai_processor.delete_document(document_id)
            if success:
                return jsonify({'message': 'Document deleted successfully'})
            else:
                return jsonify({'error': 'Failed to delete document'}), 500
        else:
            return jsonify({'error': 'Vector database is not available'}), 500
            
    except Exception as e:
        print(f"Delete document error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    try:
        vector_stats = ai_processor.get_vector_stats() if ai_processor else {'vector_db_available': False}
        
        return jsonify({
            'ai_available': ai_processor is not None,
            'vector_db_available': vector_stats.get('vector_db_available', False),
            'vector_stats': vector_stats
        })
        
    except Exception as e:
        print(f"Stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 10MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting Document Summary Chatbot on port {port}")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"🔧 Debug mode: {debug}")
    
    if ai_processor:
        print("✅ AI processor is ready")
        if ai_processor.use_vector_db:
            print("✅ Vector database integration enabled")
        else:
            print("⚠️ Vector database not available - using fallback mode")
    else:
        print("❌ AI processor is not available - check your OpenAI API key")
    
    app.run(debug=debug, host='0.0.0.0', port=port) 