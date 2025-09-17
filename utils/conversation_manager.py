from typing import List, Dict, Any
import json
from datetime import datetime, timedelta

class ConversationManager:
    def __init__(self):
        """Initialize the conversation manager"""
        self.conversation_history = []
        self.start_time = datetime.now()
        self.evaluation_scores = []
        self.candidate_responses = []
        self.interviewer_questions = []
    
    def add_exchange(self, candidate_input: str, interviewer_response: Dict[str, Any]):
        """Add a conversation exchange between candidate and interviewer"""
        
        # Create exchange record
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "candidate": candidate_input,
            "interviewer": interviewer_response.get("question", ""),
            "evaluation": interviewer_response.get("evaluation", "{}"),
            "question_number": len(self.conversation_history) + 1,
            "score": self._extract_score(interviewer_response.get("evaluation", "{}"))
        }
        
        # Add to history
        self.conversation_history.append(exchange)
        
        # Update tracking lists
        self.candidate_responses.append(candidate_input)
        self.interviewer_questions.append(interviewer_response.get("question", ""))
        
        # Extract and store score
        score = self._extract_score(interviewer_response.get("evaluation", "{}"))
        if score is not None:
            self.evaluation_scores.append(score)
    
    def _extract_score(self, evaluation_json: str) -> float:
        """Extract numeric score from evaluation JSON"""
        try:
            eval_data = json.loads(evaluation_json)
            score = eval_data.get("score", 0)
            return float(score) if score is not None else 0.0
        except (json.JSONDecodeError, ValueError, TypeError):
            return 0.0
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the complete conversation history"""
        return self.conversation_history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        duration = datetime.now() - self.start_time
        
        return {
            "total_exchanges": len(self.conversation_history),
            "duration": self._format_duration(duration),
            "duration_minutes": int(duration.total_seconds() / 60),
            "average_score": self.get_average_score(),
            "highest_score": max(self.evaluation_scores) if self.evaluation_scores else 0,
            "lowest_score": min(self.evaluation_scores) if self.evaluation_scores else 0,
            "score_trend": self._calculate_score_trend()
        }
    
    def get_average_score(self) -> float:
        """Calculate average evaluation score"""
        if not self.evaluation_scores:
            return 0.0
        return round(sum(self.evaluation_scores) / len(self.evaluation_scores), 1)
    
    def _calculate_score_trend(self) -> str:
        """Calculate if scores are trending up, down, or stable"""
        if len(self.evaluation_scores) < 2:
            return "stable"
        
        first_half = self.evaluation_scores[:len(self.evaluation_scores)//2]
        second_half = self.evaluation_scores[len(self.evaluation_scores)//2:]
        
        if not first_half or not second_half:
            return "stable"
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg + 0.5:
            return "improving"
        elif second_avg < first_avg - 0.5:
            return "declining"
        else:
            return "stable"
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration in a readable format"""
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} sec"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} min"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def export_conversation(self) -> Dict[str, Any]:
        """Export conversation data for report generation"""
        stats = self.get_stats()
        
        return {
            "conversation_history": self.conversation_history,
            "statistics": {
                "total_questions": len(self.conversation_history),
                "average_score": stats["average_score"],
                "highest_score": stats["highest_score"],
                "lowest_score": stats["lowest_score"],
                "score_trend": stats["score_trend"],
                "total_candidate_words": sum(len(response.split()) for response in self.candidate_responses),
                "average_response_length": sum(len(response.split()) for response in self.candidate_responses) // len(self.candidate_responses) if self.candidate_responses else 0
            },
            "scores_timeline": self.evaluation_scores
        }
    