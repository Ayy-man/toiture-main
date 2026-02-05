# TOITURELV Cortex - Claude Code Execution Spec

## **Status: ✅ LIVE IN PRODUCTION (2026-02-05)**

**Production URLs:**
- Frontend: `frontend-aymans-projects-eef8e702.vercel.app`
- Backend: `toiture-main-production-d6a5.up.railway.app`

## **Project Context (TL;DR)**

AI estimation system for Quebec roofing company. Three components: (1) Pinecone vector DB with 8,132 embeddings, (2) FastAPI backend with hybrid CBR/ML/LLM estimation, (3) Next.js frontend with Full Quote generation.

## **Current State**

**All Components Live:**
- ✅ 8,132 embeddings in Pinecone (toiturelv-cortex index)
- ✅ FastAPI backend on Railway with `/hybrid-quote` endpoint
- ✅ Next.js frontend on Vercel with Full Quote UI
- ✅ Hybrid CBR + ML + LLM merger system working
- ✅ Work items with labor hours generated
- ✅ Materials and pricing breakdown
- ✅ LLM reasoning explains source selection
- ✅ Feedback system (Accurate/Inaccurate buttons)
- ✅ French/English i18n

## **Phase Goals — ALL COMPLETE ✅**

1. ✅ Upload 8,132 embeddings to Pinecone
2. ✅ Build FastAPI `/estimate` and `/hybrid-quote` endpoints
3. ✅ Create Next.js Full Quote form UI
4. ✅ Wire frontend → backend → Pinecone + ML → LLM merger
5. ✅ Test end-to-end
6. ✅ Deploy FastAPI to Railway
7. ✅ Deploy Next.js to Vercel
8. ✅ Add feedback system (Accurate/Inaccurate)
9. ✅ French/English i18n

**Future Enhancements (Phase 2):**
- Voice AI integration
- GoHighLevel sync
- Google Solar API
- Auto-learning from feedback
- Multi-tenant features

---

## **Technical Spec**

### **Stack**

| Layer | Tech | Why |
|-------|------|-----|
| Vector DB | Pinecone | Managed, fast, free tier sufficient |
| Backend | FastAPI (Python) | Async, embedding handling, OpenRouter integration |
| Frontend | Next.js 14 (React) | Vercel native deployment, modern DX |
| Hosting | Railway (backend) | Easy Python deployment |
| Hosting | Vercel (frontend) | Next.js native, free tier |
| Embeddings | Already generated locally | `paraphrase-multilingual-MiniLm-L12-v2` (384-dim) |
| LLM API | OpenRouter | `mistral-7b` for case revision |

### **API Design**

**Endpoint: `POST /estimate`**

Request:
```json
{
  "roof_sqft": 1500,
  "material": "asphalt_shingle",
  "pitch": "6/12",
  "city": "Montreal",
  "access_difficulty": 3,
  "special_notes": "chimney, second story, winter job"
}
```

Response:
```json
{
  "estimate_low": 12400,
  "estimate_high": 13200,
  "estimate_mid": 12800,
  "confidence": 0.94,
  "unit": "CAD",
  "similar_cases": [
    {
      "case_id": "case_123",
      "address": "123 Rue Example, Montreal",
      "date": "2024-03",
      "sqft": 1480,
      "material": "asphalt_shingle",
      "final_price": 12800,
      "notes": "Similar pitch and size"
    }
  ],
  "reasoning": "Based on 47 similar Montreal shingle jobs from past 18 months. Adjusted +8% for 2-story access complexity.",
  "algorithm_used": "hybrid_cbr_llm",
  "timestamp": "2025-01-18T14:32:00Z"
}
```

**Endpoint: `GET /health`**
Returns `{ "status": "ok", "version": "1.0.0" }`

---

## **File Structure**

