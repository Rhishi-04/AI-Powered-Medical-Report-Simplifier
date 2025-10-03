# AI-Powered Medical Report Simplifier - Technical Architecture

## System Architecture Diagram

```mermaid
graph TB
    %% Input Layer
    subgraph "Input Layer"
        A[Text Medical Report] 
        B[Image/PDF Medical Report]
    end
    
    %% API Gateway
    subgraph "FastAPI Application"
        C[FastAPI Server<br/>Port 8000]
        D[API Routes<br/>/process/text<br/>/process/image<br/>/ocr<br/>/normalize<br/>/health]
    end
    
    %% Core Services
    subgraph "Core Services Layer"
        E[OCR Service<br/>Tesseract + pdf2image]
        F[LLM Service<br/>Ollama + Llama-3.2]
        G[Normalizer Service<br/>Test Standardization]
        H[Validator Service<br/>Hallucination Detection]
        I[Summarizer Service<br/>Patient-Friendly Output]
    end
    
    %% Processing Pipeline
    subgraph "Processing Pipeline"
        J[Step 1: OCR/Text Extraction]
        K[Step 2: Test Normalization]
        L[Step 3: Validation & Guardrails]
        M[Step 4: Summary Generation]
    end
    
    %% Output Layer
    subgraph "Output Layer"
        N[Normalized Tests JSON]
        O[Patient-Friendly Summary]
        P[Confidence Scores]
    end
    
    %% External Dependencies
    subgraph "External Dependencies"
        Q[Ollama LLM Server<br/>localhost:11434]
        R[Tesseract OCR Engine]
    end
    
    %% Data Flow
    A --> C
    B --> C
    C --> D
    D --> E
    D --> F
    
    E --> J
    F --> K
    G --> L
    H --> L
    I --> M
    
    J --> K
    K --> L
    L --> M
    
    M --> N
    M --> O
    M --> P
    
    E --> R
    F --> Q
    G --> Q
    H --> Q
    I --> Q
    
    %% Styling
    classDef inputStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef apiStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef serviceStyle fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef pipelineStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef outputStyle fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef externalStyle fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    
    class A,B inputStyle
    class C,D apiStyle
    class E,F,G,H,I serviceStyle
    class J,K,L,M pipelineStyle
    class N,O,P outputStyle
    class Q,R externalStyle
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant OCR
    participant LLM
    participant Normalizer
    participant Validator
    participant Summarizer
    
    Client->>FastAPI: POST /process/text or /process/image
    FastAPI->>OCR: Extract text (if image)
    OCR-->>FastAPI: Raw text + confidence
    
    FastAPI->>Normalizer: Normalize medical tests
    Normalizer->>LLM: Generate structured JSON
    LLM-->>Normalizer: Normalized tests data
    Normalizer-->>FastAPI: Standardized test results
    
    FastAPI->>Validator: Validate for hallucinations
    Validator->>LLM: Check data integrity
    LLM-->>Validator: Validation results
    Validator-->>FastAPI: Confidence scores
    
    FastAPI->>Summarizer: Generate patient summary
    Summarizer->>LLM: Create friendly explanations
    LLM-->>Summarizer: Summary + explanations
    Summarizer-->>FastAPI: Final output
    
    FastAPI-->>Client: Complete response JSON
```

## Processing Pipeline Details

```mermaid
flowchart TD
    Start([Input: Medical Report]) --> InputType{Input Type?}
    
    InputType -->|Text| TextInput[Raw Text]
    InputType -->|Image/PDF| ImageInput[Image/PDF File]
    
    ImageInput --> OCR[OCR Processing<br/>Tesseract + pdf2image]
    OCR --> ExtractedText[Extracted Text + Confidence]
    
    TextInput --> Normalization[Test Normalization<br/>LLM: Llama-3.2]
    ExtractedText --> Normalization
    
    Normalization --> NormalizedTests[Normalized Tests JSON<br/>- Standardized names<br/>- Numeric values<br/>- Units & ranges<br/>- Status indicators]
    
    NormalizedTests --> Validation[Hallucination Validation<br/>LLM: Confidence Check]
    Validation --> ValidatedTests[Validated Results<br/>+ Confidence Scores]
    
    ValidatedTests --> Summary[Patient Summary Generation<br/>LLM: Friendly Explanations]
    Summary --> FinalOutput[Final JSON Response<br/>- Normalized tests<br/>- Patient summary<br/>- Explanations<br/>- Status & confidence]
    
    FinalOutput --> End([Output: Patient-Friendly Report])
    
    %% Error Handling
    OCR -->|OCR Failed| Error1[Error: OCR Failed]
    Normalization -->|LLM Failed| Error2[Error: Normalization Failed]
    Validation -->|Validation Failed| Error3[Error: Validation Failed]
    Summary -->|Summary Failed| Error4[Error: Summary Failed]
    
    Error1 --> ErrorResponse[Error Response JSON]
    Error2 --> ErrorResponse
    Error3 --> ErrorResponse
    Error4 --> ErrorResponse
    
    classDef processStyle fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef errorStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef outputStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    
    class Start,End processStyle
    class Error1,Error2,Error3,Error4,ErrorResponse errorStyle
    class FinalOutput outputStyle
```

## Key Features & Capabilities

### 🔍 **Input Processing**
- **Text Reports**: Direct processing of typed medical reports
- **Image/PDF Reports**: OCR extraction with Tesseract
- **Error Handling**: Robust OCR error detection and recovery

### 🤖 **AI Processing**
- **Local LLM**: Ollama with Llama-3.2 for privacy and data security
- **Medical Normalization**: Standardized test names, values, units
- **Hallucination Detection**: LLM-based validation to prevent false data
- **Patient-Friendly Output**: Simple, non-diagnostic explanations

### 🛡️ **Guardrails & Validation**
- **Confidence Scoring**: OCR and LLM confidence tracking
- **Data Integrity**: Validation against original input
- **Error Recovery**: Graceful handling of processing failures
- **Structured Output**: Consistent JSON schema validation

### 🚀 **Deployment Ready**
- **Docker Support**: Complete containerization
- **Environment Config**: Flexible configuration management
- **API Documentation**: Auto-generated Swagger/ReDoc
- **Health Monitoring**: Built-in health check endpoints

## 🏭 **Future Scope & Industry Scaling**

### ☁️ **Cloud Integration**
- **Azure OpenAI**: Replace local Ollama for enterprise performance
- **Azure Document Intelligence**: Superior OCR accuracy for medical documents
- **Mistral OCR**: Integration when structured JSON output becomes stable 


## Performance Characteristics

- **Processing Time**: 10-30 seconds for typical reports
- **Concurrent Requests**: Supports multiple simultaneous users
- **Memory Usage**: ~2-4GB with Ollama + application
- **Storage**: Minimal (no database required)
- **Scalability**: Horizontal scaling via Docker containers

### 📊 **API Usage**
- **Text Processing**: `POST /process/text` - Complete pipeline (normalization → validation → summary)
- **Image Processing**: `POST /process/image` - Complete pipeline (OCR → normalization → validation → summary)
- **Individual Steps**: `POST /ocr`, `POST /normalize` - For testing individual components

