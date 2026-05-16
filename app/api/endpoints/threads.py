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
            graph_nodes = []
            graph_edges = []
            active_worker = "General"

            # On regarde d'abord dans l'état global pour les valeurs les plus récentes
            # (Note: Pour une persistance parfaite par message, il faudrait les stocker dans additional_kwargs)
            if role == "agent":
                graph_nodes = values.get("graph_nodes", [])
                graph_edges = values.get("graph_edges", [])
                active_worker = values.get("active_worker", "General")

            if hasattr(msg, "additional_kwargs"):
                thoughts = msg.additional_kwargs.get("thoughts_history", thoughts)
                tool_calls = msg.additional_kwargs.get("tool_calls", tool_calls)
                # Fallback sur les kwargs si présent
                graph_nodes = msg.additional_kwargs.get("graph_nodes", graph_nodes)
                graph_edges = msg.additional_kwargs.get("graph_edges", graph_edges)
            elif isinstance(msg, dict) and "additional_kwargs" in msg:
                thoughts = msg["additional_kwargs"].get("thoughts_history", thoughts)
                tool_calls = msg["additional_kwargs"].get("tool_calls", tool_calls)
                graph_nodes = msg["additional_kwargs"].get("graph_nodes", graph_nodes)
                graph_edges = msg["additional_kwargs"].get("graph_edges", graph_edges)

            history.append({
                "id": f"msg_{len(history)}",
                "role": role, 
                "content": content,
                "thoughts_history": thoughts,
                "tool_calls": tool_calls,
                "graph_nodes": graph_nodes,
                "graph_edges": graph_edges,
                "active_worker": active_worker,
                "timestamp": state.metadata.get("ts", "") if state.metadata else ""
            })
                
        return {"messages": history, "context_usage": usage}
    except Exception as e:
        logger.error(f"Error in get_thread_history: {e}")
        return {"messages": [], "context_usage": 0}

@router.delete("/{thread_id}")
async def delete_thread(thread_id: str):
    """Supprime une conversation de la base de données."""
    import aiosqlite
    from pathlib import Path
    
    db_path = Path(__file__).parent.parent.parent.parent / "data" / "checkpoints.db"
    
    try:
        async with aiosqlite.connect(db_path) as db:
            # On supprime des deux tables liées au thread
            await db.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
            await db.execute("DELETE FROM writes WHERE thread_id = ?", (thread_id,))
            await db.commit()
            
        logger.info(f"🗑️ Session supprimée : {thread_id}")
        return {"status": "success", "message": f"Session {thread_id} supprimée."}
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du thread {thread_id}: {e}")
        return {"status": "error", "message": str(e)}
