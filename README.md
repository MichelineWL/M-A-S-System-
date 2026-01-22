# Multi-Agent Data Analysis System (M-A-S)

An intelligent data analysis application powered by a multi-agent system using Google Gemini AI. Users can upload CSV/XLSX files and ask questions in natural language, with the system automatically generating insights and visualizations.

## Features

- **Multi-Agent Architecture**: Separate Planner and Executor agents for intelligent query processing
- **Natural Language Queries**: Ask questions about your data in plain English
- **Automatic Visualizations**: Charts are generated automatically when needed (Plotly)
- **Context Memory**: Remembers last 5 conversations for follow-up questions
- **Multiple Gemini Models**: Choose from Gemini 2.0 Flash, 2.5 Flash, 2.5 Pro, and more
- **Thinking vs Doing Mode**: Toggle between seeing the reasoning process or just execution steps
- **Real-time Processing**: Powered by PandasAI for dynamic code generation

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API Key ([Get it here](https://aistudio.google.com/apikey))

### Backend Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd M-A-S-System-/backend
```

2. **Create virtual environment**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
   Create `.env` file in `backend/` directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=./uploads
ALLOWED_EXTENSIONS=csv,xlsx
CONTEXT_WINDOW_SIZE=5
HOST=0.0.0.0
PORT=8000
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

5. **Run the backend**

```bash
python main.py
```

Backend will start at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**

```bash
cd ../frontend
```

2. **Install dependencies**

```bash
npm ci #clear install
```

3. **Run development server**

```bash
npm run dev
```

Frontend will start at `http://localhost:3000`

---

## 🏗️ Architecture

### Multi-Agent Communication Flow

```
User Question → Context Manager → Planner Agent → Executor Agent → Response
                      ↓                ↓               ↓
                  Conversation      Execution      Code +
                   History           Plan         Visualization
```

#### **1. Planner Agent** (The Thinker 🧠)

- **Role**: Analyzes user queries and creates execution plans
- **Input**: User query + data schema + conversation history
- **Output**: Structured execution plan with steps and reasoning
- **Process**:
  1. Understands what the user wants
  2. Examines available data columns
  3. Creates step-by-step plan
  4. Determines if visualization is needed

**Example Plan:**

```json
{
  "query_understanding": "User wants return rate per region",
  "thinking": "I'll look for 'Returned' column, group by Region, calculate percentage",
  "steps": [
    { "step_number": 1, "description": "Group by Region" },
    { "step_number": 2, "description": "Calculate return rate" },
    { "step_number": 3, "description": "Create bar chart" }
  ],
  "requires_visualization": true
}
```

#### **2. Executor Agent** (The Doer ⚡)

- **Role**: Executes the plan using PandasAI
- **Input**: Execution plan + DataFrame
- **Output**: Answer + visualization + code
- **Process**:
  1. Receives step-by-step instructions
  2. Generates Python/Pandas code dynamically
  3. Executes code safely
  4. Creates visualizations if required

#### **3. Agent Communication Protocol**

```python
# Step 1: User asks question
query = "What are the top 5 customers by sales?"

# Step 2: Context Manager retrieves conversation history
context = context_manager.get_conversation_context(session_id)

# Step 3: Planner Agent receives query + context + data schema
plan = await planner_agent.process(
    query=query,
    schema=data_schema,
    context=context  # Last 5 messages
)

# Step 4: Executor Agent receives plan + DataFrame
result = await executor_agent.process(
    plan=plan,
    df=dataframe,
    original_query=query
)

# Step 5: Context Manager stores the interaction
context_manager.add_message(session_id, MessageRole.ASSISTANT, result.answer)
```

---

## 💾 Context & Memory Management

### How We Handle Conversation Memory

#### **1. Context Window (Sliding Window Approach)**

- **Window Size**: Configurable (default: 5 messages)
- **Storage**: In-memory dictionary keyed by session_id
- **Structure**:

```python
{
  "session_id": {
    "messages": [
      {"role": "user", "content": "Show top customers"},
      {"role": "planner", "content": "Plan: Group by customer..."},
      {"role": "executor", "content": "Result: Customer A, B, C..."},
      {"role": "assistant", "content": "Here are the top customers..."}
    ],
    "metadata": {"last_query": "...", "data_columns": [...]}
  }
}
```

#### **2. Context Flow**

```
┌─────────────────────────────────────────────────────────┐
│ User: "Show top 5 customers"                            │
│ → Stored in Context                                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ AI: "Customer A: $50K, Customer B: $45K..."            │
│ → Stored in Context                                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ User: "Now show their locations" (Follow-up)           │
│ → Context Manager provides previous conversation       │
│ → Planner knows we're talking about the same customers │
└─────────────────────────────────────────────────────────┘
```

#### **3. Implementation Details**

**Context Manager Class:**

```python
class ContextManager:
    def __init__(self, window_size=5):
        self.sessions = {}
        self.window_size = window_size

    def add_message(self, session_id, role, content, metadata=None):
        # Add message to conversation history
        # Keep only last 'window_size' messages

    def get_conversation_context(self, session_id):
        # Retrieve recent messages for context
        # Format as string for agent consumption

    def has_context(self, session_id):
        # Check if session has conversation history
```

**Benefits:**

- **Follow-up Questions**: "Show more details" understands previous query
- **Pronoun Resolution**: "Show their revenue" knows who "their" refers to
- **Contextual Analysis**: Maintains conversation flow
- **Memory Efficiency**: Only stores recent messages (sliding window)

---

## 📋 API Documentation

### Endpoints

#### 1. Upload File

```http
POST /api/upload
Content-Type: multipart/form-data

file: <CSV/XLSX file>
```

**Response:**

```json
{
  "session_id": "uuid",
  "filename": "data.csv",
  "data_schema": {
    "columns": ["Name", "Sales", "Region"],
    "row_count": 1000,
    "dtypes": { "Name": "object", "Sales": "float64" }
  }
}
```

#### 2. Query Data

```http
POST /api/query
Content-Type: application/json

{
  "session_id": "uuid",
  "query": "What are the top 5 customers?",
  "model_name": "gemini-1.5-flash"
}
```

**Response:**

```json
{
  "plan": {
    "query_understanding": "User wants top 5 customers by sales",
    "thinking": "Group by customer, sum sales, sort, take top 5",
    "steps": [...],
    "requires_visualization": false
  },
  "result": {
    "success": true,
    "answer": "Top 5 customers: ...",
    "visualization": null
  }
}
```

---

## 🎨 Tech Stack

### Backend

- **Framework**: FastAPI
- **AI/LLM**: Google Gemini API (google-genai SDK)
- **Data Processing**: Pandas, PandasAI
- **Visualization**: Plotly, Matplotlib
- **File Handling**: python-multipart, openpyxl

### Frontend

- **Framework**: Next.js 14 (React + TypeScript)
- **UI Components**: shadcn/ui, Tailwind CSS
- **Charts**: Plotly.js
- **HTTP Client**: Axios
- **Icons**: Lucide React

---

## Usage Examples

### Example 1: Basic Query

```
User: "What are the total sales by region?"

Planner Agent:
- Understanding: Calculate sum of sales grouped by region
- Steps: Group by Region → Sum Sales → Sort descending

Executor Agent:
- Generates: df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
- Returns: Table with regions and sales
```

### Example 2: Visualization Request

```
User: "Show me a chart of monthly sales trends"

Planner Agent:
- Understanding: Create line chart showing sales over time
- Requires Visualization: TRUE (line chart)

Executor Agent:
- Generates: Plotly line chart
- Returns: Interactive chart + data
```

### Example 3: Follow-up Question (Context Memory)

```
User: "Who are the top 5 customers?"
AI: "Here are the top 5: Customer A ($50K), Customer B ($45K)..."

User: "Show their regions"
AI: [Uses context to know we're still talking about those 5 customers]
    "Customer A: East, Customer B: West..."
```

---

## 🔧 Configuration

### Model Selection

Available models in `config.py`:

- `gemini-2.0-flash` - Fast and efficient (2K RPM)
- `gemini-2.5-flash` - High performance (1K RPM)
- `gemini-2.5-pro` - Most powerful (150 RPM)
- `gemini-1.5-flash` - Stable legacy model

### Context Window

Adjust in `.env`:

```env
CONTEXT_WINDOW_SIZE=5  # Number of messages to remember
```

### Display Mode

Users can toggle between:

- **Both**: Shows Thinking + Doing
- **Thinking Only**: Shows reasoning process
- **Doing Only**: Shows execution steps

---

## Acknowledgments

- Google Gemini API for powerful language models
- PandasAI for intelligent DataFrame operations
- FastAPI and Next.js communities for excellent frameworks

---
