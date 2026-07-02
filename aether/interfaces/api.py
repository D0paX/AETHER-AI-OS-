from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time

from aether.session.models import SessionMode

app = FastAPI(title="Aether Internal API", docs_url=None, redoc_url=None)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )

class MessageRequest(BaseModel):
    session_id: str
    content: str
    mode: str = "text"

@app.post("/conversation/message")
async def conversation_message(req: MessageRequest, request: Request):
    kernel = request.app.state.kernel
    if not kernel:
        raise HTTPException(status_code=500, detail="Kernel not initialized")
        
    # Implementation per spec
    # 1. Get or create session via session_manager
    session_context = await kernel.session_manager.start_session(
        mode=SessionMode.TEXT,
        session_id=req.session_id
    )
    
    # 2. Build AgentContext from session context
    agent_context = session_context.package()
    
    # 3. Create AgentTask from content
    from aether.agents.base import AgentTask
    task = AgentTask(instruction=req.content)
    
    # 4. Execute: agent_runtime.execute("conversation", task, context)
    run_result = await kernel.agent_runtime.execute("conversation", task, agent_context)
    
    # 5. Update session context with new messages (Wait, AgentRuntime might do this or we do it)
    # The prompt says: Update session context with new messages. But memory API tracks messages?
    # Actually the agent runtime interacts with the memory API to store messages usually, 
    # but the session_manager tracks the transcript. 
    # Let's check how message storing works.
    
    return {
        "response": run_result.output,
        "session_id": session_context.session_id,
        "agent_run_id": str(run_result.run_id),
        "tokens_used": run_result.usage.total_tokens if run_result.usage else 0,
        "cost_usd": run_result.usage.cost_usd if run_result.usage else 0.0
    }

@app.get("/session/context")
async def get_session_context(session_id: str, request: Request):
    kernel = request.app.state.kernel
    ctx = await kernel.session_manager.get_context(session_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "active_tasks_count": len(ctx.active_tasks),
        "message_count": len(ctx.transcript)
    }

@app.get("/health")
async def health_check(request: Request):
    kernel = request.app.state.kernel
    if not kernel:
        return JSONResponse(status_code=503, content={"status": "degraded", "error": "Kernel not initialized"})
    
    agents = list(kernel.agent_runtime.agents.keys()) if kernel.agent_runtime else []
    tools = list(kernel.tool_registry.list_tools().keys()) if kernel.tool_registry else []
    
    # Check Redis ping
    try:
        import redis.asyncio as aioredis
        redis_client = aioredis.from_url(kernel.config.redis.url)
        await redis_client.ping()
        await redis_client.aclose()
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "degraded", "error": f"Redis ping failed: {e}"})
        
    return {
        "status": "healthy",
        "agents": agents,
        "tools": tools
    }
