import streamlit as st
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Import our custom modules
from agents.interview_agent import InterviewAgent
from utils.conversation_manager import ConversationManager
from utils.report_generator import ReportGenerator

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Smart Interview Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 1rem;
}
.sub-header {
    font-size: 1.2rem;
    color: #666;
    text-align: center;
    margin-bottom: 2rem;
}
.sidebar-header {
    font-size: 1.3rem;
    color: #1f77b4;
    margin-bottom: 1rem;
}
.interview-stats {
    background-color: #e8f4fd;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "conversation_manager" not in st.session_state:
        st.session_state.conversation_manager = None
    if "interview_agent" not in st.session_state:
        st.session_state.interview_agent = None
    if "job_config" not in st.session_state:
        st.session_state.job_config = {}
    if "interview_ended" not in st.session_state:
        st.session_state.interview_ended = False

def main():
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Smart Interview Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Technical Interview Conductor & Evaluator</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">Interview Configuration</h2>', unsafe_allow_html=True)
        
        # Job Configuration
        job_title = st.text_input(
            "Job Title *", 
            value="Software Engineer",
            placeholder="e.g., Software Engineer, Data Scientist"
        )
        
        experience_level = st.selectbox(
            "Experience Level *", 
            ["Entry Level (0-2 years)", "Mid Level (2-5 years)", "Senior Level (5+ years)"],
            index=1
        )
        
        interview_type = st.selectbox(
            "Interview Type *", 
            ["Technical Focus", "Behavioral Focus", "Mixed (Technical + Behavioral)"],
            index=0
        )
        
        interview_duration = st.selectbox(
            "Interview Duration",
            ["Quick (5-8 questions)", "Standard (8-12 questions)", "Comprehensive (12-15 questions)"],
            index=1
        )
        
        st.markdown("### Job Description")
        job_description = st.text_area(
            "Job Description *", 
            height=150,
            placeholder="Paste the complete job description here. Include required skills, responsibilities, and qualifications...",
            value="We are looking for a skilled Software Engineer to join our team. Responsibilities include developing web applications using Python, working with databases, and collaborating with cross-functional teams. Required skills: Python, SQL, JavaScript, problem-solving abilities."
        )
        
        candidate_name = st.text_input(
            "Candidate Name (Optional)",
            placeholder="e.g., John Doe"
        )
        
        # Validation and Start Button
        if st.button("🚀 Start Interview", type="primary"):
            if job_title and job_description:
                st.session_state.interview_started = True
                st.session_state.interview_ended = False
                st.session_state.job_config = {
                    "title": job_title,
                    "level": experience_level,
                    "type": interview_type,
                    "duration": interview_duration,
                    "description": job_description,
                    "candidate_name": candidate_name or "Candidate"
                }
                st.session_state.conversation_manager = ConversationManager()
                st.session_state.interview_agent = InterviewAgent(st.session_state.job_config)
                st.success("✅ Interview initialized! Start the conversation below.")
                st.rerun()
            else:
                st.error("❌ Please fill in Job Title and Job Description before starting.")
        
        # Reset Button
        if st.button("🔄 Reset Interview"):
            reset_interview()
            st.rerun()
    
    # Main interview interface
    if not st.session_state.interview_started:
        show_welcome_page()
    elif st.session_state.interview_ended:
        show_interview_report()
    else:
        run_interview()

def show_welcome_page():
    """Display welcome page with instructions"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## Welcome to Smart Interview Agent! 👋
        
        ### How it works:
        1. **Configure** the interview settings in the sidebar
        2. **Start** the interview with your job requirements
        3. **Interact** naturally with the AI interviewer
        4. **Receive** detailed evaluation and reports
        
        ### Features:
        - ✅ Dynamic question generation based on job description
        - ✅ Real-time candidate evaluation and scoring
        - ✅ Multiple interview formats (Technical/Behavioral/Mixed)
        - ✅ Professional interview reports with recommendations
        - ✅ Adaptive questioning based on responses
        
        ### Get Started:
        👈 **Configure your interview settings in the sidebar and click "Start Interview"**
        """)

