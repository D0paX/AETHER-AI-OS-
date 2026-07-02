"""Conversation agent implementation."""

from typing import ClassVar, Any
import json
import time

from pydantic import BaseModel, Field
from aether.agents.base import BaseAgent, AgentTask, AgentContext, AgentResult
from aether.llm import ModelTier, Message
from aether.memory.models import MemoryType

class AgentDecision(BaseModel):
    """Schema for the LLM to output its decision."""
    thought: str = Field(description="Step-by-step reasoning for what to do next.")
    action: str | None = Field(None, description="The name of the tool to execute. Must be null if providing final_answer.")
    action_input: dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool.")
    final_answer: str | None = Field(None, description="The final response to the user. Must be null if executing an action.")

class ConversationAgent(BaseAgent):
    name: ClassVar[str] = "conversation_agent"
    role: ClassVar[str] = "Primary orchestrator for user interaction."
    llm_tier: ClassVar[ModelTier] = ModelTier.STANDARD
    allowed_tools: ClassVar[list[str]] = [
        "search",
        "clock",
        "task_manager",
        "store_memory",
        "recall_memory"
    ]
    max_iterations: ClassVar[int] = 10

    async def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        start_time = time.time()
        
        function_schemas = []
        # Get schemas for allowed tools safely
        try:
            function_schemas = self._tool_registry.get_function_schemas(self.allowed_tools)
        except Exception:
            pass # Ignore missing tools for robustness
            
        tool_descriptions = json.dumps(function_schemas, indent=2)

        # 1. System Prompt
        system_prompt = (
            f"You are Aether, a highly capable OS assistant.\n"
            f"Your Role: {self.role}\n\n"
            f"Task Description: {task.description}\n"
            f"Goal: {task.goal}\n\n"
            f"Memory Context:\n{context.memory_context.model_dump_json() if context.memory_context else 'None'}\n\n"
            f"Active Tasks:\n{[t.model_dump_json() for t in context.active_tasks]}\n\n"
            f"Available Tools:\n{tool_descriptions}\n\n"
            f"Instructions:\n"
            f"You must use the exact output schema provided. You can either use a tool by providing 'action' and 'action_input', OR provide a 'final_answer' to the user."
        )
        
        messages = [
            Message(role="system", content=system_prompt)
        ]
        
        # Inject conversation history
        messages.extend(context.conversation_history[-10:])

        actions_taken = []
        memories_created = []
        tasks_modified: list[str] = []
        llm_tokens = 0
        llm_cost = 0.0
        
        success = False
        final_response = ""
        error_msg = None
        
        # 2. ReAct loop
        for iteration in range(self.max_iterations):
            try:
                # LLM Call
                response = await self._llm_router.complete(
                    messages=messages,
                    tier=self.llm_tier,
                    response_schema=AgentDecision,
                    max_tokens=1000
                )
                
                llm_tokens += response.usage.total_tokens
                llm_cost += response.cost_usd
                
                # Parse structured output
                if not response.content:
                    raise ValueError("Empty response from LLM")
                    
                decision = AgentDecision.model_validate_json(response.content)
                
                # Record the agent's thought
                messages.append(Message(role="assistant", content=response.content))
                
                if decision.final_answer:
                    # Agent has reached a conclusion
                    final_response = decision.final_answer
                    success = True
                    break
                    
                if decision.action:
                    # Agent wants to execute a tool
                    tool_name = decision.action
                    tool_args = decision.action_input
                    actions_taken.append(tool_name)
                    
                    # Execute tool
                    tool_result = await self._invoke_tool(tool_name, tool_args)
                    
                    # Record tool result for next LLM turn
                    result_str = str(tool_result.data) if tool_result.success else f"Error: {tool_result.error}"
                    messages.append(Message(
                        role="user", 
                        content=f"Tool {tool_name} returned:\n{result_str}"
                    ))
                else:
                    # Neither action nor final_answer
                    messages.append(Message(
                        role="user", 
                        content="Error: You must specify either an action or a final_answer."
                    ))

            except Exception as e:
                error_msg = str(e)
                break
                
        if not success and not error_msg:
            error_msg = "Max iterations reached without final answer."

        # 3. Post-processing
        if success and final_response:
            try:
                # We save the interaction to episodic memory
                memory_id = await self._remember(
                    content=f"User Task: {task.description}\nResponse: {final_response}",
                    memory_type=MemoryType.EPISODE,
                    importance=0.7
                )
                memories_created.append(memory_id)
            except Exception as e:
                print(f"FAILED TO STORE MEMORY: {e}")
                pass # Non-fatal if memory storage fails

        duration_ms = int((time.time() - start_time) * 1000)
        
        # 4. Return AgentResult
        return AgentResult(
            run_id="pending", # Filled by AgentRuntime
            success=success,
            response=final_response,
            actions_taken=actions_taken,
            memories_created=memories_created,
            tasks_modified=tasks_modified,
            llm_tokens_used=llm_tokens,
            llm_cost_usd=llm_cost,
            duration_ms=duration_ms,
            error=error_msg
        )
