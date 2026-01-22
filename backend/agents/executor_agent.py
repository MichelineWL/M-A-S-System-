"""
Executor Agent - Executes plans using PandasAI and generates results.
"""

import pandas as pd
from typing import Optional, Any
from pandasai import SmartDataframe
from pandasai.llm import GoogleGemini

from agents.base_agent import BaseAgent
from models.schemas import ExecutionPlan, ExecutionResult, VisualizationData
from utils.prompts import EXECUTOR_SYSTEM_PROMPT
from utils.logger import logger
from config import settings


class ExecutorAgent(BaseAgent):
    """Agent responsible for executing plans and generating results."""
    
    def __init__(self):
        """Initialize Executor Agent."""
        super().__init__(EXECUTOR_SYSTEM_PROMPT)
        
        # Initialize PandasAI with Gemini
        self.pandas_llm = GoogleGemini(api_key=settings.gemini_api_key)
    
    async def process(
        self,
        plan: ExecutionPlan,
        df: pd.DataFrame,
        original_query: str
    ) -> ExecutionResult:
        """Execute the plan and generate results."""
        logger.info(f"Executor processing plan with {len(plan.steps)} steps")
        
        try:
            # Use PandasAI to execute the query
            answer, result_data = await self._execute_with_pandasai(df, original_query, plan)
            
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
        plan: ExecutionPlan
    ) -> tuple[str, Any]:
        """Execute query using PandasAI."""
        try:
            # Create SmartDataframe
            sdf = SmartDataframe(
                df,
                config={
                    "llm": self.pandas_llm,
                    "verbose": True,
                    "enable_cache": False
                }
            )
            
            # Execute query
            logger.debug(f"Executing PandasAI query: {query[:100]}...")
            result = sdf.chat(query)
            
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
        """Generate visualization based on plan."""
        try:
            from services.visualization_service import visualization_service
            
            # Use result data if it's a DataFrame, otherwise use original df
            viz_df = result_data if isinstance(result_data, pd.DataFrame) else df
            
            # Get visualization type
            viz_type = plan.visualization_type.lower()
            
            # Determine columns intelligently
            numeric_cols = viz_df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = viz_df.select_dtypes(include=['object']).columns.tolist()
            
            if not numeric_cols:
                logger.warning("No numeric columns found for visualization")
                return None
            
            # Create visualization based on type
            if viz_type in ['bar', 'column']:
                x_col = categorical_cols[0] if categorical_cols else viz_df.columns[0]
                y_col = numeric_cols[0]
                return visualization_service.create_bar_chart(
                    df=viz_df.head(20),  # Limit to 20 rows for clarity
                    x_col=x_col,
                    y_col=y_col,
                    title=plan.query_understanding
                )
            
            elif viz_type == 'line':
                x_col = viz_df.columns[0]
                y_col = numeric_cols[0]
                return visualization_service.create_line_chart(
                    df=viz_df,
                    x_col=x_col,
                    y_col=y_col,
                    title=plan.query_understanding
                )
            
            else:
                logger.info(f"Visualization type '{viz_type}' not yet implemented")
                return None
        
        except Exception as e:
            logger.error(f"Visualization generation error: {str(e)}")
            return None


# Global executor agent instance
executor_agent = ExecutorAgent()