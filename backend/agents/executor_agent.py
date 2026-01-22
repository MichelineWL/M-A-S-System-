"""
Executor Agent - Executes plans using PandasAI and generates results.
"""

import pandas as pd
from typing import Optional, Any
from pandasai import SmartDataframe

from agents.base_agent import BaseAgent
from models.schemas import ExecutionPlan, ExecutionResult, VisualizationData
from utils.prompts import EXECUTOR_SYSTEM_PROMPT
from utils.logger import logger
from utils.custom_gemini_llm import CustomGeminiLLM
from config import settings


class ExecutorAgent(BaseAgent):
    """Agent responsible for executing plans and generating results."""
    
    def __init__(self):
        """Initialize Executor Agent."""
        super().__init__(EXECUTOR_SYSTEM_PROMPT)
    
    async def process(
        self,
        plan: ExecutionPlan,
        df: pd.DataFrame,
        original_query: str,
        model_name: Optional[str] = None
    ) -> ExecutionResult:
        """Execute the plan and generate results."""
        logger.info(f"Executor processing plan with {len(plan.steps)} steps")
        
        try:
            # Use PandasAI to execute the query
            answer, result_data = await self._execute_with_pandasai(
                df, original_query, plan, model_name
            )
            
            # Generate visualization if requested
            visualization = None
            if plan.requires_visualization and plan.visualization_type:
                visualization = await self._generate_visualization(
                    df, result_data, plan, original_query
                )
            
            result = ExecutionResult(
                success=True,
                answer=answer,
                code_executed="# Executed via PandasAI",
                visualization=visualization,  # ← Now can have chart data!
                error=None
            )
            
            logger.info("Executor completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Executor error: {str(e)}")
            return ExecutionResult(
                success=False,
                answer="",
                code_executed=None,
                visualization=None,
                error=str(e)
            )
    
    async def _execute_with_pandasai(
        self,
        df: pd.DataFrame,
        query: str,
        plan: ExecutionPlan,
        model_name: Optional[str] = None
    ) -> tuple[str, Any]:
        """Execute query using PandasAI."""
        try:
            # Create PandasAI LLM with dynamic model selection using our custom wrapper
            model = model_name or "gemini-1.5-flash"
            
            # Use custom Gemini LLM that properly supports model selection
            pandas_llm = CustomGeminiLLM(
                api_key=settings.gemini_api_key,
                model=model
            )
            
            logger.info(f"Using PandasAI with model: {model}")
            
            # Create SmartDataframe
            sdf = SmartDataframe(
                df,
                config={
                    "llm": pandas_llm,
                    "verbose": True,
                    "enable_cache": False
                }
            )
            
            # Execute query
            logger.debug(f"Executing PandasAI query: {query[:100]}...")
            
            try:
                result = sdf.chat(query)
            except Exception as pandasai_error:
                error_msg = str(pandasai_error)
                
                # Handle common PandasAI errors with better messages
                if "No code found in the response" in error_msg:
                    logger.warning(f"PandasAI 'No code found' error - retrying with simpler query")
                    # Try a second time with more explicit instruction
                    result = sdf.chat(f"Write Python code to: {query}")
                elif "NoneType" in error_msg:
                    raise Exception("PandasAI returned None. The model may not have understood the query. Try rephrasing your question.")
                else:
                    raise
            
            # Format result
            answer = self._format_result(result)
            
            return answer, result  # returns both answer and raw result
            
        except Exception as e:
            logger.error(f"PandasAI execution error: {str(e)}")
            raise
    
    def _format_result(self, result) -> str:
        """Format PandasAI result into a user-friendly answer."""
        if isinstance(result, pd.DataFrame):
            return f"**Results:**\n\n{result.to_markdown(index=False)}"
        elif isinstance(result, (int, float)):
            return f"**Answer:** {result:,.2f}" if isinstance(result, float) else f"**Answer:** {result:,}"
        else:
            return f"**Answer:** {str(result)}"

    async def _generate_visualization(
        self,
        df: pd.DataFrame,
        result_data: Any,
        plan: ExecutionPlan,
        query: str
    ) -> Optional[VisualizationData]:
        """Generate visualization based on plan and query analysis."""
        try:
            from services.visualization_service import visualization_service
            
            # Use result data if it's a DataFrame, otherwise use original df
            viz_df = result_data if isinstance(result_data, pd.DataFrame) else df
            
            # Get visualization type
            viz_type = plan.visualization_type.lower() if plan.visualization_type else "bar"
            
            # Analyze query for better chart selection
            query_lower = query.lower()
            
            # Auto-detect chart type from query if not specified
            if 'pie' in query_lower or 'distribution' in query_lower:
                viz_type = 'pie'
            elif 'scatter' in query_lower or 'correlation' in query_lower or 'relationship' in query_lower:
                viz_type = 'scatter'
            elif 'count' in query_lower or 'how many' in query_lower:
                viz_type = 'count'
            elif 'horizontal' in query_lower:
                viz_type = 'horizontal_bar'
            elif 'trend' in query_lower or 'over time' in query_lower or 'line' in query_lower:
                viz_type = 'line'
            
            # Determine columns intelligently
            numeric_cols = viz_df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = viz_df.select_dtypes(include=['object']).columns.tolist()
            date_cols = viz_df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # Title
            title = plan.query_understanding if plan.query_understanding else query
            
            # Create visualization based on type
            if viz_type == 'pie':
                if len(categorical_cols) == 0 or len(numeric_cols) == 0:
                    logger.warning("Insufficient columns for pie chart")
                    return None
                
                # Aggregate data for pie chart
                names_col = categorical_cols[0]
                values_col = numeric_cols[0]
                
                # Aggregate if needed
                if len(viz_df) > 20:
                    agg_df = viz_df.groupby(names_col)[values_col].sum().reset_index()
                    agg_df = agg_df.nlargest(10, values_col)  # Top 10
                else:
                    agg_df = viz_df
                
                return visualization_service.create_pie_chart(
                    df=agg_df,
                    names_col=names_col,
                    values_col=values_col,
                    title=title
                )
            
            elif viz_type == 'scatter':
                if len(numeric_cols) < 2:
                    logger.warning("Need at least 2 numeric columns for scatter plot")
                    return None
                
                return visualization_service.create_scatter_plot(
                    df=viz_df,
                    x_col=numeric_cols[0],
                    y_col=numeric_cols[1],
                    color_col=categorical_cols[0] if categorical_cols else None,
                    title=title
                )
            
            elif viz_type == 'count':
                if len(categorical_cols) == 0:
                    logger.warning("Need categorical column for count plot")
                    return None
                
                return visualization_service.create_count_plot(
                    df=viz_df,
                    category_col=categorical_cols[0],
                    title=title
                )
            
            elif viz_type == 'horizontal_bar':
                x_col = categorical_cols[0] if categorical_cols else viz_df.columns[0]
                y_col = numeric_cols[0] if numeric_cols else viz_df.columns[1]
                
                # Sort and limit
                viz_df = viz_df.nlargest(10, y_col) if len(viz_df) > 10 else viz_df
                
                return visualization_service.create_bar_chart(
                    df=viz_df,
                    x_col=x_col,
                    y_col=y_col,
                    title=title,
                    orientation='h'
                )
            
            elif viz_type in ['bar', 'column']:
                x_col = categorical_cols[0] if categorical_cols else viz_df.columns[0]
                
                # Check if we need grouped bar chart (multiple y columns requested)
                if 'and' in query_lower and len(numeric_cols) >= 2:
                    # Grouped bar chart for multiple metrics
                    return visualization_service.create_grouped_bar_chart(
                        df=viz_df.head(20),
                        x_col=x_col,
                        y_cols=numeric_cols[:2],  # Take first 2 numeric columns
                        title=title
                    )
                else:
                    # Single bar chart
                    y_col = numeric_cols[0] if numeric_cols else viz_df.columns[1]
                    return visualization_service.create_bar_chart(
                        df=viz_df.head(20),
                        x_col=x_col,
                        y_col=y_col,
                        title=title
                    )
            
            elif viz_type == 'line':
                # Determine x and y columns
                if date_cols:
                    x_col = date_cols[0]
                elif categorical_cols:
                    x_col = categorical_cols[0]
                else:
                    x_col = viz_df.columns[0]
                
                y_col = numeric_cols[0] if numeric_cols else viz_df.columns[1]
                
                # Check for multi-line (grouped by category)
                group_col = None
                if len(categorical_cols) > 1:
                    group_col = categorical_cols[1] if categorical_cols[0] == x_col else categorical_cols[0]
                
                return visualization_service.create_line_chart(
                    df=viz_df,
                    x_col=x_col,
                    y_col=y_col,
                    group_col=group_col,
                    title=title
                )
            
            else:
                logger.info(f"Visualization type '{viz_type}' not yet implemented")
                return None
        
        except Exception as e:
            logger.error(f"Visualization generation error: {str(e)}")
            return None


# Global executor agent instance
executor_agent = ExecutorAgent()