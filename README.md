# Document Summary Chatbot 🤖

A modern, AI-powered chatbot built with Python Flask that takes documents as input and provides intelligent summaries and answers questions about the content.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd document-summary-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   ```
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   FLASK_DEBUG=True
   SECRET_KEY=your_secret_key_here
   PORT=5000
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
document-summary-chatbot/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── README.md             # This file
├── test_app.py           # Test script
├── utils/                # Utility modules
│   ├── __init__.py       # Package initialization
│   ├── document_processor.py  # Document text extraction
│   └── ai_processor.py   # OpenAI API integration
├── templates/            # HTML templates
│   └── index.html        # Main application page
├── static/               # Static files
│   ├── css/
│   │   └── styles.css    # Modern CSS styling
│   └── js/
│       └── script.js     # Frontend JavaScript
└── uploads/              # Temporary file storage
```

## ✅ Completed Features

- [x] **Basic Flask Setup** - Application structure and configuration
- [x] **Document Processing** - PDF, DOCX, TXT text extraction
- [x] **AI Integration** - OpenAI API for summarization and chat
- [x] **Frontend Templates** - Beautiful HTML interface
- [x] **Modern CSS Styling** - Responsive design with gradients
- [x] **JavaScript Interactivity** - Drag-and-drop, chat functionality
- [x] **API Endpoints** - File upload and chat endpoints
- [x] **Error Handling** - Comprehensive validation and error messages
- [x] **Security Features** - File validation, size limits, cleanup
- [x] **Testing** - Basic test suite

## 🎯 Features

### **Document Processing**
- **Multi-format Support**: PDF, DOCX, TXT files
- **Text Extraction**: Automatic text extraction from various formats
- **File Validation**: Type and size validation (10MB limit)
- **Security**: Secure file handling with cleanup

### **AI-Powered Features**
- **Document Summarization**: Intelligent summaries using GPT-3.5-turbo
- **Interactive Chat**: Ask questions about uploaded documents
- **Context-Aware Responses**: AI understands document content
- **Token Management**: Handles large documents efficiently

### **Modern UI/UX**
- **Beautiful Design**: Gradient backgrounds and smooth animations
- **Drag-and-Drop**: Easy file upload interface
- **Responsive Layout**: Works on all devices
- **Real-time Feedback**: Loading states and error messages
- **Copy to Clipboard**: Easy copying of summaries and responses

### **Technical Features**
- **RESTful API**: Clean endpoint design
- **Error Handling**: Comprehensive error management
- **File Cleanup**: Automatic temporary file removal
- **CORS Support**: Cross-origin request handling
- **Health Monitoring**: Application status endpoints

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **AI**: OpenAI GPT-3.5-turbo
- **Document Processing**: PyPDF2, python-docx
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Modern CSS with gradients and animations
- **Icons**: Font Awesome
- **Typography**: Google Fonts (Inter)

## 📋 API Endpoints

### `GET /`
Serves the main application page.

### `GET /health`
Health check endpoint.
```json
{
  "status": "healthy",
  "message": "Document Summary Chatbot is running!",
  "version": "1.0.0",
  "ai_available": true
}
```

### `POST /upload`
Upload and process a document.
- **Content-Type**: `multipart/form-data`
- **Body**: `document` (file)
- **Response**:
```json
{
  "summary": "Document summary...",
  "originalText": "First 500 characters...",
  "filename": "document.pdf",
  "fileType": ".pdf"
}
```

### `POST /chat`
Ask questions about uploaded documents.
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "question": "What are the main points?",
  "documentText": "Full document text..."
}
```
- **Response**:
```json
{
  "answer": "AI-generated answer..."
}
```

## 🔑 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes | - |
| `FLASK_DEBUG` | Enable debug mode | No | True |
| `SECRET_KEY` | Flask secret key | No | dev-secret-key |
| `PORT` | Server port | No | 5000 |

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
python test_app.py
```

This will test:
- Health check endpoint
- Home page loading
- Error handling
- API validation

## 📝 Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Upload a document**
   - Drag and drop a file or click to browse
   - Supported: PDF, DOCX, TXT (max 10MB)

3. **Get AI summary**
   - Automatic document analysis
   - Comprehensive summary generation

4. **Ask questions**
   - Use the chat interface
   - Get detailed answers about the document

5. **Copy responses**
   - Click "Copy" button for summaries
   - Easy sharing of results

## 🚨 Troubleshooting

### Common Issues

**"AI service is not available"**
- Check your OpenAI API key in `.env`
- Verify the API key is valid and has credits

**"File too large"**
- Ensure file is under 10MB
- Compress or split large documents

**"Invalid file type"**
- Only PDF, DOCX, and TXT files are supported
- Check file extension and format

**"No text could be extracted"**
- Some PDFs may be image-based
- Try converting to text format first

### Getting Help

1. Check the console for error messages
2. Verify your OpenAI API key
3. Ensure all dependencies are installed
4. Check file format and size requirements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Built with ❤️ using Python Flask and OpenAI**

*Ready to process your documents with AI! 🚀* 