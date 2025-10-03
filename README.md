# AI-Powered Medical Report Simplifier

A backend service that transforms medical reports (text or scanned images) into patient-friendly explanations using AI.

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Tesseract OCR
- Ollama (Local LLM)

### Installation

1. **Install Tesseract OCR**
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   ```

2. **Install Ollama**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama service
   ollama serve
   
   # Pull the model
   ollama pull llama3.2:latest
   ```

3. **Setup Project**
   ```bash
   git clone <repository-url>
   cd AI-Powered-Medical-Report-Simplifier
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file (optional - uses defaults)
   cp .env.example .env
   ```

4. **Run the application**
   ```bash
   source venv/bin/activate
   uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
   ```

API available at: http://localhost:8000

## 🧪 Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Process text medical report
curl -X POST http://localhost:8000/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "CBC: Hemoglobin 14.2 g/dL (Normal), WBC 7,500 /uL (Normal)"}'

# Process image medical report
curl -X POST http://localhost:8000/process/image \
  -F "file=@sample_data/sample_medical_report.png"
```

## 🏗️ Architecture

### Processing Pipeline
```
Input (Text/Image) → OCR → LLM Normalization → Validation → Summarization → Output
```

### Key Components
1. **OCR Service** - Extract text from images/PDFs using Tesseract
2. **LLM Service** - Local Ollama integration for all AI tasks
3. **Normalizer** - Extract & standardize medical tests using LLM
4. **Validator** - Detect hallucinations and validate outputs
5. **Summarizer** - Generate patient-friendly explanations

### Project Structure
```
├── api/                      # Core API package
│   ├── __init__.py          # Package initialization
│   ├── app.py               # FastAPI application + models + routes
│   ├── services.py          # All business logic services
│   └── config.py            # Configuration settings
├── requirements.txt         # Python dependencies
└── sample_data/            # Test data and examples
```

### Technology Stack
- **Framework**: FastAPI
- **LLM**: Llama-3.2 (Local via Ollama)
- **OCR**: Tesseract
- **Validation**: Pydantic
