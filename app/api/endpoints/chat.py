import uuid
import json
import logging
from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.core.stream_service import format_event

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    image: Optional[str] = None
    model: Optional[str] = None

class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool

@router.post("/")
async def chat(request: Request, chat_req: ChatRequest):
    thread_id = chat_req.thread_id or str(uuid.uuid4())[:8]
    agent_app = request.app.state.agent

    # Extraction des configurations LLM depuis les headers
    llm_provider = request.headers.get("X-Vibrisse-Provider", "ollama").lower()
    llm_api_key = request.headers.get("X-Vibrisse-Api-Key")
    llm_model_header = request.headers.get("X-Vibrisse-Model")
    llm_custom_url = request.headers.get("X-Vibrisse-Custom-Url")
    sovereign_routing = request.headers.get("X-Vibrisse-Sovereign-Routing", "true").lower() == "true"
    
    # Résolution finale du modèle : Priorité au Payload (choix manuel) > Header > Default
    final_model = chat_req.model or llm_model_header or settings.LLM_MODEL
    
    async def event_generator():
        print(f"--- 🚀 STARTING STREAM FOR THREAD {thread_id} ---", flush=True)
        print(f"DEBUG: Header Model: {llm_model_header}, Payload Model: {chat_req.model} -> Final: {final_model}", flush=True)
        
        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 50}
        initial_state = {
            "messages": [("user", chat_req.message)], 
            "question": chat_req.message,
            "image": chat_req.image,
            "selected_model": final_model,
            "llm_provider": llm_provider,
            "llm_api_key": llm_api_key,
            "llm_custom_url": llm_custom_url,
            "sovereign_routing": sovereign_routing
        }
        try:
            async for event in agent_app.astream_events(initial_state, config, version="v2"):
                formatted = await format_event(event, thread_id)
                if formatted:
                    yield formatted
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Stream Error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/approve")
async def approve_chat(request: Request, approval_req: ApprovalRequest):
    thread_id = approval_req.thread_id
    agent_app = request.app.state.agent
    config = {"configurable": {"thread_id": thread_id}}
    
    # On récupère l'état actuel pour savoir quoi faire
    state = await agent_app.aget_state(config)
    messages = state.values.get("messages", [])
    last_message = messages[-1] if messages else None
    
    async def event_generator():
        try:
            if approval_req.approved:
                print(f"--- ✅ COMMAND APPROVED FOR THREAD {thread_id} ---", flush=True)
                async for event in agent_app.astream_events(None, config, version="v2"):
                    yield await format_event(event, thread_id)
            else:
                print(f"--- ❌ COMMAND REJECTED FOR THREAD {thread_id} ---", flush=True)
                from langchain_core.messages import ToolMessage
                
                cancellation_messages = []
                if last_message and hasattr(last_message, "tool_calls"):
                    for tool_call in last_message.tool_calls:
                        cancellation_messages.append(
                            ToolMessage(
                                tool_call_id=tool_call["id"],
                                content="Action annulée par l'utilisateur pour des raisons de sécurité."
                            )
                        )
                
                await agent_app.aupdate_state(config, {"messages": cancellation_messages})
                async for event in agent_app.astream_events(None, config, version="v2"):
                    yield await format_event(event, thread_id)
                    
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Approval Stream Error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
