"""
Visualization generation service.
Creates charts using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
import json
from typing import Optional, Dict, Any, List

from models.schemas import VisualizationData
from utils.logger import logger


class VisualizationService:
    """Handles chart generation and encoding."""
    
    @staticmethod
    def create_bar_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "",
        orientation: str = "v",  # 'v' for vertical, 'h' for horizontal
        color_col: Optional[str] = None
    ) -> VisualizationData:
        """Create a bar chart (vertical or horizontal)."""
        try:
            fig = px.bar(
                df, 
                x=x_col if orientation == 'v' else y_col,
                y=y_col if orientation == 'v' else x_col,
                title=title,
                color=color_col,
                orientation=orientation
            )
            chart_type = "horizontal_bar" if orientation == 'h' else "bar"
            return VisualizationService._convert_figure(fig, chart_type, title)
        except Exception as e:
            logger.error(f"Error creating bar chart: {str(e)}")
            raise
    
    @staticmethod
    def create_line_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "",
        color_col: Optional[str] = None,
        group_col: Optional[str] = None
    ) -> VisualizationData:
        """Create a line chart (single or multi-line)."""
        try:
            fig = px.line(
                df, 
                x=x_col, 
                y=y_col, 
                title=title,
                color=color_col or group_col
            )
            return VisualizationService._convert_figure(fig, "line", title)
        except Exception as e:
            logger.error(f"Error creating line chart: {str(e)}")
            raise
    
    @staticmethod
    def create_pie_chart(
        df: pd.DataFrame,
        names_col: str,
        values_col: str,
        title: str = ""
    ) -> VisualizationData:
        """Create a pie chart."""
        try:
            fig = px.pie(
                df,
                names=names_col,
                values=values_col,
                title=title
            )
            return VisualizationService._convert_figure(fig, "pie", title)
        except Exception as e:
            logger.error(f"Error creating pie chart: {str(e)}")
            raise
    
    @staticmethod
    def create_scatter_plot(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "",
        color_col: Optional[str] = None,
        size_col: Optional[str] = None
    ) -> VisualizationData:
        """Create a scatter plot."""
        try:
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                title=title,
                color=color_col,
                size=size_col,
                trendline="ols" if not color_col else None  # Add trendline for correlation
            )
            return VisualizationService._convert_figure(fig, "scatter", title)
        except Exception as e:
            logger.error(f"Error creating scatter plot: {str(e)}")
            raise
    
    @staticmethod
    def create_count_plot(
        df: pd.DataFrame,
        category_col: str,
        title: str = ""
    ) -> VisualizationData:
        """Create a count plot (bar chart of value counts)."""
        try:
            # Count occurrences
            counts = df[category_col].value_counts().reset_index()
            counts.columns = [category_col, 'count']
            
            fig = px.bar(
                counts,
                x=category_col,
                y='count',
                title=title
            )
            return VisualizationService._convert_figure(fig, "count", title)
        except Exception as e:
            logger.error(f"Error creating count plot: {str(e)}")
            raise
    
    @staticmethod
    def create_grouped_bar_chart(
        df: pd.DataFrame,
        x_col: str,
        y_cols: List[str],
        title: str = ""
    ) -> VisualizationData:
        """Create a grouped bar chart with multiple y columns."""
        try:
            fig = go.Figure()
            
            for y_col in y_cols:
                fig.add_trace(go.Bar(
                    x=df[x_col],
                    y=df[y_col],
                    name=y_col
                ))
            
            fig.update_layout(
                title=title,
                barmode='group',
                xaxis_title=x_col,
                yaxis_title='Values'
            )
            
            return VisualizationService._convert_figure(fig, "grouped_bar", title)
        except Exception as e:
            logger.error(f"Error creating grouped bar chart: {str(e)}")
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