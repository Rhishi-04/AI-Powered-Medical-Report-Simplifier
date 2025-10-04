# API Usage Examples

## Base URL
```
http://localhost:8000
```

---

## 1. Health Check
```bash
curl -X GET http://localhost:8000/health
```
**Response:**
```json
{"status": "healthy"}
```

---

## 2. Process File Report (Complete 4-Step Pipeline)
```bash
curl -X POST http://localhost:8000/process/file \
  -F "file=@sample_data/abnormal_medical_report.txt"
```

**Response:**
```json
{
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 10.2,
      "unit": "g/dL",
      "status": "low",
      "ref_range": {"low": 12.0, "high": 17.0}
    },
    {
      "name": "WBC",
      "value": 11200,
      "unit": "/uL",
      "status": "high",
      "ref_range": {"low": 4000, "high": 11000}
    }
  ],
  "summary": "Your test results show low hemoglobin and high white blood cell count.",
  "explanations": [
    {
      "text": "Your hemoglobin is lower than normal, which might make you feel tired or weak.",
      "test_name": "Hemoglobin"
    },
    {
      "text": "Your white blood cell count is higher than normal. This can happen during infections.",
      "test_name": "WBC"
    }
  ],
  "status": "ok"
}
```

---

## 3. Process Image Report (Complete 4-Step Pipeline)
```bash
curl -X POST http://localhost:8000/process/file \
  -F "file=@sample_data/sample_medical_report.png"
```
**Response:** Same as text processing above

---

## 4. Test with Sample Data
```bash

#image OCR
curl -X POST http://localhost:8000/process/file \
  -F "file=@sample_data/Gemini_Generated_Image_augn2laugn2laugn.png" \
  --max-time 120

```

---

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/process/file` | POST | Complete 4-step pipeline for all files (.txt, image, PDF) |

---

## Sample Files
- `comprehensive_medical_report.txt` - Normal values
- `abnormal_medical_report.txt` - Abnormal values
- `sample_medical_report.png` - Test image