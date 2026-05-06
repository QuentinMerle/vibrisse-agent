from langchain_core.messages import SystemMessage
from app.agents.state import AgentState
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import load_skill, get_active_tools, clean_mentions

async def tool_agent_node(state: AgentState):
    """Nœud utilisé si le routeur décide d'utiliser des outils."""
    messages = state.get("messages", [])
    active_tools = await get_active_tools()
    
    # On nettoie les messages pour le LLM (mentions @[display](id) -> @display)
    cleaned_messages = []
    for m in messages:
        if hasattr(m, "content") and isinstance(m.content, str):
            msg_copy = m.copy(update={"content": clean_mentions(m.content)})
            cleaned_messages.append(msg_copy)
        else:
            cleaned_messages.append(m)

    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        temperature=0
    ).bind_tools(active_tools)
    
    yield {
        "thoughts": ["**Planning:** I will use the available tools to retrieve the requested information."],
        "detail": "Planning tool execution...",
        "steps": ["tool_agent_planned"]
    }
    
    try:
        response = await llm.ainvoke([SystemMessage(content=load_skill("tool_expert"))] + cleaned_messages)
    except Exception as e:
        print(f"⚠️ Erreur critique du LLM (Tool Parser) : {e}", flush=True)
        from langchain_core.messages import AIMessage
        response = AIMessage(
            content=f"Désolé, j'ai tenté d'utiliser un outil mais j'ai généré une requête mal formatée qui a été rejetée par le système ({str(e)[:50]}). Je ne peux pas exécuter cette action pour le moment."
        )
        
    yield {"messages": [response], "steps": ["tool_agent_execution"]}
