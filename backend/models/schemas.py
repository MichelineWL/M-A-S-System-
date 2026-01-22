"""
Pydantic models for request/response validation and data structures.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Role of a message in the conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    PLANNER = "planner"
    EXECUTOR = "executor"


class ConversationMessage(BaseModel):
    """A single message in the conversation history."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class ExecutionStep(BaseModel):
    """A single step in the execution plan."""
    step_number: int
    description: str
    reasoning: Optional[str] = None


class ExecutionPlan(BaseModel):
    """Planner agent's output structure."""
    query_understanding: str
    steps: List[ExecutionStep]
    expected_output_type: str  # e.g., "table", "chart", "text"
    requires_visualization: bool = False
    visualization_type: Optional[str] = None  # e.g., "bar", "line", "scatter"


class DataSchema(BaseModel):
    """Schema information about uploaded data."""
    columns: List[str]
    dtypes: Dict[str, str]
    row_count: int
    sample_data: List[Dict[str, Any]]
    numeric_columns: List[str]
    categorical_columns: List[str]
    date_columns: List[str]


class UploadResponse(BaseModel):
    """Response after successful file upload."""
    session_id: str
    filename: str
    data_schema: DataSchema  
    message: str = "File uploaded successfully"


class QueryRequest(BaseModel):
    """Request to query the data."""
    session_id: str
    query: str
    model_name: Optional[str] = "gemini-1.5-flash"  # Default model


class VisualizationData(BaseModel):
    """Visualization output data."""
    chart_type: str
    image_base64: Optional[str] = None
    plotly_json: Optional[Dict[str, Any]] = None
    title: str
    description: Optional[str] = None


class ExecutionResult(BaseModel):
    """Result from the executor agent."""
    success: bool
    answer: str
    code_executed: Optional[str] = None
    visualization: Optional[VisualizationData] = None
    error: Optional[str] = None


class QueryResponse(BaseModel):
    """Complete response to a query."""
    session_id: str
    query: str
    plan: ExecutionPlan
    result: ExecutionResult
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)