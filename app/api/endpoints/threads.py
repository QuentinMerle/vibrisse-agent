import logging
from fastapi import APIRouter, Request
from langchain_core.messages import HumanMessage
from app.agents.nodes import calculate_context_usage

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def list_threads(request: Request):
    """Liste les conversations stockées dans le checkpointer avec des titres lisibles."""
    thread_data = []
    seen_ids = set()
    try:
        saver = request.app.state.saver
        
        # On récupère les checkpoints (Async pour SQLite, Sync pour Memory)
        checkpoints = []
        if hasattr(saver, "alist"):
            async for cp in saver.alist(None, limit=100):
                checkpoints.append(cp)
        else:
            for cp in saver.list(None, limit=100):
                checkpoints.append(cp)

        for checkpoint in checkpoints:
            try:
                if not checkpoint.config or "configurable" not in checkpoint.config:
                    continue
                    
                tid = checkpoint.config["configurable"]["thread_id"]
                if tid not in seen_ids:
                    seen_ids.add(tid)
                    
                    title = f"Session {tid}"
                    values = checkpoint.checkpoint.get("channel_values", {})
                    messages = values.get("messages", [])
                    
                    if messages:
                        # On essaie de trouver le premier message de l'HUMAIN pour le titre
                        for msg in messages:
                            content = ""
                            if hasattr(msg, "content"): content = msg.content
                            elif isinstance(msg, dict): content = msg.get("content", "")
                            
                            if content and isinstance(content, str) and len(content.strip()) > 0:
                                title = (content[:35] + '...') if len(content) > 35 else content
                                break # On a trouvé notre titre

                    thread_data.append({
                        "id": tid, 
                        "title": title, 
                        "updated_at": checkpoint.metadata.get("ts", "")
                    })
            except Exception:
                continue
    except Exception as e:
        logger.error(f"Critical error in list_threads: {e}")
        return {"threads": []}
        
    return {"threads": thread_data}

@router.get("/{thread_id}")
async def get_thread_history(request: Request, thread_id: str):
    """Récupère l'historique complet d'une conversation."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = await request.app.state.agent.aget_state(config)
        
        values = state.values or {}
        messages = values.get("messages", [])
        usage = calculate_context_usage(values)
        
        from langchain_core.messages import ToolMessage
        
        history = []
        for msg in messages:
            # On ignore les réponses des outils (succès ou erreurs)
            if isinstance(msg, ToolMessage) or (isinstance(msg, dict) and msg.get("type") == "tool"):
                continue
                
            role = "user" if isinstance(msg, HumanMessage) or (isinstance(msg, dict) and msg.get("type") == "human") else "agent"
            content = getattr(msg, "content", "") or (msg.get("content") if isinstance(msg, dict) else "")
            
            # Extraction des métadonnées
            thoughts = []
            tool_calls = []
            if hasattr(msg, "additional_kwargs"):
                thoughts = msg.additional_kwargs.get("thoughts_history", [])
                tool_calls = msg.additional_kwargs.get("tool_calls", [])
            elif isinstance(msg, dict) and "additional_kwargs" in msg:
                thoughts = msg["additional_kwargs"].get("thoughts_history", [])
                tool_calls = msg["additional_kwargs"].get("tool_calls", [])

            if role == "agent" and history and history[-1]["role"] == "agent":
                # Fusion avec le message précédent si c'est aussi l'agent
                prev = history[-1]
                if content and content != prev["content"]:
                    prev["content"] = (prev["content"] + "\n\n" + content).strip()
                if thoughts:
                    prev_thoughts = prev.get("thoughts_history", [])
                    prev["thoughts_history"] = list(dict.fromkeys(prev_thoughts + thoughts))
                if tool_calls:
                    prev_tool_calls = prev.get("tool_calls", [])
                    prev["tool_calls"] = prev_tool_calls + tool_calls
            else:
                history.append({
                    "role": role, 
                    "content": content,
                    "thoughts_history": thoughts,
                    "tool_calls": tool_calls
                })
                
        return {"messages": history, "context_usage": usage}
    except Exception as e:
        logger.error(f"Error in get_thread_history: {e}")
        return {"messages": [], "context_usage": 0}