```
cortex-project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── estimate.py      # /estimate endpoint logic
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── pinecone_client.py     # Query Pinecone
│   │   │   ├── cbr_engine.py          # Hybrid retrieval + filtering
│   │   │   └── llm_service.py         # OpenRouter calls for revision
│   │   └── models/
│   │       ├── __init__.py
│   │       └── schemas.py      # Pydantic models for request/response
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_estimate.py     # 5 sample jobs
│   ├── .env.example            # Template env vars
│   ├── requirements.txt
│   ├── Dockerfile
│   └── railway.toml            # Railway config
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Home page
│   │   ├── components/
│   │   │   ├── EstimateForm.tsx    # Input form
│   │   │   ├── ResultDisplay.tsx   # Show estimate + cases
│   │   │   └── LoadingSpinner.tsx  # Loading state
│   │   ├── api/
│   │   │   └── estimate/
│   │   │       └── route.ts     # Next.js API route (proxy to FastAPI)
│   │   └── layout.tsx
│   ├── public/
│   ├── styles/
│   │   └── globals.css
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── package.json
│   └── .env.local.example
│
├── data/
│   ├── cbr_cases.json          # 8,293 structured cases
│   ├── cbr_embeddings.json     # 8,132 vectors
│   └── master_quotes_valid.csv # Source
│
└── docs/
    ├── API.md                  # API documentation
    ├── DEPLOYMENT.md           # Railway + Vercel setup
    └── USER_GUIDE.md           # How Laurent uses it
```

---

## **Backend Implementation Details**

### **1. Pinecone Integration (`services/pinecone_client.py`)**

```python
from pinecone import Pinecone

class PineconeClient:
    def __init__(self, api_key: str, index_name: str = "toiturelv-cortex"):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
    
    def query(
        self, 
        vector: list[float], 
        top_k: int = 5,
        filters: dict = None
    ) -> list[dict]:
        """
        Query Pinecone for similar cases.
        
        Args:
            vector: 384-dim query embedding
            top_k: Number of similar cases to return
            filters: Optional metadata filters (material, city, etc)
        
        Returns:
            List of matching cases with metadata
        """
        results = self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter=filters if filters else None
        )
        return results['matches']
```

### **2. CBR Engine (`services/cbr_engine.py`)**

**Responsibility:** Hybrid retrieval (structured → semantic)

```python
class CBREngine:
    def __init__(self, pinecone_client, embedding_model):
        self.pinecone = pinecone_client
        self.embeddings = embedding_model
    
    def retrieve_similar_cases(
        self,
        roof_sqft: int,
        material: str,
        pitch: str,
        city: str,
        special_notes: str = ""
    ) -> list[dict]:
        """
        1. Create query embedding from input
        2. Filter by material + city (structured)
        3. Rank by semantic similarity
        4. Return top 5 with metadata
        """
        # Build query text
        query_text = f"{roof_sqft} sqft {material} roof {pitch} pitch in {city}"
        if special_notes:
            query_text += f" {special_notes}"
        
        # Generate embedding
        query_embedding = self.embeddings.encode(query_text)
        
        # Query Pinecone with filters
        filters = {
            "material": {"$eq": material},
            "city": {"$eq": city}
        }
        
        matches = self.pinecone.query(
            vector=query_embedding,
            top_k=5,
            filters=filters
        )
        
        return matches
```

### **3. LLM Service (`services/llm_service.py`)**

**Responsibility:** Call OpenRouter for case revision (confidence adjustment)

```python
import requests
from typing import dict

class LLMService:
    def __init__(self, api_key: str, model: str = "mistral-7b"):
        self.api_key = api_key
        self.model = model
        self.url = "https://openrouter.ai/api/v1/chat/completions"
    
    def revise_estimate(
        self,
        query_specs: dict,
        similar_cases: list[dict],
        base_estimate: float
    ) -> dict:
        """
        Use Claude/Mistral to analyze why estimate differs from similar cases.
        Return confidence level + reasoning.
        """
        prompt = f"""
You are TOITURELV's pricing expert. Analyze this roof job and similar past jobs.

NEW JOB:
- {query_specs['roof_sqft']} sqft {query_specs['material']} roof
- Pitch: {query_specs['pitch']}
- Location: {query_specs['city']}
- Access: {query_specs['access_difficulty']}/5
- Notes: {query_specs.get('special_notes', 'None')}

SIMILAR PAST JOBS:
{self._format_cases(similar_cases)}

BASE ESTIMATE: ${base_estimate}

RESPOND WITH JSON ONLY:
{{
  "confidence": 0.85,
  "estimate_adjusted": 12800,
  "reasoning": "Brief explanation of estimate",
  "key_differences": ["difference 1", "difference 2"]
}}
"""
        
        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
        )
        
        return response.json()
    
    def _format_cases(self, cases: list[dict]) -> str:
        """Format similar cases for LLM context"""
        formatted = []
        for case in cases:
            formatted.append(f"- {case['sqft']} sqft, ${case['price']}")
        return "\n".join(formatted)
```

