from langchain_core.messages import SystemMessage
from app.agents.state import AgentState
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import load_skill, get_active_tools

async def tool_agent_node(state: AgentState):
    """Nœud utilisé si le routeur décide d'utiliser des outils."""
    messages = state.get("messages", [])
    active_tools = await get_active_tools()
    
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        temperature=0
    ).bind_tools(active_tools)
    
    yield {
        "thoughts": ["**Planification :** Je vais utiliser les outils à ma disposition pour récupérer les informations demandées."],
        "detail": "Planification de l'exécution des outils...",
        "steps": ["tool_agent_planned"]
    }

    try:
        response = await llm.ainvoke([SystemMessage(content=load_skill("tool_expert"))] + messages)
    except Exception as e:
        print(f"⚠️ Erreur critique du LLM (Tool Parser) : {e}", flush=True)
        from langchain_core.messages import AIMessage
        response = AIMessage(
            content=f"Désolé, j'ai tenté d'utiliser un outil mais j'ai généré une requête mal formatée qui a été rejetée par le système ({str(e)[:50]}). Je ne peux pas exécuter cette action pour le moment."
        )
        
    yield {"messages": [response], "steps": ["tool_agent_execution"]}
