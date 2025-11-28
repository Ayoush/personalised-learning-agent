# 🎓 AI-Powered Personalized Learning Path Generator

An intelligent multi-agent system built with Google ADK that creates personalized learning paths by analyzing student profiles, learning styles, and goals.

## 🌟 Features

- **Multi-Agent Architecture**: Coordinator, Sequential, Parallel, and Loop agent patterns
- **Personalized Learning**: Adapts to Visual, Auditory, Reading/Writing, and Kinesthetic learning styles
- **Knowledge Gap Analysis**: Identifies and addresses specific learning gaps
- **Resource Curation**: Finds the best learning resources matched to your style
- **Quality Assurance**: Loop-based content refinement for high-quality output
- **Teacher Approval Workflow**: Long-running operations with human-in-the-loop
- **Memory Persistence**: Remembers student preferences across sessions
- **Full Observability**: Logging, metrics, and tracing

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    COORDINATOR AGENT                            │
│                  (LLM-Powered Orchestrator)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Sequential  │    │   Parallel    │    │     Loop      │
│   Pipeline    │    │   Research    │    │   Refiner     │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ • Profile     │    │ • Web Search  │    │ • Generator   │
│ • Curriculum  │    │ • Video       │    │ • Reviewer    │
│ • Resources   │    │ • Practice    │    │ • Refiner     │
│ • Assessment  │    │               │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 📁 Project Structure

```
personalized_learning/
├── agents/
│   ├── __init__.py
│   ├── coordinator_agent.py    # Main LLM-powered orchestrator
│   ├── profile_analyzer.py     # Sequential Agent 1
│   ├── curriculum_designer.py  # Sequential Agent 2
│   ├── resource_finder.py      # Sequential Agent 3
│   ├── assessment_generator.py # Sequential Agent 4
│   ├── parallel_researchers.py # Parallel agents for resource discovery
│   └── content_refiner.py      # Loop agent for quality refinement
├── tools/
│   ├── __init__.py
│   └── custom_tools.py         # Learning style analysis, knowledge gap, etc.
├── memory/
│   ├── __init__.py
│   └── student_memory.py       # Memory Bank integration
├── observability/
│   ├── __init__.py
│   ├── logging_config.py       # Logging setup
│   └── metrics_collector.py    # Metrics collection
├── __init__.py
├── agent.py                    # ADK entry point (root_agent)
├── app.py                      # Application with Runner setup
├── requirements.txt
├── .env
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Cloud account with Vertex AI enabled
- ADK installed (`pip install google-adk`)

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd personalized_learning
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   # Edit .env with your Google Cloud project
   GOOGLE_GENAI_USE_VERTEXAI=1
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

4. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth application-default login
   gcloud config set project your-project-id
   ```

### Running the Agent

**Option 1: ADK CLI**
```bash
cd /path/to/capstone
adk run personalized_learning
```

**Option 2: ADK Web Interface**
```bash
cd /path/to/capstone
adk web personalized_learning
```

**Option 3: Interactive Python Session**
```bash
python -m personalized_learning.app
```

## 💡 Usage Examples

### Basic Learning Path Request

```
👤 You: I want to learn Python programming. I'm a complete beginner and 
        prefer watching videos. I have about 10 hours per week to study.

🤖 Assistant: 📚 Your Personalized Learning Path: Python Programming

👤 Your Profile
- Learning Style: Visual (Video-based learning)
- Current Level: Beginner
- Target: Intermediate Python Developer
- Available Time: 10 hours/week

📋 Curriculum Overview
Module 1: Python Basics (Week 1-2)
Module 2: Control Flow (Week 3)
Module 3: Functions & Modules (Week 4)
...

📖 Recommended Resources
🎥 Videos:
1. Python for Beginners - Corey Schafer (YouTube)
2. 100 Days of Code - Udemy
...
```

### Teacher Approval Flow

For complex learning paths, the system will pause for teacher approval:

```
⏸️ EXECUTION PAUSED - APPROVAL REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Complex learning path generated for advanced machine learning.
Please review the curriculum before delivery to student.

Do you approve? (Y/N): 
```

## 🔧 Implemented Concepts

| Concept | Implementation | File |
|---------|---------------|------|
| **Multi-Agent System** | Coordinator + Sub-agents | `coordinator_agent.py` |
| **Sequential Agents** | Profile → Curriculum → Resources → Assessment | `agents/*.py` |
| **Parallel Agents** | Web + Video + Practice research | `parallel_researchers.py` |
| **Loop Agents** | Generate → Review → Refine cycle | `content_refiner.py` |
| **Custom Tools** | Learning style, Knowledge gap | `tools/custom_tools.py` |
| **Built-in Tools** | `google_search` | `resource_finder.py` |
| **Long-Running Ops** | Teacher approval workflow | `custom_tools.py` |
| **Sessions** | InMemorySessionService | `app.py` |
| **Memory Bank** | StudentMemoryManager | `memory/student_memory.py` |
| **Observability** | Logging + Metrics | `observability/` |

## 📊 Observability

### Logging

```python
from personalized_learning.observability import setup_logging, get_logger

# Setup logging
setup_logging(level="DEBUG", log_file="app.log")

# Get logger
logger = get_logger("my_module")
logger.info("Processing student request...")
```

### Metrics

```python
from personalized_learning.observability import get_metrics

metrics = get_metrics()

# Record custom metrics
metrics.record_learning_path_generated("Python", "intermediate", 5.2)
metrics.record_agent_invocation("profile_analyzer", success=True)

# Get summary
print(metrics.get_summary())
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=personalized_learning tests/
```

## 📦 Deployment

### Local Development
```bash
adk web personalized_learning
```

### Cloud Run
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/personalized-learning

# Deploy
gcloud run deploy personalized-learning \
  --image gcr.io/PROJECT_ID/personalized-learning \
  --platform managed \
  --region us-central1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is part of the Google x Kaggle 5-Day AI Agents Intensive Course capstone.

## 🙏 Acknowledgments

- Google ADK Team
- Kaggle x Google AI Agents Course
- The open-source community

---

**Built with ❤️ using Google ADK for the Agents for Good Capstone Project**