def run_interview():
    """Main interview interface"""
    
    # Interview Status Bar
    col1, col2, col3, col4 = st.columns(4)
    
    history = st.session_state.conversation_manager.get_history()
    stats = st.session_state.conversation_manager.get_stats()
    
    with col1:
        st.metric("Questions Asked", len(history))
    with col2:
        st.metric("Duration", stats.get("duration", "0 min"))
    with col3:
        st.metric("Average Score", f"{stats.get('average_score', 0):.1f}/10")
    with col4:
        progress = min(len(history) / 10, 1.0)  # Assume 10 questions max
        st.metric("Progress", f"{int(progress * 100)}%")
    
    # Chat Interface
    st.markdown("### 💬 Interview Conversation")
    
    # Display conversation history
    chat_container = st.container()
    
    with chat_container:
        if not history:
            # Show initial question
            first_question = st.session_state.interview_agent.get_first_question()
            with st.chat_message("assistant", avatar="🤖"):
                st.write(f"**AI Interviewer:** {first_question}")
        else:
            # Display all exchanges
            for exchange in history:
                with st.chat_message("human", avatar="👤"):
                    st.write(f"**{st.session_state.job_config['candidate_name']}:** {exchange['candidate']}")
                
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(f"**AI Interviewer:** {exchange['interviewer']}")
                    
                    # Show evaluation if available
                    if exchange.get('evaluation'):
                        try:
                            eval_data = json.loads(exchange['evaluation'])
                            score = eval_data.get('score', 'N/A')
                            feedback = eval_data.get('feedback', 'No feedback available')
                            
                            st.markdown(f"""
                            <div style="background-color: #f0f8ff; padding: 8px; border-radius: 5px; margin: 5px 0; font-size: 0.9em;">
                            <strong>Evaluation:</strong> Score: {score}/10<br>
                            <strong>Feedback:</strong> {feedback}
                            </div>
                            """, unsafe_allow_html=True)
                        except:
                            pass
    
    # Input area
    st.markdown("### 🎤 Your Response")
    
    # Check if interview should end
    max_questions = get_max_questions(st.session_state.job_config["duration"])
    if len(history) >= max_questions:
        st.info(f"📝 Interview completed! You've answered {len(history)} questions.")
        if st.button("📊 View Interview Report", type="primary"):
            st.session_state.interview_ended = True
            st.rerun()
        return
    
    # Response input
    user_input = st.text_area(
        "Type your response here:",
        height=100,
        placeholder="Share your thoughts, experience, or technical knowledge...",
        key="user_response"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📤 Submit Response", type="primary") and user_input.strip():
            process_candidate_response(user_input.strip())
            st.rerun()
    
    with col2:
        if st.button("⏭️ Skip Question"):
            process_candidate_response("I'd prefer to skip this question.")
            st.rerun()
    
    with col3:
        if st.button("🏁 End Interview"):
            st.session_state.interview_ended = True
            st.rerun()

def process_candidate_response(user_input):
    """Process candidate response and get next question"""
    try:
        with st.spinner("🤔 AI is evaluating your response..."):
            # Get response from interview agent
            agent_response = st.session_state.interview_agent.process_response(user_input)
            
            # Add to conversation history
            st.session_state.conversation_manager.add_exchange(user_input, agent_response)
            
    except Exception as e:
        st.error(f"Error processing response: {str(e)}")
        st.error("Please check your OpenAI API key and try again.")

def show_interview_report():
    """Display comprehensive interview report"""
    st.markdown("# 📊 Interview Report")
    
    # Generate report
    try:
        with st.spinner("📝 Generating comprehensive interview report..."):
            conversation_data = st.session_state.conversation_manager.export_conversation()
            report_generator = ReportGenerator()
            report = report_generator.generate_report(conversation_data, st.session_state.job_config)
        
        # Display report sections
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("## Executive Summary")
            st.write(report.get("executive_summary", "No summary available"))
            
            st.markdown("## Strengths Identified")
            strengths = report.get("strengths", ["Analysis pending"])
            for strength in strengths if isinstance(strengths, list) else [strengths]:
                st.write(f"✅ {strength}")
            
            st.markdown("## Areas for Improvement")
            improvements = report.get("areas_for_improvement", ["Analysis pending"])
            for improvement in improvements if isinstance(improvements, list) else [improvements]:
                st.write(f"📈 {improvement}")
            
            st.markdown("## Recommendation")
            recommendation = report.get("recommendation", "Further review recommended")
            if "hire" in recommendation.lower() and "no" not in recommendation.lower():
                st.success(f"✅ **Recommendation:** {recommendation}")
            elif "no hire" in recommendation.lower():
                st.error(f"❌ **Recommendation:** {recommendation}")
            else:
                st.warning(f"⚠️ **Recommendation:** {recommendation}")
        
        with col2:
            st.markdown("## Interview Statistics")
            metadata = report.get("interview_metadata", {})
            
            st.metric("Total Questions", metadata.get("questions_asked", 0))
            st.metric("Overall Score", f"{metadata.get('average_score', 0):.1f}/10")
        
        # Export options
        st.markdown("## 📄 Export Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Copy Report Text"):
                report_text = report_generator.export_to_text(report)
                st.code(report_text, language=None)
        
        with col2:
            if st.button("📊 Download JSON"):
                st.download_button(
                    label="Download Report JSON",
                    data=json.dumps(report, indent=2),
                    file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("🔄 New Interview"):
                reset_interview()
                st.rerun()
                
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        st.error("Please check your OpenAI API key and try again.")

def get_max_questions(duration_setting):
    """Get maximum questions based on duration setting"""
    duration_map = {
        "Quick (5-8 questions)": 8,
        "Standard (8-12 questions)": 12,
        "Comprehensive (12-15 questions)": 15
    }
    return duration_map.get(duration_setting, 10)

def reset_interview():
    """Reset all interview session state"""
    keys_to_reset = [
        "interview_started", "conversation_manager", "interview_agent", 
        "job_config", "interview_ended"
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

if __name__ == "__main__":
    main()