### **4. Main API (`routers/estimate.py`)**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.cbr_engine import CBREngine
from services.llm_service import LLMService
from services.pinecone_client import PineconeClient
from datetime import datetime

router = APIRouter()

class EstimateRequest(BaseModel):
    roof_sqft: int
    material: str  # "asphalt_shingle", "metal", "flat", etc
    pitch: str     # "6/12", "8/12", etc
    city: str      # "Montreal", "Laval", etc
    access_difficulty: int = 2  # 1-5 scale
    special_notes: str = ""

class EstimateResponse(BaseModel):
    estimate_low: float
    estimate_high: float
    estimate_mid: float
    confidence: float
    unit: str = "CAD"
    similar_cases: list
    reasoning: str
    algorithm_used: str
    timestamp: str

@router.post("/estimate", response_model=EstimateResponse)
async def get_estimate(request: EstimateRequest):
    """
    Main estimation endpoint.
    
    Flow:
    1. Retrieve similar cases from Pinecone
    2. Calculate base estimate from similar cases
    3. Use LLM to revise estimate and confidence
    4. Return results with reasoning
    """
    try:
        # Initialize services (should be dependency-injected in real app)
        cbr = CBREngine(...)
        llm = LLMService(...)
        
        # Retrieve similar cases
        similar_cases = cbr.retrieve_similar_cases(
            roof_sqft=request.roof_sqft,
            material=request.material,
            pitch=request.pitch,
            city=request.city,
            special_notes=request.special_notes
        )
        
        # Calculate base estimate from similar cases
        prices = [case['price'] for case in similar_cases]
        base_estimate = sum(prices) / len(prices) if prices else 0
        
        # Get LLM revision
        llm_result = llm.revise_estimate(
            query_specs=request.dict(),
            similar_cases=similar_cases,
            base_estimate=base_estimate
        )
        
        # Build response
        return EstimateResponse(
            estimate_low=llm_result['estimate_adjusted'] * 0.95,
            estimate_high=llm_result['estimate_adjusted'] * 1.05,
            estimate_mid=llm_result['estimate_adjusted'],
            confidence=llm_result['confidence'],
            similar_cases=similar_cases[:3],  # Top 3
            reasoning=llm_result['reasoning'],
            algorithm_used="hybrid_cbr_llm",
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## **Frontend Implementation Details**

### **1. Main Form (`components/EstimateForm.tsx`)**

```typescript
'use client'

import { useState } from 'react'
import ResultDisplay from './ResultDisplay'
import LoadingSpinner from './LoadingSpinner'

export default function EstimateForm() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  
  const [formData, setFormData] = useState({
    roof_sqft: 1500,
    material: 'asphalt_shingle',
    pitch: '6/12',
    city: 'Montreal',
    access_difficulty: 3,
    special_notes: ''
  })
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const res = await fetch('/api/estimate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      if (!res.ok) throw new Error('Estimate failed')
      
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="container">
      <form onSubmit={handleSubmit} className="form">
        {/* Input fields for roof_sqft, material, pitch, city, etc */}
      </form>
      
      {loading && <LoadingSpinner />}
      {error && <div className="error">{error}</div>}
      {result && <ResultDisplay result={result} />}
    </div>
  )
}
```

### **2. Next.js API Route (`app/api/estimate/route.ts`)**

Acts as proxy to FastAPI backend:

```typescript
export async function POST(request: Request) {
  const data = await request.json()
  
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  
  const response = await fetch(`${backendUrl}/estimate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  
  return response.json()
}
```

---

## **Environment Variables**

### **Backend (`.env`)**
```
PINECONE_API_KEY=xxx
OPENROUTER_API_KEY=xxx
INDEX_NAME=toiturelv-cortex
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### **Frontend (`.env.local`)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
# In production:
# NEXT_PUBLIC_API_URL=https://cortex-api.railway.app
```

---

## **Testing Requirements**

**5 Sample Jobs (must pass):**

1. **Standard Montreal Shingle, 1500 sqft, 6/12**
   - Expected: $12,000-$14,000 range
   - Similar cases should exist
   
2. **Complex Multi-Story, 2500 sqft, chimney, 8/12**
   - Expected: $18,000-$22,000 range
   - Should trigger access_difficulty premium
   
3. **Rural Laval Metal Roof, 3000 sqft, 4/12**
   - Expected: $16,000-$19,000 range
   - City premium applied
   
4. **Winter Emergency (January), 800 sqft, Elastomere**
   - Expected: 12% seasonal premium
   - Should flag in reasoning
   
5. **Edge Case: Odd geometry, 1200 sqft, flat roof + skylights**
   - Should either estimate with low confidence or escalate

**Validation Gates:**
- ✅ All 5 jobs return estimate within ±15% of Laurent's expectations
- ✅ Confidence scores make sense (>0.90 for common jobs, <0.70 for edge cases)
- ✅ Similar_cases always populated (never empty)
- ✅ Response time <5 seconds per request
- ✅ No API errors or timeouts

---

## **Deployment Targets**

### **Backend → Railway**

```bash
# Railway auto-detects FastAPI + requirements.txt
# Just connect GitHub repo and Railway will:
# 1. Install deps
# 2. Run: uvicorn app.main:app --host 0.0.0.0 --port $PORT
# 3. Assign HTTPS URL (e.g., cortex-api.railway.app)
```

Create `railway.toml`:
```toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### **Frontend → Vercel**

