"""
Gemini AI service for intelligent analysis and solution generation
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """Gemini AI service for analysis and solution generation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_client_data(self, client_data: Dict[str, Any], scraped_data: List[Dict[str, Any]], 
                          rag_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze client data and generate insights
        
        Args:
            client_data: Basic client information
            scraped_data: Scraped website data
            rag_context: RAG context from knowledge base
        
        Returns:
            Analysis results
        """
        try:
            # Prepare context for analysis
            context = self._prepare_analysis_context(client_data, scraped_data, rag_context)
            
            prompt = f"""
            As a business analyst and consultant, analyze the following client data and provide comprehensive insights:
            
            CLIENT INFORMATION:
            {json.dumps(client_data, indent=2)}
            
            WEBSITE DATA:
            {json.dumps(scraped_data, indent=2)}
            
            KNOWLEDGE BASE CONTEXT:
            {json.dumps(rag_context, indent=2)}
            
            Please provide a detailed analysis including:
            1. Business Overview and Industry Analysis
            2. Website Performance and User Experience Assessment
            3. Content Quality and SEO Analysis
            4. Competitive Positioning
            5. Strengths and Weaknesses
            6. Opportunities and Threats
            7. Key Recommendations
            
            Format your response as a structured JSON object with clear sections and actionable insights.
            """
            
            response = self.model.generate_content(prompt)
            analysis = self._parse_analysis_response(response.text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing client data: {str(e)}")
            return {"error": str(e)}
    
    def generate_solutions(self, analysis: Dict[str, Any], requirements: str, 
                          client_goals: List[str]) -> List[Dict[str, Any]]:
        """
        Generate solutions based on analysis and requirements
        
        Args:
            analysis: Client analysis results
            requirements: Client requirements
            client_goals: List of client goals
        
        Returns:
            List of generated solutions
        """
        try:
            prompt = f"""
            Based on the following client analysis and requirements, generate specific, actionable solutions:
            
            ANALYSIS:
            {json.dumps(analysis, indent=2)}
            
            REQUIREMENTS:
            {requirements}
            
            CLIENT GOALS:
            {json.dumps(client_goals, indent=2)}
            
            Generate 5-7 specific solutions that address the client's needs. Each solution should include:
            1. Solution Title
            2. Description
            3. Implementation Steps
            4. Expected Outcomes
            5. Priority Level (High/Medium/Low)
            6. Estimated Timeline
            7. Required Resources
            8. Success Metrics
            
            Format as a JSON array of solution objects.
            """
            
            response = self.model.generate_content(prompt)
            solutions = self._parse_solutions_response(response.text)
            
            return solutions
            
        except Exception as e:
            logger.error(f"Error generating solutions: {str(e)}")
            return []
    
    def generate_marketing_strategy(self, client_data: Dict[str, Any], 
                                  analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate marketing strategy recommendations
        
        Args:
            client_data: Client information
            analysis: Client analysis results
        
        Returns:
            Marketing strategy recommendations
        """
        try:
            prompt = f"""
            Create a comprehensive marketing strategy for this client:
            
            CLIENT DATA:
            {json.dumps(client_data, indent=2)}
            
            ANALYSIS:
            {json.dumps(analysis, indent=2)}
            
            Generate a detailed marketing strategy including:
            1. Target Audience Analysis
            2. Brand Positioning
            3. Content Strategy
            4. Digital Marketing Channels
            5. SEO Strategy
            6. Social Media Strategy
            7. Email Marketing Strategy
            8. Paid Advertising Recommendations
            9. Budget Allocation
            10. Success Metrics and KPIs
            
            Format as a structured JSON object with actionable recommendations.
            """
            
            response = self.model.generate_content(prompt)
            strategy = self._parse_strategy_response(response.text)
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error generating marketing strategy: {str(e)}")
            return {"error": str(e)}
    
    def generate_technical_recommendations(self, scraped_data: List[Dict[str, Any]], 
                                         analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate technical recommendations for website improvement
        
        Args:
            scraped_data: Scraped website data
            analysis: Client analysis results
        
        Returns:
            Technical recommendations
        """
        try:
            prompt = f"""
            Analyze the technical aspects of this website and provide improvement recommendations:
            
            WEBSITE DATA:
            {json.dumps(scraped_data, indent=2)}
            
            ANALYSIS:
            {json.dumps(analysis, indent=2)}
            
            Provide technical recommendations covering:
            1. Performance Optimization
            2. SEO Technical Issues
            3. Security Improvements
            4. Mobile Responsiveness
            5. Accessibility
            6. Code Quality
            7. Infrastructure Recommendations
            8. Monitoring and Analytics Setup
            
            Format as a structured JSON object with specific, actionable technical recommendations.
            """
            
            response = self.model.generate_content(prompt)
            recommendations = self._parse_technical_response(response.text)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating technical recommendations: {str(e)}")
            return {"error": str(e)}
    
    def generate_content_suggestions(self, client_data: Dict[str, Any], 
                                   analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate content suggestions for the client
        
        Args:
            client_data: Client information
            analysis: Client analysis results
        
        Returns:
            List of content suggestions
        """
        try:
            prompt = f"""
            Generate content suggestions for this client based on their business and analysis:
            
            CLIENT DATA:
            {json.dumps(client_data, indent=2)}
            
            ANALYSIS:
            {json.dumps(analysis, indent=2)}
            
            Generate 10-15 specific content suggestions including:
            1. Blog Post Topics
            2. Social Media Content Ideas
            3. Video Content Suggestions
            4. Infographic Ideas
            5. Case Study Topics
            6. White Paper Ideas
            7. Email Newsletter Content
            8. Landing Page Content
            9. FAQ Content
            10. Resource Page Ideas
            
            Each suggestion should include:
            - Title
            - Description
            - Target Audience
            - Content Type
            - Priority Level
            - Expected Impact
            
            Format as a JSON array of content suggestion objects.
            """
            
            response = self.model.generate_content(prompt)
            suggestions = self._parse_content_response(response.text)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating content suggestions: {str(e)}")
            return []
    
    def _prepare_analysis_context(self, client_data: Dict[str, Any], 
                                scraped_data: List[Dict[str, Any]], 
                                rag_context: List[Dict[str, Any]]) -> str:
        """Prepare context for analysis"""
        context = {
            "client": client_data,
            "website_summary": self._summarize_website_data(scraped_data),
            "knowledge_base_summary": self._summarize_rag_context(rag_context)
        }
        return json.dumps(context, indent=2)
    
    def _summarize_website_data(self, scraped_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize scraped website data"""
        if not scraped_data:
            return {}
        
        summary = {
            "total_pages": len(scraped_data),
            "titles": [page.get("title", "") for page in scraped_data if page.get("title")],
            "content_types": list(set([page.get("content_type", "unknown") for page in scraped_data])),
            "total_links": sum(len(page.get("links", [])) for page in scraped_data),
            "total_images": sum(len(page.get("images", [])) for page in scraped_data)
        }
        return summary
    
    def _summarize_rag_context(self, rag_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize RAG context"""
        if not rag_context:
            return {}
        
        summary = {
            "total_chunks": len(rag_context),
            "sources": list(set([chunk.get("metadata", {}).get("source_type", "unknown") for chunk in rag_context])),
            "key_topics": self._extract_key_topics(rag_context)
        }
        return summary
    
    def _extract_key_topics(self, rag_context: List[Dict[str, Any]]) -> List[str]:
        """Extract key topics from RAG context"""
        # Simple keyword extraction - could be enhanced with NLP
        topics = set()
        for chunk in rag_context:
            content = chunk.get("content", "").lower()
            # Add simple keyword extraction logic here
            if "seo" in content:
                topics.add("SEO")
            if "marketing" in content:
                topics.add("Marketing")
            if "design" in content:
                topics.add("Design")
            if "performance" in content:
                topics.add("Performance")
        return list(topics)
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse analysis response from Gemini"""
        try:
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                # Fallback to text parsing
                return {"raw_analysis": response_text}
        except:
            return {"raw_analysis": response_text}
    
    def _parse_solutions_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse solutions response from Gemini"""
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                return [{"raw_solution": response_text}]
        except:
            return [{"raw_solution": response_text}]
    
    def _parse_strategy_response(self, response_text: str) -> Dict[str, Any]:
        """Parse strategy response from Gemini"""
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                return {"raw_strategy": response_text}
        except:
            return {"raw_strategy": response_text}
    
    def _parse_technical_response(self, response_text: str) -> Dict[str, Any]:
        """Parse technical response from Gemini"""
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                return {"raw_recommendations": response_text}
        except:
            return {"raw_recommendations": response_text}
    
    def _parse_content_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse content response from Gemini"""
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                return [{"raw_suggestion": response_text}]
        except:
            return [{"raw_suggestion": response_text}]
