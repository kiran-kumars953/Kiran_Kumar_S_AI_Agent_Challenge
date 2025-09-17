import openai
import json
import os
from typing import Dict
import streamlit as st

class InterviewAgent:
    def __init__(self, job_config: Dict):
        """Initialize the Interview Agent with job configuration"""
        self.job_config = job_config

        # Get OpenAI API key from environment or Streamlit secrets
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        if not api_key:
            raise openai.error.OpenAIError(
                "OpenAI API key not found! Set it in environment variables or Streamlit secrets."
            )

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=api_key)

        # Interview state
        self.question_count = 0
        self.current_question = ""
        self.interview_context = []

        # Interview settings based on duration
        self.max_questions = self._get_max_questions()

        # Generate first question
        self.current_question = self._generate_first_question()

    def _get_max_questions(self) -> int:
        """Determine max questions based on duration setting"""
        duration_map = {
            "Quick (5-8 questions)": 8,
            "Standard (8-12 questions)": 12,
            "Comprehensive (12-15 questions)": 15
        }
        return duration_map.get(self.job_config.get("duration", "Standard (8-12 questions)"), 10)

    def get_first_question(self) -> str:
        """Return the first question"""
        return self.current_question

    def _generate_first_question(self) -> str:
        """Generate opening question"""
        system_prompt = f"""
You are an experienced interviewer for a {self.job_config['title']} position.
Job Description:
{self.job_config['description']}
Candidate: {self.job_config.get('candidate_name', 'Candidate')}
Generate a professional opening question suitable for this position.
Return only the question text.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message['content'].strip()
        except Exception:
            # Fallback question
            return f"Hello! I'm excited to interview you for the {self.job_config['title']} position. Can you start by telling me about your relevant experience and what interests you about this role?"

    def process_response(self, candidate_response: str) -> Dict:
        """Process candidate response and generate next question"""
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

        is_final = self.question_count >= self.max_questions

        return {
            "question": next_question,
            "evaluation": evaluation,
            "is_final": is_final,
            "question_number": self.question_count + 1
        }

    def _evaluate_response(self, response_text: str) -> str:
        """Evaluate candidate response"""
        evaluation_prompt = f"""
Evaluate this response for a {self.job_config['title']} candidate.
Question: "{self.current_question}"
Response: "{response_text}"
Provide JSON: {{
  "score": [1-10],
  "feedback": "[brief constructive feedback]",
  "strengths": "[key strengths]",
  "areas_to_probe": "[areas needing more exploration]"
}}
Return ONLY JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": evaluation_prompt}],
                temperature=0.7,
                max_tokens=300
            )
            eval_text = response.choices[0].message['content'].strip()
            json.loads(eval_text)  # Ensure valid JSON
            return eval_text
        except Exception:
            # Fallback evaluation
            return json.dumps({
                "score": 6,
                "feedback": "Response received. Let's continue with the next question.",
                "strengths": "Engagement",
                "areas_to_probe": "More technical depth"
            })

    def _generate_next_question(self, candidate_response: str, evaluation: str) -> str:
        """Generate the next question based on previous response"""
        try:
            eval_data = json.loads(evaluation)
            areas_to_probe = eval_data.get("areas_to_probe", "")
            score = eval_data.get("score", 5)
        except Exception:
            areas_to_probe = ""
            score = 5

        # Build context from previous questions
        context_summary = ""
        if self.interview_context:
            recent_topics = [ctx["question"][:100] for ctx in self.interview_context[-3:]]
            context_summary = f"Previous topics: {'; '.join(recent_topics)}"

        question_prompt = f"""
You are conducting an interview for {self.job_config['title']}.
Current question: {self.current_question}
Candidate response: {candidate_response[:500]}
Evaluation score: {score}
Areas to probe: {areas_to_probe}
{context_summary}
Job Requirements:
{self.job_config['description'][:800]}
Generate the next interview question appropriate for {self.job_config['level']} level.
Return only the question text.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": question_prompt}],
                temperature=0.8,
                max_tokens=250
            )
            return response.choices[0].message['content'].strip()
        except Exception:
            fallback_questions = [
                "Can you describe a challenging technical problem you've solved?",
                "How do you stay updated in your field?",
                "Tell me about a time you worked with a difficult team member.",
                "What interests you about this role?",
                "Do you have any questions about the position?"
            ]
            index = min(self.question_count, len(fallback_questions) - 1)
            return fallback_questions[index]

    def get_interview_summary(self) -> Dict:
        """Return interview summary"""
        return {
            "total_questions": len(self.interview_context),
            "max_questions": self.max_questions,
            "progress_percentage": min((len(self.interview_context) / self.max_questions) * 100, 100),
            "job_config": self.job_config,
            "interview_context": self.interview_context
        }
