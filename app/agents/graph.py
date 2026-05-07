import os
from pathlib import Path
from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.nodes import (
    router_node, retrieve_code, generate_answer, 
    tool_agent_node, get_active_tools, expert_review_node, vision_node,
    finalize_answer
)
from app.agents.tools import run_terminal_command
from app.core.config import settings
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import ToolMessage

# --- Nœuds d'exécution des outils dynamiques ---

async def call_safe_tools(state: AgentState):
    """Exécute les outils 'sûrs' (Web, MCP, etc.) de manière dynamique."""
    messages = state.get("messages", [])
    last_message = messages[-1]
    
    # On récupère la liste complète et à jour des outils (incluant le MCP)
    all_tools = await get_active_tools()
    tool_map = {t.name: t for t in all_tools}
    
    responses = []
    tool_results_summary = []
    
    for tool_call in last_message.tool_calls:
        tool = tool_map.get(tool_call["name"])
        if tool:
            print(f"🛠️ Exécution de l'outil : {tool_call['name']}", flush=True)
            result = await tool.ainvoke(tool_call["args"])
            
            # Synthèse pour la ThinkingConsole
            res_str = str(result)
            summary = f"Résultat de {tool_call['name']} : " + (res_str[:150] + "..." if len(res_str) > 150 else res_str)
            tool_results_summary.append(summary)
            
            responses.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=res_str
            ))
        else:
            responses.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=f"Erreur : L'outil '{tool_call['name']}' est introuvable."
            ))
            
    return {
        "messages": responses, 
        "thoughts": [f"**Action Outil :** {s}" for s in tool_results_summary],
        "detail": "Résultats des outils récupérés."
    }

async def call_sensitive_tools(state: AgentState):
    """Exécute les outils sensibles (terminal, écriture)."""
    messages = state.get("messages", [])
    last_message = messages[-1]
    
    from app.agents.tools import run_terminal_command, write_file
    tool_map = {
        "run_terminal_command": run_terminal_command,
        "write_file": write_file
    }
    
    responses = []
    for tool_call in last_message.tool_calls:
        name = tool_call["name"]
        if name in tool_map:
            print(f"⚠️ Exécution SENSITIVE : {name}", flush=True)
            result = await tool_map[name].ainvoke(tool_call["args"])
            responses.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=str(result)
            ))
    return {"messages": responses}

def custom_tools_condition(state: AgentState):
    messages = state.get("messages", [])
    if not messages: return "generate_answer"
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        # Si un des appels concerne le terminal, on va vers le nœud sensitive
        for tc in last_message.tool_calls:
            if tc["name"] in ["run_terminal_command", "write_file"]: 
                return "sensitive_tools"
        return "safe_tools"
    return "generate_answer"

workflow = StateGraph(AgentState)

# 1. Ajout des nœuds
workflow.add_node("router_node", router_node)
workflow.add_node("vision_node", vision_node)
workflow.add_node("retrieve_code", retrieve_code)
workflow.add_node("generate_answer", generate_answer)
workflow.add_node("tool_agent_node", tool_agent_node)
workflow.add_node("expert_review_node", expert_review_node)
workflow.add_node("finalize_answer", finalize_answer)
workflow.add_node("safe_tools", call_safe_tools)
workflow.add_node("sensitive_tools", call_sensitive_tools)

# 2. Définition des liens (Edges)
def initial_routing(state: AgentState):
    if state.get("image"):
        return "vision_node"
    return "router_node"

workflow.set_conditional_entry_point(
    initial_routing,
    {
        "vision_node": "vision_node",
        "router_node": "router_node"
    }
)

workflow.add_edge("vision_node", "router_node")

def router_decision(state: AgentState):
    return state.get("decision", "direct_response")

workflow.add_conditional_edges(
    "router_node",
    router_decision,
    {
        "vectorstore": "retrieve_code",
        "direct_response": "generate_answer",
        "web_and_tools": "tool_agent_node"
    }
)

workflow.add_edge("retrieve_code", "generate_answer")

workflow.add_conditional_edges(
    "tool_agent_node",
    custom_tools_condition,
    {
        "safe_tools": "safe_tools",
        "sensitive_tools": "sensitive_tools",
        "generate_answer": "generate_answer"
    }
)

workflow.add_edge("safe_tools", "tool_agent_node")
workflow.add_edge("sensitive_tools", "tool_agent_node")

# Routage final
workflow.add_edge("generate_answer", "expert_review_node")
workflow.add_edge("expert_review_node", "finalize_answer")
workflow.add_edge("finalize_answer", END)

def get_checkpointer():
    """Utilise AsyncSqliteSaver (maintenant compatible avec aiosqlite 0.21.0)."""
    base_dir = Path(__file__).parent.parent.parent / "data"
    os.makedirs(base_dir, exist_ok=True)
    db_path = str(base_dir / "checkpoints.db")
    return AsyncSqliteSaver.from_conn_string(db_path)