```bash
# Vercel auto-detects Next.js
# Set env var: NEXT_PUBLIC_API_URL=https://cortex-api.railway.app
```

---

## **Success Criteria — ALL MET ✅**

**MVP Complete:**

- ✅ 8,132 embeddings uploaded to Pinecone
- ✅ FastAPI server responds to `/estimate` and `/hybrid-quote`
- ✅ Sample jobs return sensible estimates with work items
- ✅ Next.js Full Quote form submits and displays results
- ✅ Backend deployed to Railway: `toiture-main-production-d6a5.up.railway.app`
- ✅ Frontend deployed to Vercel: `frontend-aymans-projects-eef8e702.vercel.app`
- ✅ End-to-end flow works: Form → FastAPI → CBR + ML → LLM merger → Response
- ✅ Hybrid system combines CBR similar cases with ML predictions
- ✅ LLM reasoning explains estimate sources
- ✅ Feedback system for continuous learning

---

## **Known Constraints & Workarounds**

| Issue | Mitigation |
|-------|------------|
| C-Cube has no API | Using pre-extracted CSV data; refresh via manual export |
| 22% missing city data | Fallback to region-level grouping; mark low confidence |
| 28% missing chimney detection | Ask in form; manual override in special_notes |
| OpenRouter rate limits | Batch requests, cache similar cases for repeat queries |
| Pinecone free tier limits | 8K vectors fits comfortably; no scaling issues for MVP |

---

## **Nice-to-Haves (Out of Scope)**

- Slack bot integration
- Database for logging estimates
- Feedback loop (learn from Laurent's corrections)
- Advanced filtering UI
- Export to PDF
- Multi-language support

---

## **Questions for Claude Code**

When you start, ask yourself:

1. **Is Pinecone API key available?** (Need it in env vars)
2. **Is OpenRouter API key available?** (For LLM calls)
3. **Do we need to rebuild embeddings or use existing?** (Use existing `cbr_embeddings.json`)
4. **Should backend run on localhost:8000 by default?** (Yes)
5. **Should frontend run on localhost:3000 by default?** (Yes)
6. **Do we need Docker for local dev or just Python/Node?** (Python + Node locally; Docker for Railway)

---

## **Execution Instructions for Claude Code**

**DO NOT ASK QUESTIONS.** Execute in this order:

1. Create folder structure (backend/, frontend/, data/, docs/)
2. Create `requirements.txt` for backend deps
3. Create `package.json` for frontend
4. Build backend services in order: pinecone_client.py → cbr_engine.py → llm_service.py → estimate.py
5. Build main.py entry point for FastAPI
6. Build Next.js app structure and components
7. Load embeddings and upload to Pinecone
8. Run local tests with 5 sample jobs
9. Generate documentation

If you hit a blocker (missing env var, API auth), state it clearly and stop.
