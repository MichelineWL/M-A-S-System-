### Project Flow
#### Frontend:
- User uploads CSV/XLSX file (max 10MB).
- User enters natural language question.
- User optionally selects LLM version (or whether they want "thinking" vs. "doing").
- Frontend sends a POST request to your backend with:
  - The uploaded CSV file (or base64-encoded if needed).
  - The question.
  - The chosen LLM mode (e.g., Gemini Pro, etc.).

#### Backend:
- Receives the request.
- Parses the CSV file into a Pandas DataFrame.
- Sends schema + question to Agent 1 (Planner) → gets back an execution plan.
- Sends plan + DataFrame to Agent 2 (Executor) → uses PandasAI + Gemini to run code.
- Returns final result (text or chart image/data
  (If the user asks for a trend or comparison, the app should automatically render a chart (using Plotly, Recharts, or Matplotlib))
  ) + optional plan steps to frontend.

#### Frontend:
- Receives and displays the response:
- Answer (text or table).
- Optional chart or debug plan output.

### Tech Stack: 
Backend/AI: Python, PandasAI, Google Gemini API (Recommended).
Frontend/UI: Streamlit (for speed) OR React/TypeScript .
Hosting: GitHub (Code) + Streamlit Cloud/Vercel (Live Link).
