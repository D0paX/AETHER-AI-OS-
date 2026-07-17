"""Conversation agent implementation."""

import asyncio
import contextlib
import json
import time
from typing import Any, ClassVar

import structlog
from pydantic import BaseModel, Field, ValidationError

from aether.agents.base import AgentContext, AgentResult, AgentTask, BaseAgent
from aether.core.exceptions import AetherError
from aether.llm import Message, ModelTier
from aether.memory.models import MemoryType

logger = structlog.get_logger(__name__)

# Importance for an explicitly-stated durable fact captured in the moment,
# distinctly above the 0.7 per-turn episode importance so recall favours the
# clean fact over the generic episode (M2.1.8).
EXPLICIT_FACT_IMPORTANCE: float = 0.85


class AgentDecision(BaseModel):
    """Schema for the LLM to output its decision."""

    thought: str = Field(description="Step-by-step reasoning for what to do next.")
    action: str | None = Field(
        None, description="The name of the tool to execute. Must be null if providing final_answer."
    )
    action_input: dict[str, Any] = Field(
        default_factory=dict, description="Arguments for the tool."
    )
    final_answer: str | None = Field(
        None, description="The final response to the user. Must be null if executing an action."
    )


class FactCheckResult(BaseModel):
    """Schema for the per-turn explicit-fact recognition check (M2.1.8)."""

    contains_fact: bool = Field(
        description="True only if the user stated a durable personal fact worth "
        "remembering long-term (name, preference, role, project, relationship, etc.)."
    )
    fact_statement: str | None = Field(
        default=None,
        description="If contains_fact is true, a single clean third-person sentence "
        "restating the fact with 'The user' as the subject, copying the user's own "
        'words and names exactly (e.g. "The user works as a nurse."). Otherwise null.',
    )


