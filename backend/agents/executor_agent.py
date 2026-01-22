"""
Executor Agent - Executes plans using PandasAI and generates results.
"""

import pandas as pd
from typing import Optional
from pandasai import SmartDataframe
from pandasai.llm import GoogleGemini

from agents.base_agent import BaseAgent
from models.schemas import ExecutionPlan, ExecutionResult
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
            answer = await self._execute_with_pandasai(df, original_query, plan)
            
            result = ExecutionResult(
                success=True,
                answer=answer,
                code_executed="# Executed via PandasAI",
                visualization=None,
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
    ) -> str:
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
            
            return answer
        
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


# Global executor agent instance
executor_agent = ExecutorAgent()