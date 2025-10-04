# AI-Powered Medical Report Simplifier

A backend service that transforms medical reports (text or scanned images) into patient-friendly explanations using AI.

##  Setup Instructions

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

##  Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Process typed medical report (.txt file)
curl -X POST http://localhost:8000/process/file \
  -F "file=@sample_data/abnormal_medical_report.txt"

# Process scanned medical report (image file)
curl -X POST http://localhost:8000/process/file \
  -F "file=@sample_data/sample_medical_report.png"
```

##  API Usage Examples

###  **Main API Endpoint**

** Complete Pipeline** - Single endpoint handles all file types (.txt, image, PDF) through all 4 steps:

```bash
# For typed medical reports (.txt files)
curl -X POST http://localhost:8000/process/file \
  -F "file=@sample_data/abnormal_medical_report.txt"

# For scanned medical reports (image/PDF files)  
curl -X POST http://localhost:8000/process/file \
  -F "file=@sample_data/sample_medical_report.png"
```

** Complete 4-Step Pipeline:**
1. **OCR/Text Extraction** (for images/text/PDFs)
2. **Test Normalization** 
3. **Hallucination Validation**
4. **Patient-Friendly Summary**

###  **Expected Output (Matches Company Requirements)**

**Input:** `CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)`

**Output:**
```json
{
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 10.2,
      "unit": "g/dL",
      "status": "low",
      "ref_range": {"low": 12.0, "high": 15.0}
    },
    {
      "name": "WBC",
      "value": 11200,
      "unit": "/uL",
      "status": "high",
      "ref_range": {"low": 4000, "high": 11000}
    }
  ],
  "summary": "Low hemoglobin and high white blood cell count.",
  "explanations": [
    {
      "text": "Low hemoglobin may relate to anemia.",
      "test_name": "Hemoglobin"
    },
    {
      "text": "High WBC can occur with infections.",
      "test_name": "WBC"
    }
  ],
  "status": "ok"
}
```

###  **Guardrails & Error Handling**

**Hallucination Detection:**
```json
{
  "status": "unprocessed",
  "reason": "hallucinated tests not present in input"
}
```

###  **API Documentation**
- **Interactive API Explorer**: http://localhost:8000/docs
- **Detailed Documentation**: http://localhost:8000/redoc

##  Architecture

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
│   ├── app.py               # FastAPI application + models + 
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
