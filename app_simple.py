"""
Simplified MultiToolAPI - Basic Working Version
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MultiToolAPI - Simplified",
    description="Intelligent Client Analysis and Solution Generation System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

# Pydantic models
class Client(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None

class ScrapingRequest(BaseModel):
    url: str
    strategy: str = "requests"

class AnalysisRequest(BaseModel):
    client_data: Client
    requirements: str
    goals: List[str]

# In-memory storage (for demo purposes)
clients_db = []
scraped_data_db = []

@app.get("/")
async def root():
    return {
        "message": "MultiToolAPI - Simplified Version",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "gemini_configured": bool(gemini_api_key),
        "clients_count": len(clients_db)
    }

@app.post("/clients/")
async def create_client(client: Client):
    """Create a new client"""
    client_dict = client.model_dump()
    client_dict["id"] = len(clients_db) + 1
    clients_db.append(client_dict)
    return {"message": "Client created successfully", "client_id": client_dict["id"]}

@app.get("/clients/")
async def get_clients():
    """Get all clients"""
    return {"clients": clients_db}

@app.get("/clients/{client_id}")
async def get_client(client_id: int):
    """Get a specific client"""
    for client in clients_db:
        if client["id"] == client_id:
            return client
    raise HTTPException(status_code=404, detail="Client not found")

@app.post("/scraping/scrape")
async def scrape_website(request: ScrapingRequest):
    """Scrape a website"""
    try:
        response = requests.get(request.url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic information
        scraped_data = {
            "url": request.url,
            "title": soup.title.string if soup.title else "",
            "meta_description": soup.find('meta', attrs={'name': 'description'}).get('content', '') if soup.find('meta', attrs={'name': 'description'}) else "",
            "headings": [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])],
            "links": [{"text": a.get_text().strip(), "href": a.get('href', '')} for a in soup.find_all('a', href=True)],
            "text_content": soup.get_text().strip(),
            "images": [{"src": img.get('src', ''), "alt": img.get('alt', '')} for img in soup.find_all('img')]
        }
        
        scraped_data_db.append(scraped_data)
        
        return {
            "message": "Website scraped successfully",
            "data": scraped_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.post("/analysis/analyze")
async def analyze_client(request: AnalysisRequest):
    """Analyze client data and generate insights"""
    
    try:
        # Prepare context for analysis
        context = f"""
        CLIENT INFORMATION:
        Name: {request.client_data.name}
        Company: {request.client_data.company}
        Website: {request.client_data.website}
        Industry: {request.client_data.industry}
        Description: {request.client_data.description}
        
        REQUIREMENTS:
        {request.requirements}
        
        GOALS:
        {', '.join(request.goals)}
        """
        
        # Try Gemini AI first
        if model:
            try:
                prompt = f"""
                As a business analyst and consultant, analyze the following client data and provide comprehensive insights:
                
                {context}
                
                Please provide a detailed analysis including:
                1. Business Overview and Industry Analysis
                2. Strengths and Weaknesses
                3. Opportunities and Threats
                4. Key Recommendations
                5. Actionable Next Steps
                
                Format your response as a structured analysis with clear sections and actionable insights.
                """
                
                response = model.generate_content(prompt)
                
                return {
                    "message": "AI Analysis completed successfully",
                    "analysis": response.text,
                    "client_id": request.client_data.name,
                    "analysis_type": "AI-powered"
                }
            except Exception as e:
                # Fall back to rule-based analysis if AI fails
                pass
        
        # Fallback: Rule-based analysis
        analysis = generate_rule_based_analysis(request.client_data, request.requirements, request.goals)
        
        return {
            "message": "Analysis completed successfully (Rule-based)",
            "analysis": analysis,
            "client_id": request.client_data.name,
            "analysis_type": "Rule-based"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def generate_rule_based_analysis(client_data, requirements, goals):
    """Generate rule-based analysis as fallback"""
    
    # Industry-specific insights
    industry_insights = {
        "Technology": {
            "strengths": ["High innovation potential", "Scalable business model", "Digital-first approach"],
            "opportunities": ["AI integration", "Cloud migration", "Digital transformation"],
            "recommendations": ["Focus on user experience", "Implement agile methodologies", "Invest in cybersecurity"]
        },
        "Aviation": {
            "strengths": ["Specialized expertise", "Safety-focused operations", "Regulatory compliance"],
            "opportunities": ["Digital maintenance systems", "Customer experience enhancement", "Sustainability initiatives"],
            "recommendations": ["Modernize fleet management", "Enhance customer portals", "Implement predictive maintenance"]
        },
        "Healthcare": {
            "strengths": ["Regulatory expertise", "Patient care focus", "Medical knowledge"],
            "opportunities": ["Telemedicine expansion", "AI diagnostics", "Patient engagement platforms"],
            "recommendations": ["Digital health integration", "Patient data security", "Workflow optimization"]
        }
    }
    
    # Get industry-specific insights
    industry = client_data.industry or "General"
    insights = industry_insights.get(industry, industry_insights["Technology"])
    
    # Generate analysis
    analysis = f"""
