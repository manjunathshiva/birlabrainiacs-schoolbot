# Birlabrainiacs School Assistant  🏫

An intelligent chatbot created during the Llama Impact Hackathon, designed specifically for Birla Brainiacs School. 
This assistant helps students, parents, and staff access academic information through an intuitive chat interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-green)
![Streamlit](https://img.shields.io/badge/Streamlit-red)

## 🌟 Features

- **Smart Information Retrieval**
   - Crawls Birla Brainiacs School website for latest information
   - RAG (Retrieval Augmented Generation) system for accurate responses
   - Comprehensive coverage of:
      - Academic Calendar
      - Exam & Test Schedules
      - Course Portions

- **Intelligent Response System**
   - First searches the school website
   - Then queries the RAG system
   - Provides clear "Information not found" responses when needed

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- Poetry (for dependency management)
- Docker (for running the Restack services)
- Active [Together AI](https://together.ai) account with API key
- Active [SerpAPI](https://serpapi.com) account with API key
- Active [Qdrant](https://qdrant.tech) account with API key

### Installation Steps

1. **Start Restack Engine**

   ```bash
   docker run -d --pull always --name studio -p 5233:5233 -p 6233:6233 -p 7233:7233 ghcr.io/restackio/engine:main
   ```

2. **Access Web UI**

   ```
   http://localhost:5233
   ```

3. **Clone Repository**

   ```bash
   git clone https://github.com/manjunathshiva/birlabrainiacs-schoolbot
   cd birlabrainiacs-schoolbot
   ```

4. **Install Dependencies**

   ```bash
   poetry install
   ```

5. **Setup Environment**

   Copy `.env.example` to `.env` and configure required API keys:

   ```bash
   cp .env.example .env
   # Edit .env and add your TOGETHER_API_KEY, SERPAPI_KEY, QDRANT_HOST and QDRANT_API_KEY
   ```

## 💻 Development Setup

1. **Activate Poetry Environment**

   ```bash
   poetry shell
   ```

2. **IDE Configuration**
   - Use the Poetry interpreter path shown after shell activation
   - Configure in VSCode/Cursor:
      - Select Python Interpreter
      - Choose the poetry virtual environment path

## 🎯 Running the Application

1. **Start Backend Services**

   ```bash
   poetry run services
   ```
   This will start the Restack service with the defined workflows and functions.

2. **Launch FastAPI Server**

   ```bash
   poetry run app
   ```

3. **Start Streamlit Frontend**

   ```bash
   poetry run streamlit run frontend.py
   ```

## 🔍 API Testing

Test the endpoint directly:

```bash
curl -X POST \
  http://localhost:8000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the skill development certificate courses offered by School ?", "count": 1}'
```

## 📁 Project Structure

```
birlabrainiacs-schoolbot/
├── src/
│   ├── __init__.py
│   ├── app.py          # FastAPI application
│   ├── client.py       # Client implementations
│   ├── services.py     # Core services
│   ├── functions/
│   │   ├── bb/        # Birla Brainiacs specific functions
│   │   │   ├── schema.py
│   │   │   └── search.py
│   │   └── llm/       # LLM related functions
│   │       └── chat.py
│   └── workflows/      # Workflow definitions
│       └── workflow.py
├── data/
│   └── Academic Calender 2024-25.pdf.md  # Processed academic data
├── frontend.py         # Streamlit UI
├── ingestion.py        # Data ingestion scripts
├── pyproject.toml      # Poetry dependencies
├── .env.example        # Environment variables template
├── .gitignore
└── README.md
```

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and enhancement requests.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built during Llama Impact Hackathon
- Powered by Together AI
- Uses LlamaIndex for RAG implementation
- Frontend built with Streamlit
- Backend powered by FastAPI
- Workflow managed by Restack
- Document Processing:
  - LlamaParse: Advanced PDF parsing for:
    - Color-coded academic calendars
    - Complex table structures
    - Formatted text conversion to markdown
    - Preservation of semantic meaning in calendar layouts

Key LlamaParse contribution: Enhanced the RAG system's understanding of calendar data by maintaining the structural and visual relationships present in the original PDF format.

---
Created with ❤️ for Birla Brainiacs School