class ConversationAgent(BaseAgent):
    name: ClassVar[str] = "conversation_agent"
    role: ClassVar[str] = "Primary orchestrator for user interaction."
    llm_tier: ClassVar[ModelTier] = ModelTier.STANDARD
    # Tool names match the registered tools exactly (V1_TECHNICAL_SPECIFICATION.md
    # Section 8.6) — M2.1.6 correction from the prior nonexistent names.
    allowed_tools: ClassVar[list[str]] = [
        "get_current_datetime",
        "web_search",
        "create_task",
        "list_tasks",
        "update_task_status",
    ]
    max_iterations: ClassVar[int] = 10

    # M2.1.8: handle to the non-blocking per-turn fact-capture task, tracked so
    # callers (and tests) can await its completion explicitly rather than
    # relying on a timing hack. Set per execute(); None when no user text.
    _fact_check_task: "asyncio.Task[None] | None" = None

    async def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        start_time = time.time()

        function_schemas = []
        # Get schemas for allowed tools safely — ignore missing tools for robustness
        with contextlib.suppress(Exception):
            function_schemas = self._tool_registry.get_function_schemas(self.allowed_tools)

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
            f"You must use the exact output schema provided. You can either use a tool by providing 'action' and 'action_input', OR provide a 'final_answer' to the user.\n"
            f"If the user's message does not require a tool - a greeting, a "
            f"statement to acknowledge, or a question you can answer from the "
            f"conversation and memory context above - respond immediately with "
            f"'final_answer' and leave 'action' null. Only call a tool when you "
            f"genuinely need external information or an action performed."
        )

        messages = [Message(role="system", content=system_prompt)]

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
        for _iteration in range(self.max_iterations):
            try:
                # LLM Call
                response = await self._llm_router.complete(
                    messages=messages,
                    tier=self.llm_tier,
                    response_schema=AgentDecision,
                    max_tokens=1000,
                )

                # M2.1.6 fix: LLMResponse carries token counts at top level
                # (V1_TECHNICAL_SPECIFICATION.md Section 2.4); it has no
                # .usage attribute — the old access crashed every real call.
                llm_tokens += response.total_tokens
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
                    result_str = (
                        str(tool_result.data)
                        if tool_result.success
                        else f"Error: {tool_result.error}"
                    )
                    messages.append(
                        Message(role="user", content=f"Tool {tool_name} returned:\n{result_str}")
                    )
                else:
                    # Neither action nor final_answer
                    messages.append(
                        Message(
                            role="user",
                            content="Error: You must specify either an action or a final_answer.",
                        )
                    )

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
                    importance=0.7,
                )
                memories_created.append(memory_id)
            except Exception as e:
                # Non-fatal: the turn succeeded even if episodic storage failed.
                logger.warning("conversation.memory_store.failed", error=str(e))

        # 4. M2.1.8: fire immediate explicit-fact capture as a NON-BLOCKING
        # background task. Everything above — the conversational response and its
        # result — is unchanged and already final; this neither delays nor
        # affects the reply the user sees.
        self._fact_check_task = self._launch_fact_check(task, context)

        duration_ms = int((time.time() - start_time) * 1000)

        # 5. Return AgentResult
        return AgentResult(
            run_id="pending",  # Filled by AgentRuntime
            success=success,
            response=final_response,
            actions_taken=actions_taken,
            memories_created=memories_created,
            tasks_modified=tasks_modified,
            llm_tokens_used=llm_tokens,
            llm_cost_usd=llm_cost,
            duration_ms=duration_ms,
            error=error_msg,
        )

    def _launch_fact_check(
        self, task: AgentTask, context: AgentContext
    ) -> "asyncio.Task[None] | None":
        """Fire the per-turn fact-capture task if the turn carried user text.

        Uses the same non-blocking asyncio.create_task pattern as
        SessionManager.end_session's consolidation trigger. Returns the task
        handle (tracked so callers/tests can await it) or None when there is no
        user text to check. The user text comes from task.input_data["text"],
        set by the interfaces (M2.1.6).
        """
        user_text = task.input_data.get("text", "")
        if not user_text:
            return None
        return asyncio.create_task(self._check_for_explicit_fact(user_text, context.session_id))

    async def _check_for_explicit_fact(self, user_text: str, session_id: str) -> None:
        """Recognize an explicit durable fact in a turn and store it immediately.

        Runs as a background task, uses the free local tier, and is fully
        isolated from the conversational reply (which has already been returned).
        Any failure here is logged and swallowed at this boundary — it never
        surfaces to the user or affects the turn.

        Args:
            user_text: The user's message for this turn.
            session_id: The active session/conversation id (for log context;
                storage uses the agent's own session via self._remember).
        """
        try:
            system_prompt = (
                "You extract durable personal facts from a user's message for "
                "long-term memory. A durable fact is a lasting piece of personal "
                "information: the user's name, a stable preference, their role or "
                "job, a project they are working on, a relationship, and the like. "
                "Transient chit-chat, questions, greetings, and one-off requests "
                "are NOT durable facts.\n"
                "If the message states such a fact, set contains_fact=true and "
                "write ONE clean sentence restating it in the third person, using "
                "'The user' as the subject and copying the user's own words and "
                "names EXACTLY. Never invent, change, or add any name or detail the "
                "user did not state. For example, 'I work as a nurse' becomes 'The "
                "user works as a nurse.', and 'My name is Sam' becomes 'The user's "
                "name is Sam.'\n"
                "Otherwise set contains_fact=false and fact_statement=null."
            )
            response = await self._llm_router.complete(
                messages=[
                    Message(role="system", content=system_prompt),
                    Message(role="user", content=user_text),
                ],
                tier=ModelTier.LOCAL,
                response_schema=FactCheckResult,
                max_tokens=200,
            )
            if not response.content:
                return
            result = FactCheckResult.model_validate_json(response.content)
            if result.contains_fact and result.fact_statement:
                await self._remember(
                    content=result.fact_statement,
                    memory_type=MemoryType.FACT,
                    importance=EXPLICIT_FACT_IMPORTANCE,
                )
                logger.info(
                    "conversation.fact_captured",
                    session_id=session_id,
                    fact=result.fact_statement[:100],
                )
        except (AetherError, ValidationError) as e:
            # A malformed local-model response (ValidationError) or an LLM/memory
            # failure (AetherError) must never affect the already-returned reply.
            logger.warning(
                "conversation.fact_check.failed",
                session_id=session_id,
                error=str(e),
                error_type=type(e).__name__,
            )
