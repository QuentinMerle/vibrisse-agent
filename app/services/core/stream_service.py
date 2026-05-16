import json
from typing import Any, Dict, Optional
from app.core.constants import NODE_STATUS_MAP

async def format_event(event: Dict[str, Any], thread_id: str) -> str:
    """Helper pour formater les événements du flux SSE."""
    kind = event["event"]
    payload = {"thread_id": thread_id}
    
    if kind == "on_chain_start":
        node = event.get("metadata", {}).get("langgraph_node") or event.get("metadata", {}).get("node") or event.get("name")
        
        # On cherche une correspondance insensible à la casse, en ignorant le nœud racine "LangGraph"
        if node and node != "LangGraph":
            node_key = str(node).lower()
            matching_key = next((k for k in NODE_STATUS_MAP if k.lower() == node_key), None)
            
            if matching_key:
                payload["status"] = "thinking"
                payload["steps"] = [NODE_STATUS_MAP[matching_key]]
                return f"data: {json.dumps(payload)}\n\n"
            
    elif kind in ["on_chat_model_stream", "on_llm_stream"]:
        # Sécurité : On ne streame les tokens QUE pour les nœuds de génération finale
        node = event.get("metadata", {}).get("langgraph_node")
        if node not in ["generate_answer", "expert_review_node", "finalize_answer"]:
            return ""

        data = event.get("data", {})
        chunk = data.get("chunk") or data.get("output")
        if not chunk: return ""
        
        # Si c'est du texte brut (provenant du LLM)
        content = ""
        if hasattr(chunk, "content"): content = chunk.content
        elif isinstance(chunk, dict) and "content" in chunk: content = chunk["content"]
        elif isinstance(chunk, str): content = chunk
        
        if content and isinstance(content, str):
            payload["chunk"] = content
            return f"data: {json.dumps(payload)}\n\n"

    elif kind in ["on_node_stream", "on_chain_stream"]:
        data = event.get("data", {})
        chunk = data.get("chunk") or data.get("output")
        if not chunk or not isinstance(chunk, dict): return ""
        
        # LangGraph wrappe l'output dans une clé portant le nom du nœud
        target_dict = chunk
        if len(chunk) == 1 and isinstance(list(chunk.values())[0], dict):
            target_dict = list(chunk.values())[0]

        if "detail" in target_dict:
            payload["detail"] = target_dict["detail"]
        if "status" in target_dict:
            payload["status"] = target_dict["status"]
        if "steps" in target_dict:
            payload["steps"] = target_dict["steps"]
        if "thoughts" in target_dict:
            payload["thoughts"] = target_dict["thoughts"]
        if "graph_nodes" in target_dict:
            payload["graph_nodes"] = target_dict["graph_nodes"]
        if "graph_edges" in target_dict:
            payload["graph_edges"] = target_dict["graph_edges"]
        if "offload_proposal" in target_dict:
            payload["offload_proposal"] = target_dict["offload_proposal"]
        
        # On ne continue que si on a quelque chose à envoyer (statut/pensée/graphe)
        if any(k in payload for k in ["detail", "status", "steps", "thoughts", "graph_nodes", "graph_edges", "offload_proposal"]):
            return f"data: {json.dumps(payload)}\n\n"

    elif kind == "on_chain_end":
        node = event.get("metadata", {}).get("langgraph_node") or event.get("metadata", {}).get("node") or event.get("name")
        
        # Badges de statut
        if node:
            node_key = str(node).lower()
            matching_key = next((k for k in NODE_STATUS_MAP if k.lower() == node_key), None)
            
            if matching_key:
                payload["steps"] = [NODE_STATUS_MAP[matching_key]]
                payload["status"] = "completed"

        # On n'envoie le texte final que si on n'a pas déjà streamé (sécurité anti-doublon)
        if node in ["generate_answer", "expert_review_node", "finalize_answer"]:
            data = event.get("data", {})
            output = data.get("output")
            if isinstance(output, dict) and "messages" in output:
                last_msg = output["messages"][-1]
                content = getattr(last_msg, "content", "") or (last_msg.get("content") if isinstance(last_msg, dict) else "")
                if content and isinstance(content, str):
                    payload["final_content"] = content
                if hasattr(last_msg, "additional_kwargs") and "thoughts_history" in last_msg.additional_kwargs:
                    payload["thoughts_history"] = last_msg.additional_kwargs["thoughts_history"]
            
        # Tool calls finaux
        data = event.get("data", {})
        output = data.get("output")
        
        # Extraction des détails de réflexion pour l'UX
        if isinstance(output, dict):
            # Priorité aux champs de réflexion connus
            detail = output.get("vision_description") or output.get("reasoning")
            if detail:
                payload["detail"] = detail[:300] + "..." if len(detail) > 300 else detail
                
            if "context_usage" in output:
                payload["context_usage"] = output["context_usage"]
            
            if "context" in output:
                payload["context"] = output["context"]
                
        if isinstance(output, dict) and "messages" in output:
            last_msg = output["messages"][-1]
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                payload["tool_calls"] = last_msg.tool_calls
                
        if "steps" in payload or "final_content" in payload or "tool_calls" in payload or "context_usage" in payload or "detail" in payload or "context" in payload:
            return f"data: {json.dumps(payload)}\n\n"
    
    return ""
