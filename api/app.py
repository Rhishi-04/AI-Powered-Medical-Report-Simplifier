"""
AI-Powered Medical Report Simplifier - Complete Application
All-in-one FastAPI app with models, routes, and main logic.
"""

import logging
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .config import settings
from .services import (
    OCRService,
    NormalizerService,
    ValidatorService,
    SummarizerService
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class TextInput(BaseModel):
    """Request model for text input."""
    text: str = Field(..., description="Raw medical report text")


class OCRResponse(BaseModel):
    """Response model for OCR extraction."""
    raw_text: str = Field(..., description="Extracted raw text from image")
    lines: List[str] = Field(..., description="Line-wise array of extracted text")
    ocr_confidence: float = Field(..., ge=0.0, le=1.0, description="OCR confidence score")


class ReferenceRange(BaseModel):
    """Reference range for a medical test."""
    low: float = Field(..., description="Lower bound of normal range")
    high: float = Field(..., description="Upper bound of normal range")


class Test(BaseModel):
    """Normalized medical test result."""
    name: str = Field(..., description="Standardized test name")
    value: float = Field(..., description="Numeric test value")
    unit: str = Field(..., description="Standardized unit of measurement")
    status: str = Field(..., description="Status: low, normal, high")
    ref_range: ReferenceRange = Field(..., description="Reference range")


class NormalizedTestsResponse(BaseModel):
    """Response model for normalized tests."""
    tests: List[Test] = Field(..., description="List of normalized tests")
    normalization_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class Explanation(BaseModel):
    """Patient-friendly explanation for a test."""
    text: str = Field(..., description="Simple explanation")
    test_name: str = Field(..., description="Associated test name")


class SummaryResponse(BaseModel):
    """Response model for patient-friendly summary."""
    summary: str = Field(..., description="Overall summary of findings")
    explanations: List[Explanation] = Field(..., description="Detailed explanations per test")
    status: str = Field(default="ok", description="Processing status")


class FinalResponse(BaseModel):
    """Final combined response."""
    tests: List[Test] = Field(..., description="Normalized test results")
    summary: str = Field(..., description="Patient-friendly summary")
    explanations: List[Explanation] = Field(..., description="Test explanations")
    status: str = Field(default="ok", description="Processing status")


class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = Field(default="unprocessed", description="Error status")
    reason: str = Field(..., description="Reason for failure")


class ValidationResponse(BaseModel):
    """Response model for validation."""
    status: str = Field(..., description="Validation status: ok or unprocessed")
    reason: Optional[str] = Field(None, description="Reason if validation failed")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Validation confidence")

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Medical Report Simplifier",
    description="Backend service for extracting, normalizing, and simplifying medical reports",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ocr_service = OCRService()
normalizer_service = NormalizerService()
validator_service = ValidatorService()
summarizer_service = SummarizerService()

# ============================================================================
# API ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI-Powered Medical Report Simplifier API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process/text": "Process text input",
            "POST /process/image": "Process image input",
            "POST /ocr": "OCR only (Step 1)",
            "POST /normalize": "Normalize tests (Step 2)",
            "POST /summarize": "Generate summary (Step 3)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/ocr", response_model=OCRResponse)
async def extract_text(file: UploadFile = File(...)):
    """
    Step 1: Extract text from image using OCR.
    
    Args:
        file: Image or PDF file
        
    Returns:
        OCRResponse with raw text, lines, and confidence
    """
    try:
        logger.info(f"OCR request received for file: {file.filename}")
        
        # Read file bytes
        file_bytes = await file.read()
        
        # Determine file type and process accordingly
        if file.content_type.startswith('image/'):
            result = ocr_service.extract_from_image(file_bytes)
        elif file.content_type == 'application/pdf':
            result = ocr_service.extract_from_pdf(file_bytes)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Please upload an image or PDF."
            )
        
        return OCRResponse(**result)
        
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/normalize", response_model=NormalizedTestsResponse)
async def normalize_tests(input_data: TextInput):
    """
    Step 2: Normalize medical tests from raw text.
    
    Args:
        input_data: TextInput with raw medical report text
        
    Returns:
        NormalizedTestsResponse with extracted and normalized tests
    """
    try:
        logger.info("Normalization request received")
        
        result = normalizer_service.normalize_tests(input_data.text)
        
        return NormalizedTestsResponse(**result)
        
    except Exception as e:
        logger.error(f"Normalization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/text")
