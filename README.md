# 🤖 Smart Interview Agent

AI-powered interview assistant that conducts technical interviews, evaluates candidates in real time, and generates professional reports.  
Built for the **AI Agent Development Challenge**.

---

## ✨ Features

- ✅ **Dynamic Question Generation** – Context-aware questions based on job description  
- ✅ **Real-Time Evaluation** – Instant scoring & feedback  
- ✅ **Multiple Interview Modes** – Technical, Behavioral, or Mixed  
- ✅ **Adaptive Questioning** – Adjusts based on candidate’s responses  
- ✅ **Professional Reports** – Comprehensive, exportable evaluations  
- ✅ **Interactive UI** – Clean Streamlit-powered experience  

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd YourName_AI_Agent_Challenge
```
```bash
##  2. Setup Environment
# Create virtual environment

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

# Install dependencies
```bash
pip install -r requirements.txt
```

## 3. Configure API Key
# Copy environment template
```bash
cp .env.example .env  # On Windows: copy .env.example .env
```

# Edit .env file with your OpenAI API key
```bash
OPENAI_API_KEY=your_api_key_here
```
## 4. Run the Application
```bash
streamlit run app.py
```

Open your browser at 👉 http://localhost:8501

## 🏗️ Project Structure
```bash
Smart Interview Agent
├── app.py                     # Main Streamlit application
├── agents/
│   ├── __init__.py
│   └── interview_agent.py     # Core AI interview logic
├── utils/
│   ├── __init__.py
│   ├── conversation_manager.py # Session & conversation management
│   └── report_generator.py    # AI-powered report generation
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🎯 Core Components
## 🧑‍💻 InterviewAgent

1. Generates contextual interview questions
2. Evaluates responses with scoring
3. Adapts questioning based on conversation flow

## 💬 ConversationManager

1. Tracks session history
2. Manages state & analytics
3. Supports data export

## 📑 ReportGenerator

1. Builds professional candidate reports
2. Detailed scoring breakdown
3. Provides hiring recommendations

## 📊 Evaluation Criteria

1. Technical
2. Knowledge depth
3. Problem solving
4. Code/system design skills
5. Communication clarity

## Soft Skills

1. Teamwork & collaboration
2. Leadership & adaptability
3. Cultural fit

## 🌐 Deployment

## Option 1: Streamlit Cloud (recommended)

1. Push code to GitHub
2. Connect repository on Streamlit Cloud
3. Add your OpenAI API key in Secrets
4. Deploy 🚀

# 📝 License

MIT License – see LICENSE

# 👨‍💻 Developer

Created for the AI Agent Development Challenge by KIRAN KUMAR S
