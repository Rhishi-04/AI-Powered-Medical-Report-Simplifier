"""
All services for medical report processing in a single file.
"""

import json
import logging
import requests
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io
from typing import Dict, Any, List
from .config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# LLM SERVICE
# ============================================================================

class LLMService:
    """Service for LLM inference using Ollama (local)."""
    
    def __init__(self):
        self.model_name = settings.LLM_MODEL_NAME
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        self.ollama_url = settings.OLLAMA_URL
        self.api_url = f"{self.ollama_url}/api/generate"
    
    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """Generate and parse JSON response from LLM."""
        try:
            # Add JSON instruction to prompt
            json_prompt = f"{prompt}\n\nYou must respond with valid JSON only. Do not include any explanatory text outside the JSON."
            
            payload = {
                "model": self.model_name,
                "prompt": json_prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            logger.info(f"Calling Ollama API: {self.model_name}")
            response = requests.post(self.api_url, json=payload, timeout=settings.LLM_TIMEOUT)
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API failed with status {response.status_code}")
            
            result = response.json()
            response_text = result.get("response", "").strip()
            
            if not response_text:
                logger.error("Empty response from Ollama")
                raise Exception("Empty response from Ollama")
            
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise Exception("No JSON object found in LLM response")
            
            json_str = response_text[start_idx:end_idx + 1]
            parsed_json = json.loads(json_str)
            
            logger.info("Successfully generated and parsed JSON from LLM")
            return parsed_json
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM: {str(e)}")
            raise Exception(f"Invalid JSON from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise Exception(f"LLM generation failed: {str(e)}")


# ============================================================================
# OCR SERVICE
# ============================================================================

class OCRService:
    """Service for OCR text extraction from images and PDFs."""
    
    def __init__(self):
        self.confidence_threshold = settings.OCR_CONFIDENCE_THRESHOLD
    
    def extract_from_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Extract text from image using Tesseract OCR."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            raw_text = pytesseract.image_to_string(image)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
            
            # Split into lines and filter empty lines
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            
            logger.info(f"OCR extraction completed. Confidence: {avg_confidence:.2f}")
            
            return {
                "raw_text": raw_text.strip(),
                "lines": lines,
                "ocr_confidence": round(avg_confidence, 2)
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise Exception(f"OCR failed: {str(e)}")
    
    def extract_from_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text from PDF by converting to images first."""
        try:
            images = convert_from_bytes(pdf_bytes)
            all_text = []
            all_lines = []
            all_confidences = []
            
            # Process each page
            for page_num, image in enumerate(images, 1):
                logger.info(f"Processing PDF page {page_num}")
                
                ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                page_text = pytesseract.image_to_string(image)
                
                confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                if confidences:
                    all_confidences.extend(confidences)
                
                all_text.append(page_text.strip())
                page_lines = [line.strip() for line in page_text.split('\n') if line.strip()]
                all_lines.extend(page_lines)
            
            # Calculate overall confidence
            avg_confidence = sum(all_confidences) / len(all_confidences) / 100.0 if all_confidences else 0.0
            combined_text = "\n".join(all_text)
            
            logger.info(f"PDF OCR extraction completed. Confidence: {avg_confidence:.2f}")
            
            return {
                "raw_text": combined_text,
                "lines": all_lines,
                "ocr_confidence": round(avg_confidence, 2)
            }
            
        except Exception as e:
            logger.error(f"PDF OCR extraction failed: {str(e)}")
            raise Exception(f"PDF OCR failed: {str(e)}")


# ============================================================================
# NORMALIZER SERVICE
# ============================================================================

class NormalizerService:
    """Service for normalizing medical test results using LLM."""
    
    def __init__(self):
        self.llm = LLMService()
    
    def normalize_tests(self, raw_text: str) -> Dict[str, Any]:
        """Extract and normalize medical tests from raw text."""
        try:
            prompt = self._create_normalization_prompt(raw_text)
            
            logger.info("Calling LLM for test normalization")
            result = self.llm.generate_json(prompt)
            
            # Validate response structure
            if "tests" not in result:
                raise Exception("LLM response missing 'tests' field")
            
            if "normalization_confidence" not in result:
                result["normalization_confidence"] = 0.8
            
            # Basic validation and data cleaning
            if not result["tests"]:
                logger.warning("No tests extracted by LLM")
                result["tests"] = []
            else:
                # Filter out incomplete tests that have None values
                cleaned_tests = []
                for test in result["tests"]:
                    # Check if all required fields are present and not None
                    if (test.get("name") and 
                        test.get("value") is not None and 
                        test.get("unit") and 
                        test.get("status") and 
                        test.get("ref_range") and
                        test.get("ref_range", {}).get("low") is not None and
                        test.get("ref_range", {}).get("high") is not None):
                        cleaned_tests.append(test)
                    else:
                        logger.warning(f"Skipping incomplete test: {test}")
                
                result["tests"] = cleaned_tests
                logger.info(f"Filtered to {len(cleaned_tests)} complete tests from {len(result['tests'])} total")
            
            logger.info(f"Normalized {len(result['tests'])} tests")
            return result
            
        except Exception as e:
            logger.error(f"Test normalization failed: {str(e)}")
            raise Exception(f"Normalization failed: {str(e)}")
    
    def _create_normalization_prompt(self, raw_text: str) -> str:
        """Create flexible prompt that works with any medical report."""
        return f"""You are a medical data extraction expert. Extract test results from ANY medical report and return them in EXACT JSON format.

CRITICAL: You MUST return valid JSON that matches this EXACT structure. Every field is required.

INPUT TEXT:
{raw_text}

EXTRACT ONLY tests mentioned in the text above. For each test, provide:
1. Standardized medical name (use full names, not abbreviations)
2. Numeric value (convert OCR errors: O→0, l→1, I→1, remove commas)
3. Standardized unit (mg/dL, g/dL, /uL, U/L, mEq/L, %, etc.)
4. Status: "low", "normal", or "high" based on medical reference ranges
5. Reference range with medically accurate numeric bounds

MEDICAL KNOWLEDGE GUIDELINES:
- Use your medical knowledge to determine appropriate reference ranges
- Consider age, gender, and test type when applicable
- For common tests, use standard medical reference ranges
- For specialized tests, use medically appropriate ranges
- If reference ranges are provided in the text, use those
- If uncertain about a test, use reasonable medical ranges

COMMON MEDICAL TESTS (use these as guidance, not limits):
- Blood counts: WBC, RBC, Hemoglobin, Hematocrit, Platelets
- Metabolic: Glucose, Creatinine, BUN, Electrolytes
- Liver: ALT, AST, ALP, Bilirubin, Albumin
- Cardiac: Troponin, CK-MB, BNP
- Lipid: Total Cholesterol, LDL, HDL, Triglycerides
- Thyroid: TSH, T3, T4, Free T4
- Kidney: Creatinine, BUN, eGFR
- Inflammatory: CRP, ESR, Procalcitonin

REQUIRED JSON FORMAT (copy this structure exactly):
{{
  "tests": [
    {{
      "name": "Standardized Test Name",
      "value": numeric_value,
      "unit": "standardized_unit",
      "status": "low|normal|high",
      "ref_range": {{
        "low": numeric_lower_bound,
        "high": numeric_upper_bound
      }}
    }}
  ],
  "normalization_confidence": 0.0_to_1.0
}}

RULES:
- ALL numeric values must be floats (e.g., 10.2, not 10)
- ALL reference range values must be floats (e.g., 12.0, not 12)
- Test names must be full medical names (e.g., "Hemoglobin" not "Hb")
- Units must be standardized medical units
- Status must be "low", "normal", or "high" based on medical knowledge
- Confidence must be between 0.0 and 1.0
- Extract tests from ANY medical specialty (cardiology, neurology, oncology, etc.)
- ONLY include tests that have complete information (name, value, unit)
- SKIP incomplete entries, headers, or partial data
- If a test entry is missing values, DO NOT include it in the results

EXAMPLES OF FLEXIBLE EXTRACTION:
- "Hb: 8.5 g/dL" → "Hemoglobin: 8.5 g/dL (low, ref: 12.0-17.0)"
- "Troponin I: 0.15 ng/mL" → "Troponin I: 0.15 ng/mL (high, ref: 0.0-0.04)"
- "TSH: 8.2 mIU/L" → "Thyroid Stimulating Hormone: 8.2 mIU/L (high, ref: 0.4-4.0)"

Extract tests from the input text using your medical knowledge. Return ONLY the JSON object. No other text."""


# ============================================================================
# VALIDATOR SERVICE
# ============================================================================

class ValidatorService:
    """Service for validating extracted tests against original text using LLM."""
    
    def __init__(self):
        self.llm = LLMService()
        self.confidence_threshold = settings.VALIDATION_CONFIDENCE_THRESHOLD
    
    def validate_extraction(self, original_text: str, extracted_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that extracted tests are present in original text using LLM."""
        try:
            if not extracted_tests:
                return {
                    "status": "unprocessed",
                    "reason": "No tests extracted from input",
                    "confidence": 0.0
                }
            
            prompt = self._create_validation_prompt(original_text, extracted_tests)
            
            logger.info("Calling LLM for hallucination validation")
            result = self.llm.generate_json(prompt)
            
            if "status" not in result:
                raise Exception("LLM validation response missing 'status' field")
            
            if result["status"] == "unprocessed":
                logger.warning(f"Validation failed: {result.get('reason', 'Unknown reason')}")
            else:
                logger.info("Validation passed - no hallucinations detected")
            
            # Return validation result with original tests preserved
            validation_response = {
                "status": result["status"],
                "reason": result.get("reason"),
                "confidence": result.get("confidence", 0.0)
            }
            
            # Only include tests if validation passed
            if result["status"] == "ok":
                validation_response["tests"] = extracted_tests
            
            return validation_response
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return {
                "status": "unprocessed",
                "reason": f"Validation error: {str(e)}",
                "confidence": 0.0
            }
    
    def _create_validation_prompt(self, original_text: str, extracted_tests: List[Dict[str, Any]]) -> str:
        """Create enhanced validation prompt with confidence scoring."""
        tests_json = json.dumps(extracted_tests, indent=2)
        
        return f"""You are a medical data validation expert. Verify extracted test results against the original text and provide confidence scores.

VALIDATION CRITERIA:
1. Test Name Verification: Does the test name (or abbreviation) appear in original text?
2. Value Verification: Does the numeric value appear near the test name?
3. Medical Accuracy: Is this a real medical test with reasonable values?
4. OCR Error Tolerance: Account for common OCR errors (O→0, l→1, I→1, etc.)

ORIGINAL TEXT:
{original_text}

EXTRACTED TESTS TO VALIDATE:
{tests_json}

VALIDATION TASK:
For each test, score confidence (0.0-1.0) based on:
- 1.0: Perfect match with clear evidence
- 0.8-0.9: Good match with minor OCR errors
- 0.6-0.7: Reasonable match with some uncertainty
- 0.3-0.5: Weak evidence, possible hallucination
- 0.0-0.2: No evidence, likely fabricated

MEDICAL ABBREVIATIONS (acceptable):
- Hb, Hgb → Hemoglobin
- WBC → White Blood Cells
- RBC → Red Blood Cells
- Plt → Platelets
- Gluc → Glucose
- Chol → Cholesterol
- Creat → Creatinine
- ALT, SGPT → Alanine Aminotransferase
- AST, SGOT → Aspartate Aminotransferase

RESPONSE FORMAT:
{{
  "status": "ok" or "unprocessed",
  "reason": "explanation if status is unprocessed",
  "confidence": overall_confidence_0_to_1,
  "test_validations": [
    {{
      "test_name": "exact_name_from_input",
      "is_valid": true/false,
      "confidence": 0.0_to_1.0,
      "evidence": "brief explanation of evidence found"
    }}
  ]
}}

DECISION RULES:
- If ALL tests have confidence ≥ 0.6: status = "ok"
- If ANY test has confidence < 0.4: status = "unprocessed"
- Overall confidence = average of individual test confidences

Validate each test and return only valid JSON."""


# ============================================================================
# SUMMARIZER SERVICE
# ============================================================================

class SummarizerService:
    """Service for generating patient-friendly summaries using LLM."""
    
    def __init__(self):
        self.llm = LLMService()
    
    def generate_summary(self, normalized_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate patient-friendly summary and explanations."""
        try:
            if not normalized_tests:
                return {
                    "summary": "No test results to summarize.",
                    "explanations": [],
                    "status": "ok"
                }
            
            prompt = self._create_summary_prompt(normalized_tests)
            
            logger.info("Calling LLM for summary generation")
            result = self.llm.generate_json(prompt)
            
            if "summary" not in result or "explanations" not in result:
                raise Exception("LLM response missing required fields")
            
            if "status" not in result:
                result["status"] = "ok"
            
            logger.info(f"Generated summary with {len(result['explanations'])} explanations")
            return result
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            raise Exception(f"Summarization failed: {str(e)}")
    
    def _create_summary_prompt(self, normalized_tests: List[Dict[str, Any]]) -> str:
        """Create prompt for summary generation."""
        tests_json = json.dumps(normalized_tests, indent=2)
        
        return f"""You are a medical communication expert. Your task is to create patient-friendly explanations of medical test results without providing medical diagnoses.

IMPORTANT GUIDELINES:
1. Use simple, everyday language
2. Focus on what the results mean, not medical diagnoses
3. Be empathetic and non-alarming
4. Only explain tests that are provided in the input
5. DO NOT add information about tests not in the input
6. For abnormal results (low/high), provide gentle context
7. Avoid medical jargon
8. Do not provide treatment recommendations
9. Encourage consulting with healthcare provider

NORMALIZED TEST RESULTS:
{tests_json}

YOUR TASK:
1. Create a brief overall summary (1-2 sentences) highlighting any abnormal findings
2. For each test with abnormal status (low/high), provide a simple explanation
3. Do not explain normal tests unless particularly relevant

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
  "summary": "Brief overall summary of findings",
  "explanations": [
    {{
      "text": "Simple explanation for patients",
      "test_name": "Test Name"
    }}
  ],
  "status": "ok"
}}

EXAMPLE OUTPUT:
{{
  "summary": "Your test results show low hemoglobin and high white blood cell count.",
  "explanations": [
    {{
      "text": "Your hemoglobin is lower than normal, which might make you feel tired or weak. This can be related to anemia. Your doctor can help determine the cause.",
      "test_name": "Hemoglobin"
    }},
    {{
      "text": "Your white blood cell count is slightly higher than normal. This can happen during infections or inflammation. Your doctor will help interpret this in context.",
      "test_name": "WBC"
    }}
  ],
  "status": "ok"
}}

Now generate the patient-friendly summary. Return only valid JSON."""
