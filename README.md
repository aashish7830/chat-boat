# 🎓 Collegemate - AI Chatbot for College Students

Collegemate is a Flask-based AI chatbot designed specifically for college students. It provides intelligent responses using OpenAI's GPT-3.5-turbo model and can store and retrieve knowledge using ChromaDB for enhanced context-aware conversations.

## 📁 Project Structure

```
collegemate/
├── backend/
│   ├── app.py              # Flask backend with chat and ingest routes
│   ├── ingest.py           # Command-line script for text ingestion
│   └── requirements.txt    # Python dependencies
├── frontend/
│   └── index.html         # Simple HTML chat interface
├── setup.sh               # Setup script for Linux/macOS
├── run.sh                 # Run script for Linux/macOS
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip3
- OpenAI API key
- Git (optional, for cloning)

### Setup Instructions

#### For Linux/macOS:

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd collegemate
   ```

2. **Run the setup script**
   ```bash
   bash setup.sh
   ```

3. **Configure your OpenAI API key**
   ```bash
   nano .env  # or use your preferred editor
   ```
   Replace `your_openai_api_key_here` with your actual OpenAI API key.

4. **Start the application**
   ```bash
   bash run.sh
   ```

5. **Open the frontend**
   Open `frontend/index.html` in your web browser.

#### For Windows:

1. **Open PowerShell as Administrator**

2. **Navigate to the project directory**
   ```powershell
   cd "C:\path\to\collegemate"
   ```

3. **Create virtual environment**
   ```powershell
   python -m venv venv
   ```

4. **Activate virtual environment**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

5. **Install dependencies**
   ```powershell
   pip install -r backend\requirements.txt
   ```

6. **Create .env file**
   ```powershell
   Copy-Item .env.example .env
   ```

7. **Edit .env file**
   Open `.env` in a text editor and replace `your_openai_api_key_here` with your actual OpenAI API key.

8. **Create necessary directories**
   ```powershell
   New-Item -ItemType Directory -Path "chroma_db" -Force
   New-Item -ItemType Directory -Path "logs" -Force
   ```

9. **Start the application**
   ```powershell
   cd backend
   python app.py
   ```

10. **Open the frontend**
    Open `frontend/index.html` in your web browser.

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
FLASK_ENV=development
FLASK_DEBUG=True
CHROMA_DB_PATH=./chroma_db
AI_MODEL=gpt-3.5-turbo
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=500
HOST=0.0.0.0
PORT=5000
```

### Getting an OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it in your `.env` file

## 📚 Usage

### Web Interface

1. Start the backend server using `bash run.sh` (Linux/macOS) or `python backend/app.py` (Windows)
2. Open `frontend/index.html` in your web browser
3. Type your questions in the chat input and press Enter or click Send

### Command Line Ingestion

Use the `ingest.py` script to add knowledge to the chatbot:

```bash
# Interactive mode
python backend/ingest.py --interactive

# Ingest from file
python backend/ingest.py --file path/to/your/file.txt

# Ingest text directly
python backend/ingest.py --text "Your text content here"

# Ingest with metadata
python backend/ingest.py --text "Your text" --metadata '{"subject": "math", "topic": "calculus"}'
```

### API Endpoints

The Flask backend provides several REST API endpoints:

#### POST `/chat`
Send a message to the chatbot.

**Request:**
```json
{
    "message": "What is calculus?"
}
```

**Response:**
```json
{
    "response": "Calculus is a branch of mathematics...",
    "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### POST `/ingest`
Add text to the knowledge base.

**Request:**
```json
{
    "text": "Text content to store",
    "metadata": {
        "subject": "math",
        "topic": "calculus"
    }
}
```

**Response:**
```json
{
    "message": "Text successfully ingested",
    "id": "uuid-string",
    "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### GET `/stats`
Get collection statistics.

**Response:**
```json
{
    "total_documents": 42,
    "timestamp": "2024-01-01T12:00:00.000000"
}
```

## 🛠️ Development

### Project Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **python-dotenv**: Environment variable management
- **openai**: OpenAI API client
- **chromadb**: Vector database for embeddings
- **sentence-transformers**: Text embeddings
- **numpy**: Numerical computing
- **pandas**: Data manipulation

### Adding New Features

1. **Backend**: Modify `backend/app.py` to add new routes
2. **Frontend**: Update `frontend/index.html` for UI changes
3. **Ingestion**: Extend `backend/ingest.py` for new data sources

### Database Management

ChromaDB automatically creates and manages the vector database in the `chroma_db` directory. The database persists between sessions and contains:

- Document embeddings
- Metadata for each document
- Search indices for fast retrieval

## 🐛 Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Make sure you've created a `.env` file
   - Verify your API key is correct
   - Check that the `.env` file is in the project root

2. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r backend/requirements.txt`

3. **"Failed to connect" in frontend**
   - Make sure the backend server is running
   - Check that the server is running on `http://localhost:5000`

4. **Permission errors on Linux/macOS**
   - Make scripts executable: `chmod +x setup.sh run.sh`

### Logs and Debugging

- Backend logs are displayed in the terminal
- Check the browser console for frontend errors
- ChromaDB logs are stored in the `chroma_db` directory

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the API documentation
3. Open an issue on the project repository

---

**Happy studying with Collegemate! 🎓✨**