async def process_text_report(input_data: TextInput):
    """
    Complete pipeline: Process text input through all steps.
    
    Args:
        input_data: TextInput with medical report text
        
    Returns:
        FinalResponse or ErrorResponse
    """
    try:
        logger.info("Text processing pipeline started")
        
        # Step 1: Already have text, skip OCR
        raw_text = input_data.text
        
        # Step 2: Normalize tests
        logger.info("Step 2: Normalizing tests...")
        normalized_result = normalizer_service.normalize_tests(raw_text)
        
        # Step 3: Validate extraction (hallucination check)
        logger.info("Step 3: Validating extraction...")
        validation_result = validator_service.validate_extraction(
            raw_text,
            normalized_result["tests"]
        )
        
        # Check validation status
        if validation_result["status"] == "unprocessed":
            logger.warning(f"Validation failed: {validation_result['reason']}")
            return ErrorResponse(
                status="unprocessed",
                reason=validation_result["reason"]
            )
        
        # Step 4: Generate patient-friendly summary
        logger.info("Step 4: Generating summary...")
        validated_tests = validation_result.get("tests", normalized_result["tests"])
        summary_result = summarizer_service.generate_summary(validated_tests)
        
        # Step 5: Combine results
        final_response = FinalResponse(
            tests=validated_tests,
            summary=summary_result["summary"],
            explanations=summary_result["explanations"],
            status="ok"
        )
        
        logger.info("Text processing completed successfully")
        return final_response
        
    except Exception as e:
        logger.error(f"Text processing failed: {str(e)}")
        return ErrorResponse(
            status="unprocessed",
            reason=f"Processing error: {str(e)}"
        )


@app.post("/process/image")
async def process_image_report(file: UploadFile = File(...)):
    """
    Complete pipeline: Process image input through all steps (OCR + normalization + summary).
    
    Args:
        file: Image or PDF file containing medical report
        
    Returns:
        FinalResponse or ErrorResponse
    """
    try:
        logger.info(f"Image processing pipeline started for file: {file.filename}")
        
        # Step 1: OCR
        logger.info("Step 1: Performing OCR...")
        file_bytes = await file.read()
        
        if file.content_type.startswith('image/'):
            ocr_result = ocr_service.extract_from_image(file_bytes)
        elif file.content_type == 'application/pdf':
            ocr_result = ocr_service.extract_from_pdf(file_bytes)
        else:
            return ErrorResponse(
                status="unprocessed",
                reason=f"Unsupported file type: {file.content_type}"
            )
        
        raw_text = ocr_result["raw_text"]
        
        # Check OCR confidence
        if ocr_result["ocr_confidence"] < 0.3:
            return ErrorResponse(
                status="unprocessed",
                reason=f"OCR confidence too low: {ocr_result['ocr_confidence']}"
            )
        
        # Step 2: Normalize tests
        logger.info("Step 2: Normalizing tests...")
        normalized_result = normalizer_service.normalize_tests(raw_text)
        
        # Step 3: Validate extraction (hallucination check)
        logger.info("Step 3: Validating extraction...")
        validation_result = validator_service.validate_extraction(
            raw_text,
            normalized_result["tests"]
        )
        
        # Check validation status
        if validation_result["status"] == "unprocessed":
            logger.warning(f"Validation failed: {validation_result['reason']}")
            return ErrorResponse(
                status="unprocessed",
                reason=validation_result["reason"]
            )
        
        # Step 4: Generate patient-friendly summary
        logger.info("Step 4: Generating summary...")
        validated_tests = validation_result.get("tests", normalized_result["tests"])
        summary_result = summarizer_service.generate_summary(validated_tests)
        
        # Step 5: Combine results
        final_response = FinalResponse(
            tests=validated_tests,
            summary=summary_result["summary"],
            explanations=summary_result["explanations"],
            status="ok"
        )
        
        logger.info("Image processing completed successfully")
        return final_response
        
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        return ErrorResponse(
            status="unprocessed",
            reason=f"Processing error: {str(e)}"
        )

# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info("Starting AI-Powered Medical Report Simplifier API")
    logger.info(f"Using Ollama (Local LLM): {settings.LLM_MODEL_NAME}")
    logger.info(f"Ollama URL: {settings.OLLAMA_URL}")
    logger.info(f"API running on {settings.API_HOST}:{settings.API_PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info("Shutting down AI-Powered Medical Report Simplifier API")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