# BUSINESS ANALYSIS REPORT
## Client: {client_data.name} - {client_data.company}

### 1. BUSINESS OVERVIEW
**Company:** {client_data.company}
**Industry:** {industry}
**Website:** {client_data.website or 'Not provided'}
**Description:** {client_data.description or 'No description provided'}

### 2. REQUIREMENTS ANALYSIS
**Primary Requirements:** {requirements}

**Goals Assessment:**
{chr(10).join([f"• {goal}" for goal in goals])}

### 3. STRENGTHS & OPPORTUNITIES
**Key Strengths:**
{chr(10).join([f"• {strength}" for strength in insights['strengths']])}

**Growth Opportunities:**
{chr(10).join([f"• {opportunity}" for opportunity in insights['opportunities']])}

### 4. STRATEGIC RECOMMENDATIONS
**Immediate Actions (0-3 months):**
• Conduct comprehensive website audit
• Implement analytics tracking
• Develop content strategy
• Set up social media presence

**Medium-term Goals (3-12 months):**
• Optimize for search engines
• Implement lead generation systems
• Develop customer feedback mechanisms
• Create automated marketing workflows

**Long-term Vision (12+ months):**
• Establish thought leadership in {industry.lower()}
• Build strategic partnerships
• Expand digital capabilities
• Implement advanced analytics

### 5. DIGITAL TRANSFORMATION ROADMAP
**Phase 1: Foundation**
- Website optimization and mobile responsiveness
- Basic SEO implementation
- Social media setup and content calendar

**Phase 2: Growth**
- Advanced analytics and tracking
- Email marketing automation
- Customer relationship management system

**Phase 3: Scale**
- AI-powered customer insights
- Advanced personalization
- Integrated marketing automation

### 6. SUCCESS METRICS
**Key Performance Indicators:**
• Website traffic increase: Target 50% within 6 months
• Lead generation: 25% increase in qualified leads
• Search engine rankings: Top 3 for primary keywords
• Customer engagement: 40% improvement in interaction rates

### 7. NEXT STEPS
1. **Week 1:** Complete website audit and competitor analysis
2. **Week 2:** Develop content strategy and editorial calendar
3. **Week 3:** Implement basic SEO and analytics tracking
4. **Week 4:** Launch social media presence and content marketing

**Priority Level:** High
**Estimated Timeline:** 3-6 months for full implementation
**Required Resources:** Digital marketing specialist, content creator, web developer

---
*This analysis was generated using rule-based intelligence. For AI-powered insights, please ensure your Gemini API key is properly configured.*
"""
    
    return analysis

@app.post("/solutions/generate")
async def generate_solutions(request: AnalysisRequest):
    """Generate solutions for a client"""
    if not model:
        raise HTTPException(status_code=500, detail="Gemini AI not configured")
    
    try:
        context = f"""
        CLIENT INFORMATION:
        Name: {request.client_data.name}
        Company: {request.client_data.company}
        Website: {request.client_data.website}
        Industry: {request.client_data.industry}
        Description: {request.client_data.description}
        
        REQUIREMENTS:
        {request.requirements}
        
        GOALS:
        {', '.join(request.goals)}
        """
        
        prompt = f"""
        Based on the following client information and requirements, generate specific, actionable solutions:
        
        {context}
        
        Generate 5-7 specific solutions that address the client's needs. Each solution should include:
        1. Solution Title
        2. Description
        3. Implementation Steps
        4. Expected Outcomes
        5. Priority Level (High/Medium/Low)
        6. Estimated Timeline
        7. Required Resources
        
        Format as a structured list of solutions.
        """
        
        response = model.generate_content(prompt)
        
        return {
            "message": "Solutions generated successfully",
            "solutions": response.text,
            "client_id": request.client_data.name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Solution generation failed: {str(e)}")

@app.get("/scraping/data")
async def get_scraped_data():
    """Get all scraped data"""
    return {"scraped_data": scraped_data_db}

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "running",
        "gemini_configured": bool(gemini_api_key),
        "clients_count": len(clients_db),
        "scraped_data_count": len(scraped_data_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
