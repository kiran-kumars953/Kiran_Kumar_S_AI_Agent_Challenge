import openai
import json
import os
from datetime import datetime
from typing import Dict, List, Any

class ReportGenerator:
    def __init__(self):
        """Initialize the Report Generator"""
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate_report(self, conversation_data: Dict[str, Any], job_config: Dict[str, str]) -> Dict[str, Any]:
        """Generate a comprehensive interview report"""
        
        try:
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(conversation_data, job_config)
            
            # Generate report content
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer and HR analyst. Provide thorough, fair, and professional interview evaluations."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            report_content = response.choices[0].message.content.strip()
            
            # Parse the generated content
            parsed_report = self._parse_report_content(report_content)
            
            # Add metadata
            complete_report = self._add_metadata(parsed_report, conversation_data, job_config)
            
            return complete_report
            
        except Exception as e:
            return self._create_fallback_report(conversation_data, job_config, str(e))
    
    def _create_analysis_prompt(self, conversation_data: Dict[str, Any], job_config: Dict[str, str]) -> str:
        """Create the analysis prompt for report generation"""
        
        history = conversation_data.get("conversation_history", [])
        stats = conversation_data.get("statistics", {})
        
        # Build conversation summary
        conversation_summary = ""
        for i, exchange in enumerate(history, 1):
            score = exchange.get("score", 0)
            conversation_summary += f"""
Question {i}: {exchange.get('interviewer', '')[:200]}
Response: {exchange.get('candidate', '')[:300]}
Score: {score}/10

"""
        
        return f"""Analyze this technical interview and provide a comprehensive evaluation report.

INTERVIEW CONTEXT:
Position: {job_config.get('title', 'Software Engineer')}
Experience Level: {job_config.get('level', 'Not specified')}
Interview Type: {job_config.get('type', 'Technical')}
Candidate: {job_config.get('candidate_name', 'Candidate')}

JOB REQUIREMENTS:
{job_config.get('description', 'No job description provided')}

INTERVIEW STATISTICS:
- Total Questions: {stats.get('total_questions', 0)}
- Average Score: {stats.get('average_score', 0)}/10
- Highest Score: {stats.get('highest_score', 0)}/10
- Lowest Score: {stats.get('lowest_score', 0)}/10
- Score Trend: {stats.get('score_trend', 'stable')}

CONVERSATION DETAILS:
{conversation_summary}

Provide a structured analysis in JSON format with these exact fields:

{{
  "executive_summary": "2-3 sentence overall assessment",
  "overall_score": [number from 1-10],
  "strengths": ["List of 3-5 key strengths"],
  "areas_for_improvement": ["List of 3-4 improvement areas"],
  "technical_assessment": {{
    "technical_knowledge": [1-10 score],
    "problem_solving": [1-10 score],
    "technical_communication": [1-10 score]
  }},
  "soft_skills_assessment": {{
    "communication": [1-10 score],
    "adaptability": [1-10 score],
    "cultural_fit": [1-10 score]
  }},
  "recommendation": "Choose: 'Strong Hire', 'Hire', 'No Hire', or 'Further Interview Required'",
  "reasoning": "2-3 sentences explaining the recommendation"
}}

Return ONLY the JSON."""
    
    def _parse_report_content(self, content: str) -> Dict[str, Any]:
        """Parse the AI-generated report content"""
        try:
            # Try to extract JSON from the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_content = content[json_start:json_end]
                return json.loads(json_content)
            else:
                return self._create_basic_report()
                
        except json.JSONDecodeError:
            return self._create_basic_report()
    
    def _create_basic_report(self) -> Dict[str, Any]:
        """Create a basic report structure"""
        return {
            "executive_summary": "Interview completed successfully with standard evaluation.",
            "overall_score": 6,
            "strengths": ["Communication skills", "Technical engagement"],
            "areas_for_improvement": ["More specific examples needed", "Technical depth"],
            "technical_assessment": {
                "technical_knowledge": 6,
                "problem_solving": 6,
                "technical_communication": 6
            },
            "soft_skills_assessment": {
                "communication": 6,
                "adaptability": 6,
                "cultural_fit": 6
            },
            "recommendation": "Further Interview Required",
            "reasoning": "Additional assessment needed for final determination."
        }
    
    def _add_metadata(self, report: Dict[str, Any], conversation_data: Dict[str, Any], job_config: Dict[str, str]) -> Dict[str, Any]:
        """Add metadata to the report"""
        stats = conversation_data.get("statistics", {})
        
        report["interview_metadata"] = {
            "position": job_config.get("title", ""),
            "candidate_name": job_config.get("candidate_name", "Candidate"),
            "interview_date": datetime.now().strftime("%Y-%m-%d"),
            "questions_asked": stats.get("total_questions", 0),
            "average_score": stats.get("average_score", 0)
        }
        
        report["report_generated_at"] = datetime.now().isoformat()
        return report
    
    def _create_fallback_report(self, conversation_data: Dict[str, Any], job_config: Dict[str, str], error: str) -> Dict[str, Any]:
        """Create fallback report when AI generation fails"""
        stats = conversation_data.get("statistics", {})
        
        return {
            "executive_summary": f"Interview completed with {stats.get('total_questions', 0)} questions.",
            "overall_score": stats.get("average_score", 6),
            "strengths": ["Completed interview process", "Engaged with questions"],
            "areas_for_improvement": ["Detailed assessment needed"],
            "recommendation": "Further Interview Required",
            "reasoning": "Standard evaluation completed.",
            "interview_metadata": {
                "position": job_config.get("title", ""),
                "candidate_name": job_config.get("candidate_name", "Candidate"),
                "questions_asked": stats.get("total_questions", 0),
                "average_score": stats.get("average_score", 0)
            },
            "error_note": f"Fallback report due to: {error}"
        }
    
    def export_to_text(self, report_data: Dict[str, Any]) -> str:
        """Export report as formatted text"""
        metadata = report_data.get("interview_metadata", {})
        
        return f"""
INTERVIEW EVALUATION REPORT
===========================

Candidate: {metadata.get('candidate_name', 'N/A')}
Position: {metadata.get('position', 'N/A')}
Interview Date: {metadata.get('interview_date', 'N/A')}
Questions Asked: {metadata.get('questions_asked', 'N/A')}
Overall Score: {report_data.get('overall_score', 'N/A')}/10

EXECUTIVE SUMMARY
-----------------
{report_data.get('executive_summary', 'No summary available')}

RECOMMENDATION
--------------
{report_data.get('recommendation', 'No recommendation available')}

REASONING
---------
{report_data.get('reasoning', 'No reasoning provided')}
"""
    