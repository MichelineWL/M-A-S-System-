"""
File upload and data processing handler.
Supports CSV and XLSX files with schema extraction.
"""

import pandas as pd
import os
import uuid
from pathlib import Path
from typing import Tuple, Dict, Any
from fastapi import UploadFile, HTTPException

from models.schemas import DataSchema
from config import settings
from utils.logger import logger


class FileHandler:
    """Handles file uploads, validation, and data processing."""
    
    def __init__(self):
        """Initialize file handler and ensure upload directory exists."""
        settings.ensure_upload_dir()
        self.upload_dir = Path(settings.upload_dir)
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    async def process_upload(self, file: UploadFile) -> Tuple[str, pd.DataFrame, DataSchema]:
        """
        Process uploaded file and extract schema.
        
        Args:
            file: Uploaded file from FastAPI
            
        Returns:
            Tuple of (session_id, dataframe, schema)
        """
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
        if file_ext not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(settings.allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        logger.info(f"Processing file: {file.filename} ({file_size} bytes)")
        
        # Generate session ID and save file
        session_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{session_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Load data into DataFrame
        try:
            if file_ext == 'csv':
                df = pd.read_csv(file_path)
            elif file_ext == 'xlsx':
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
        
        # Extract schema
        schema = self._extract_schema(df)
        
        # Store session data
        self.sessions[session_id] = {
            'df': df,
            'schema': schema,
            'filename': file.filename,
            'file_path': str(file_path)
        }
        
        logger.info(f"Session created: {session_id} with {len(df)} rows")
        
        return session_id, df, schema
    
    def _extract_schema(self, df: pd.DataFrame) -> DataSchema:
        """Extract schema information from DataFrame."""
        # Identify column types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Get sample data (first 5 rows)
        sample_data = df.head(5).fillna("").to_dict('records')
        
        # Create schema
        schema = DataSchema(
            columns=df.columns.tolist(),
            dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
            row_count=len(df),
            sample_data=sample_data,
            numeric_columns=numeric_cols,
            categorical_columns=categorical_cols,
            date_columns=date_cols
        )
        
        return schema
    
    def get_session_data(self, session_id: str) -> Tuple[pd.DataFrame, DataSchema, str]:
        """Retrieve session data."""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = self.sessions[session_id]
        return session['df'], session['schema'], session['filename']
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        return session_id in self.sessions


# Global file handler instance
file_handler = FileHandler()