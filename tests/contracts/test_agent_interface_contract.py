import pytest
from pydantic import ValidationError

from aether.agents.base import AgentTask, AgentContext, AgentResult
from aether.memory.models import ContextPackage

def test_agent_task_is_frozen():
    task = AgentTask(description="test", goal="test_goal")
    with pytest.raises(ValidationError):
        task.description = "new"

def test_agent_context_is_frozen():
    ctx = AgentContext(session_id="123", conversation_history=[], memory_context=ContextPackage(memories=[], total_found=0, token_estimate=0, formatted_context="", retrieval_query="", retrieval_duration_ms=0), active_tasks=[]) # Type error if None, but we can pass mock ContextPackage
    # Just checking model config
    assert AgentContext.model_config.get("frozen") is True

def test_agent_result_is_frozen():
    res = AgentResult(
        run_id="r1", 
        success=True, 
        response="", 
        actions_taken=[], 
        memories_created=[], 
        tasks_modified=[], 
        llm_tokens_used=0, 
        llm_cost_usd=0.0, 
        duration_ms=0
    )
    with pytest.raises(ValidationError):
        res.success = False
