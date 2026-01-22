"""
Visualization generation service.
Creates charts using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
import json
from typing import Optional, Dict, Any

from models.schemas import VisualizationData
from utils.logger import logger


class VisualizationService:
    """Handles chart generation and encoding."""
    
    @staticmethod
    def create_bar_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = ""
    ) -> VisualizationData:
        """Create a bar chart."""
        try:
            fig = px.bar(df, x=x_col, y=y_col, title=title)
            return VisualizationService._convert_figure(fig, "bar", title)
        except Exception as e:
            logger.error(f"Error creating bar chart: {str(e)}")
            raise
    
    @staticmethod
    def create_line_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = ""
    ) -> VisualizationData:
        """Create a line chart."""
        try:
            fig = px.line(df, x=x_col, y=y_col, title=title)
            return VisualizationService._convert_figure(fig, "line", title)
        except Exception as e:
            logger.error(f"Error creating line chart: {str(e)}")
            raise
    
    @staticmethod
    def _convert_figure(
        fig: go.Figure,
        chart_type: str,
        title: str
    ) -> VisualizationData:
        """Convert Plotly figure to VisualizationData."""
        # Convert to JSON (for interactive display)
        plotly_json = json.loads(fig.to_json())
        
        return VisualizationData(
            chart_type=chart_type,
            image_base64=None,
            plotly_json=plotly_json,
            title=title,
            description=f"{chart_type.capitalize()} chart: {title}"
        )


# Global visualization service instance
visualization_service = VisualizationService()