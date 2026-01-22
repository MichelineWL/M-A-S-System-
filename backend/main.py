"""
Main FastAPI application for the Intelligent Data Room.
Exposes REST API endpoints for file upload and query processing.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from models import (
    QueryRequest,
    QueryResponse,
    UploadResponse,
    ErrorResponse,
    MessageRole
)
from services import file_handler, context_manager
from agents import planner_agent, executor_agent
from config import settings
from utils.logger import logger

# Create FastAPI app
app = FastAPI(
    title="Intelligent Data Room API",
    description="Multi-agent system for intelligent data analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Intelligent Data Room API",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a CSV or XLSX file for analysis."""
    try:
        logger.info(f"Received file upload: {file.filename}")
        
        # Process file upload
        session_id, df, schema = await file_handler.process_upload(file)
        
        # Create response
        response = UploadResponse(
            session_id=session_id,
            filename=file.filename,
            data_schema=schema
        )
        
        logger.info(f"File uploaded successfully: {session_id}")
        return response
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query using the multi-agent system."""
    try:
        logger.info(f"Processing query for session {request.session_id}: {request.query[:50]}...")
        
        # Get session data
        df, schema, filename = file_handler.get_session_data(request.session_id)
        
        # Get conversation context
        context = context_manager.get_formatted_history(request.session_id)
        
        # Add user message to context
        context_manager.add_message(
            request.session_id,
            MessageRole.USER,
            request.query
        )
        
        # STEP 1: Planner Agent analyzes query and creates execution plan
        logger.info("Step 1: Planner Agent analyzing query...")
        plan = await planner_agent.process(
            query=request.query,
            schema=schema,
            context=context if context_manager.has_context(request.session_id) else None
        )
        
        # Log planner output
        context_manager.add_message(
            request.session_id,
            MessageRole.PLANNER,
            f"Plan: {plan.query_understanding}",
            metadata={"steps": len(plan.steps)}
        )
        
        # STEP 2: Executor Agent executes the plan
        logger.info("Step 2: Executor Agent executing plan...")
        result = await executor_agent.process(
            plan=plan,
            df=df,
            original_query=request.query
        )
        
        # Log executor output
        context_manager.add_message(
            request.session_id,
            MessageRole.EXECUTOR,
            result.answer,
            metadata={"success": result.success}
        )
        
        # Add assistant message to context (final answer)
        context_manager.add_message(
            request.session_id,
            MessageRole.ASSISTANT,
            result.answer
        )
        
        # Create response
        response = QueryResponse(
            session_id=request.session_id,
            query=request.query,
            plan=plan,
            result=result,
            timestamp=datetime.now()
        )
        
        logger.info(f"Query processed successfully")
        return response
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{session_id}")
async def get_history(session_id: str, limit: int = None):
    """Get conversation history for a session."""
    try:
        # Check if session exists
        if not file_handler.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get history
        history = context_manager.get_history(session_id, limit)
        
        return {
            "session_id": session_id,
            "message_count": len(history),
            "messages": history
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and clear all associated data."""
    try:
        # Check if session exists
        if not file_handler.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Clear context
        context_manager.clear_session(session_id)
        
        logger.info(f"Session deleted: {session_id}")
        return {
            "message": "Session deleted successfully",
            "session_id": session_id
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Intelligent Data Room API...")
    logger.info(f"Server running on {settings.host}:{settings.port}")
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info"
    )