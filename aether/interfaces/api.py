"""Aether internal REST API (localhost only).

Serves the voice service and future interface surfaces. Contains zero
business logic: the conversation endpoint flows through
SessionManager.build_agent_context() -> AgentRuntime.execute() ->
SessionManager.update_context(), exactly like the CLI (M2.1.6).
"""

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from aether.agents.base import AgentTask
from aether.llm import Message
from aether.session.models import SessionMode

app = FastAPI(title="Aether Internal API", docs_url=None, redoc_url=None)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": str(exc), "type": type(exc).__name__})


class MessageRequest(BaseModel):
    session_id: str = ""
    content: str
    mode: str = "text"


@app.post("/conversation/message")
async def conversation_message(req: MessageRequest, request: Request) -> dict[str, Any]:
    kernel = request.app.state.kernel
    if not kernel:
        raise HTTPException(status_code=500, detail="Kernel not initialized")

    # Get or create the session: an empty session_id starts a new session.
    if req.session_id:
        session_id = req.session_id
    else:
        session = await kernel.session_manager.start_session(SessionMode.TEXT)
        session_id = session.id

    context = await kernel.session_manager.build_agent_context(session_id, req.content)
    task = AgentTask(
        description="Conversational turn",
        goal="Respond to the user's message",
        input_data={"text": req.content},
    )
    result = await kernel.agent_runtime.execute("conversation", task, context)

    # Exactly the new turn's two messages — never the accumulated history
    # (M2.1.5 delta contract).
    await kernel.session_manager.update_context(
        session_id,
        new_messages=[
            Message(role="user", content=req.content),
            Message(role="assistant", content=result.response),
        ],
    )

    return {
        "response": result.response,
        "session_id": session_id,
        "agent_run_id": result.run_id,
        "tokens_used": result.llm_tokens_used,
        "cost_usd": result.llm_cost_usd,
    }


@app.get("/session/context")
async def get_session_context(session_id: str, request: Request) -> dict[str, Any]:
    kernel = request.app.state.kernel
    ctx = await kernel.session_manager.get_context(session_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"active_tasks_count": len(ctx.active_tasks), "message_count": len(ctx.messages)}


@app.get("/health")
async def health_check(request: Request) -> Any:
    kernel = request.app.state.kernel
    if not kernel:
        return JSONResponse(
            status_code=503, content={"status": "degraded", "error": "Kernel not initialized"}
        )

    agents = kernel.agent_runtime.list_agents() if kernel.agent_runtime else []
    tools = [t.name for t in kernel.tool_registry.list()] if kernel.tool_registry else []

    # Check Redis ping
    try:
        import redis.asyncio as aioredis

        # Ignore justified per ADR-011 Section 3.3: redis-py's asyncio
        # from_url has no type annotations in the pinned version.
        redis_client = aioredis.from_url(kernel.config.redis.url)  # type: ignore[no-untyped-call]
        await redis_client.ping()
        await redis_client.aclose()
    except Exception as e:
        return JSONResponse(
            status_code=503, content={"status": "degraded", "error": f"Redis ping failed: {e}"}
        )

    return {"status": "healthy", "agents": agents, "tools": tools}
