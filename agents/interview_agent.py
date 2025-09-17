import openai
import json
import os
from datetime import datetime
from typing import Dict, List

class InterviewAgent:
    def __init__(self, job_config):
        """Initialize the Interview Agent with job configuration"""
        self.job_config = job_config
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Interview state
        self.question_count = 0
        self.current_question = ""
        self.interview_context = []
        
        # Interview settings based on duration
        self.max_questions = self._get_max_questions()
        
        # Generate first question
        self.current_question = self._generate_first_question()
    
    def _get_max_questions(self):
        """Determine max questions based on duration setting"""
        duration_map = {
            "Quick (5-8 questions)": 8,
            "Standard (8-12 questions)": 12,
            "Comprehensive (12-15 questions)": 15
        }
        return duration_map.get(self.job_config.get("duration", "Standard (8-12 questions)"), 10)
    
    def get_first_question(self):
        """Get the first question for the interview"""
        return self.current_question
    
    def _generate_first_question(self):
        """Generate the opening question based on job configuration"""
        
        system_prompt = f"""You are an experienced technical interviewer conducting an interview for a {self.job_config['title']} position.

Interview Details:
- Position: {self.job_config['title']}
- Experience Level: {self.job_config['level']}
- Interview Type: {self.job_config['type']}
- Candidate: {self.job_config.get('candidate_name', 'Candidate')}

Job Description:
{self.job_config['description']}

Generate an engaging opening question that:
1. Is appropriate for the {self.job_config['level']} experience level
2. Relates to the job requirements and responsibilities
3. Sets a professional, welcoming tone
4. Either asks about their background OR starts with a relevant technical/behavioral question
5. Follows interview best practices

Examples of good opening questions:
- For technical: "Can you walk me through your experience with [relevant technology from job description]?"
- For behavioral: "Tell me about a challenging project you've worked on that relates to this role."
- For background: "I'd love to hear about your background and what interests you about this position."

Return ONLY the question text, no additional formatting or explanations."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices.message.content.strip()
            
        except Exception as e:
            return f"Hello! I'm excited to interview you for the {self.job_config['title']} position. Can you start by telling me about your relevant experience and what interests you about this role?"
    
    def process_response(self, candidate_response: str) -> Dict:
        """Process candidate response and generate next question"""
        
        # Evaluate the current response
        evaluation = self._evaluate_response(candidate_response)
        
        # Update interview context
        self.interview_context.append({
            "question": self.current_question,
            "response": candidate_response,
            "evaluation": evaluation
        })
        
        # Generate next question
        next_question = self._generate_next_question(candidate_response, evaluation)
        self.current_question = next_question
        self.question_count += 1
        
        # Check if interview should end
        is_final = self.question_count >= self.max_questions
        
        return {
            "question": next_question,
            "evaluation": evaluation,
            "is_final": is_final,
            "question_number": self.question_count + 1
        }
    
    def _evaluate_response(self, response: str) -> str:
        """Evaluate candidate response with scoring and feedback"""
        
        evaluation_prompt = f"""As an expert interviewer for a {self.job_config['title']} position, evaluate this candidate response.

Previous Question: "{self.current_question}"
Candidate Response: "{response}"

Job Context:
- Position: {self.job_config['title']}
- Level: {self.job_config['level']}
- Type: {self.job_config['type']}

Evaluation Criteria:
1. Technical accuracy (if applicable)
2. Communication clarity and structure
3. Completeness and depth of answer
4. Relevant experience demonstration
5. Problem-solving approach (if applicable)

Provide evaluation in this EXACT JSON format:
{{
  "score": [number from 1-10],
  "feedback": "[brief constructive feedback in 1-2 sentences]",
  "strengths": "[key strengths observed]",
  "areas_to_probe": "[areas that need more exploration]"
}}

Score Guidelines:
- 8-10: Excellent response with strong technical knowledge and clear communication
- 6-7: Good response with some strong points but room for improvement
- 4-5: Average response with basic understanding but lacking depth
- 1-3: Weak response with significant gaps or unclear communication

Return ONLY the JSON, no additional text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": evaluation_prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            eval_text = response.choices.message.content.strip()
            
            # Ensure valid JSON
            try:
                json.loads(eval_text)
                return eval_text
            except json.JSONDecodeError:
                # Fallback evaluation
                return json.dumps({
                    "score": 6,
                    "feedback": "Thank you for your response. I'd like to explore this topic further.",
                    "strengths": "Good communication",
                    "areas_to_probe": "Technical depth"
                })
                
        except Exception as e:
            # Fallback evaluation
            return json.dumps({
                "score": 5,
                "feedback": "I appreciate your response. Let's continue with the next question.",
                "strengths": "Engagement with the question",
                "areas_to_probe": "More detailed examples"
            })
    
    def _generate_next_question(self, candidate_response: str, evaluation: str) -> str:
        """Generate the next interview question"""
        
        # Parse evaluation for context
        try:
            eval_data = json.loads(evaluation)
            areas_to_probe = eval_data.get("areas_to_probe", "")
            score = eval_data.get("score", 5)
        except:
            areas_to_probe = ""
            score = 5
        
        # Build context from previous questions
        context_summary = ""
        if self.interview_context:
            recent_topics = [ctx["question"][:100] for ctx in self.interview_context[-3:]]
            context_summary = f"Previous topics covered: {'; '.join(recent_topics)}"
        
        question_prompt = f"""You are conducting an interview for a {self.job_config['title']} position.

Current Status:
- Question Number: {self.question_count + 1} of {self.max_questions}
- Interview Type: {self.job_config['type']}
- Experience Level: {self.job_config['level']}

Previous Question: "{self.current_question}"
Candidate Response: "{candidate_response[:500]}..."
Evaluation Score: {score}/10
Areas to Probe: {areas_to_probe}

{context_summary}

Job Requirements:
{self.job_config['description'][:800]}

Generate the next question that:
1. Builds naturally on the conversation flow
2. Explores different aspects of the candidate's qualifications
3. Is appropriate for {self.job_config['level']} level
4. Matches the {self.job_config['type']} interview style
5. Avoids repeating previous topics
6. {"Is a strong closing question since this is near the end" if self.question_count >= self.max_questions - 2 else "Maintains good interview momentum"}

Question Types to Consider:
- Technical: Code problems, system design, debugging scenarios
- Behavioral: STAR method situations, teamwork, problem-solving
- Experience: Deep dives into past projects and achievements
- Situational: How they would handle specific job-related scenarios

Return ONLY the question text, no additional formatting."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": question_prompt}],
                temperature=0.8,
                max_tokens=250
            )
            
            return response.choices.message.content.strip()
            
        except Exception as e:
            # Fallback questions based on interview progress
            fallback_questions = [
                "Can you describe a challenging technical problem you've solved and walk me through your approach?",
                "How do you stay updated with the latest developments in your field?",
                "Tell me about a time when you had to work with a difficult team member. How did you handle it?",
                "What interests you most about this role and our company?",
                "Do you have any questions about the position or our team?"
            ]
            
            question_index = min(self.question_count, len(fallback_questions) - 1)
            return fallback_questions[question_index]
    
    def get_interview_summary(self) -> Dict:
        """Get a summary of the interview progress"""
        return {
            "total_questions": len(self.interview_context),
            "max_questions": self.max_questions,
            "progress_percentage": min((len(self.interview_context) / self.max_questions) * 100, 100),
            "job_config": self.job_config,
            "interview_context": self.interview_context
        }
