"""
Planner Agent - Analyzes queries and creates execution plans.
"""

import json
from typing import Optional

from agents.base_agent import BaseAgent
from models.schemas import ExecutionPlan, ExecutionStep, DataSchema
from utils.prompts import PLANNER_SYSTEM_PROMPT
from utils.logger import logger


class PlannerAgent(BaseAgent):
    """Agent responsible for analyzing user queries and creating execution plans."""
    
    def __init__(self):
        """Initialize Planner Agent with system prompt."""
        super().__init__(PLANNER_SYSTEM_PROMPT)
    
    async def process(
        self,
        query: str,
        schema: DataSchema,
        context: Optional[str] = None
    ) -> ExecutionPlan:
        """Analyze query and create execution plan."""
        logger.info(f"Planner processing query: {query[:50]}...")
        
        # Create structured input for the planner
        input_data = self._format_input(query, schema, context)
        
        # Create prompt
        prompt = self._create_prompt(input_data, context)
        
        # Call Gemini
        response = await self._call_gemini(prompt)
        
        # Parse response into ExecutionPlan
        plan = self._parse_plan(response)
        
        logger.info(f"Planner created plan with {len(plan.steps)} steps")
        return plan
    
    def _format_input(
        self,
        query: str,
        schema: DataSchema,
        context: Optional[str] = None
    ) -> str:
        """Format input data for the planner."""
        input_parts = [
            f"QUERY: {query}",
            "",
            "DATA SCHEMA:",
            f"- Columns: {', '.join(schema.columns)}",
            f"- Numeric columns: {', '.join(schema.numeric_columns)}",
            f"- Categorical columns: {', '.join(schema.categorical_columns)}",
            f"- Total rows: {schema.row_count}",
            "",
            "Please create a step-by-step execution plan in JSON format."
        ]
        
        return "\n".join(input_parts)
    
    def _parse_plan(self, response: str) -> ExecutionPlan:
        """Parse Gemini response into ExecutionPlan."""
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.index("```json") + 7
                json_end = response.index("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                json_start = response.index("{")
                json_end = response.rindex("}") + 1
                json_str = response[json_start:json_end]
            else:
                json_str = response
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Create ExecutionStep objects
            steps = [
                ExecutionStep(
                    step_number=step.get('step_number', i + 1),
                    description=step.get('description', ''),
                    reasoning=step.get('reasoning')
                )
                for i, step in enumerate(data.get('steps', []))
            ]
            
            # Create ExecutionPlan
            plan = ExecutionPlan(
                query_understanding=data.get('query_understanding', ''),
                steps=steps,
                expected_output_type=data.get('expected_output_type', 'text'),
                requires_visualization=data.get('requires_visualization', False),
                visualization_type=data.get('visualization_type')
            )
            
            return plan
        
        except Exception as e:
            logger.error(f"Error parsing plan: {str(e)}")
            
            # Fallback: create a simple plan
            return ExecutionPlan(
                query_understanding=f"Process query: {response[:100]}",
                steps=[
                    ExecutionStep(
                        step_number=1,
                        description="Execute query on data",
                        reasoning="Fallback plan due to parsing error"
                    )
                ],
                expected_output_type='text',
                requires_visualization=False
            )


# Global planner agent instance
planner_agent = PlannerAgent()