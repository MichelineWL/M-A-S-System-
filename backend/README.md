# Intelligent Data Room - Backend

An intelligent multi-agent data analysis system that allows users to "talk" to their data. Built with Python, FastAPI, PandasAI, and Google Gemini.

## 🚀 Features

- **Multi-Agent Architecture**:
  - **Planner Agent**: Analyzes queries and plans execution steps.
  - **Executor Agent**: Executes code and generates analysis using PandasAI.
- **Smart Data Upload**: Supports CSV and XLSX files (up to 10MB).
- **Interactive Querying**: Natural language interface for data analysis.
- **Auto-Visualization**: Automatically generates Plotly charts when requested.
- **Context Retention**: Remembers conversation history for follow-up questions.

## 🛠️ Prerequisites

- Python 3.10 or 3.11 (Python 3.13 is NOT supported due to dependency issues)
- Google Gemini API Key

## 📦 Setup Instructions

1. **Create Virtual Environment**
   ```bash
   # Windows
   py -3.11 -m venv venv
   .\venv\Scripts\Activate
   
   # Linux/Mac
   python3.11 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   - Copy `.env.example` to `.env` (or create new `.env`)
   - Add your Google Gemini API key:
     ```env
     GEMINI_API_KEY=your_api_key_here
     ```

## 🏃‍♂️ Running the Server

Start the backend server:

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**

## 📚 API Documentation

Once running, explore the interactive API docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/upload`: Upload a file (CSV/XLSX)
- `POST /api/query`: Ask a question about the uploaded data
- `GET /api/history/{session_id}`: Get conversation history

## 🧪 Testing with Sample Data

1. Use the provided `sample_sales.csv` for testing.
2. Upload via `/api/upload`.
3. Try these queries:
   - "Show me the top 5 products by sales"
   - "Plot monthly sales trend as a line chart"
   - "What is the total profit by region? Show as bar chart"
