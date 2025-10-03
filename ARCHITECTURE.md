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
        D[API Routes<br/>/process/text<br/>/process/image<br/>/health]
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

## Component Architecture

```mermaid
graph LR
    subgraph "API Package (api/)"
        A[app.py<br/>FastAPI + Routes + Models]
        B[services.py<br/>Business Logic]
        C[config.py<br/>Settings]
        D[__init__.py<br/>Package Init]
    end
    
    subgraph "Configuration"
        E[.env<br/>Environment Variables]
        F[requirements.txt<br/>Dependencies]
    end
    
    subgraph "Deployment"
        G[Dockerfile<br/>Container Config]
        H[docker-compose.yml<br/>Multi-service Setup]
    end
    
    subgraph "Documentation"
        I[README.md<br/>Setup & Usage]
        J[ARCHITECTURE.md<br/>Technical Docs]
    end
    
    A --> B
    A --> C
    B --> C
    C --> E
    
    classDef packageStyle fill:#e3f2fd,stroke:#0277bd,stroke-width:2px
    classDef configStyle fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef deployStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef docStyle fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class A,B,C,D packageStyle
    class E,F configStyle
    class G,H deployStyle
    class I,J docStyle
```

## Technology Stack

```mermaid
graph TB
    subgraph "Frontend/Client"
        A[curl/Postman<br/>API Testing]
        B[Web Browser<br/>Swagger UI]
    end
    
    subgraph "Backend Framework"
        C[FastAPI<br/>Python Web Framework]
        D[Uvicorn<br/>ASGI Server]
    end
    
    subgraph "AI/ML Services"
        E[Ollama<br/>Local LLM Server]
        F[Llama-3.2<br/>Language Model]
        G[Tesseract<br/>OCR Engine]
    end
    
    subgraph "Data Processing"
        H[Pydantic<br/>Data Validation]
        I[pdf2image<br/>PDF Processing]
        J[Pillow<br/>Image Processing]
    end
    
    subgraph "Infrastructure"
        K[Docker<br/>Containerization]
        L[Python 3.8+<br/>Runtime]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    C --> G
    E --> F
    C --> H
    C --> I
    C --> J
    K --> L
    
    classDef clientStyle fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px
    classDef backendStyle fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef aiStyle fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    classDef dataStyle fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef infraStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A,B clientStyle
    class C,D backendStyle
    class E,F,G aiStyle
    class H,I,J dataStyle
    class K,L infraStyle
```

## API Endpoints Structure

```mermaid
graph TD
    A[FastAPI Application<br/>localhost:8000] --> B[GET /]
    A --> C[GET /health]
    A --> D[POST /process/text]
    A --> E[POST /process/image]
    A --> F[POST /ocr]
    A --> G[POST /normalize]
    A --> H[POST /summarize]
    A --> I[GET /docs]
    A --> J[GET /redoc]
    
    B --> K[API Information]
    C --> L[Health Check]
    D --> M[Complete Text Pipeline]
    E --> N[Complete Image Pipeline]
    F --> O[OCR Only]
    G --> P[Normalization Only]
    H --> Q[Summary Only]
    I --> R[Swagger Documentation]
    J --> S[ReDoc Documentation]
    
    classDef endpointStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef docStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class B,C,D,E,F,G,H endpointStyle
    class I,J,K,L,M,N,O,P,Q,R,S docStyle
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

## Deployment Architecture

```mermaid
graph TB
    subgraph "Local Development"
        A[Developer Machine]
        B[Python Virtual Environment]
        C[Ollama Local Server]
        D[FastAPI Application]
    end
    
    subgraph "Docker Deployment"
        E[Docker Container]
        F[Ollama Service]
        G[App Service]
        H[Shared Network]
    end
    
    subgraph "Cloud Deployment Options"
        I[AWS EC2]
        J[Google Cloud Run]
        K[Azure Container Instances]
        L[Heroku]
    end
    
    A --> B
    B --> D
    C --> D
    D --> E
    
    E --> F
    E --> G
    F --> H
    G --> H
    
    E --> I
    E --> J
    E --> K
    E --> L
    
    classDef localStyle fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef dockerStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef cloudStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class A,B,C,D localStyle
    class E,F,G,H dockerStyle
    class I,J,K,L cloudStyle
```

## Key Features & Capabilities

### 🔍 **Input Processing**
- **Text Reports**: Direct processing of typed medical reports
- **Image/PDF Reports**: OCR extraction with Tesseract
- **Error Handling**: Robust OCR error detection and recovery

### 🤖 **AI Processing**
- **Local LLM**: Ollama with Llama-3.2 for privacy
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

## Performance Characteristics

- **Processing Time**: 10-30 seconds for typical reports
- **Concurrent Requests**: Supports multiple simultaneous users
- **Memory Usage**: ~2-4GB with Ollama + application
- **Storage**: Minimal (no database required)
- **Scalability**: Horizontal scaling via Docker containers
