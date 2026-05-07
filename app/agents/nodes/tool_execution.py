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

    worker = state.get("active_worker", "coder") # Fallback coder for tools
    
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        temperature=0,
        role=worker
    )
    
    yield {
        "thoughts": ["**Planning:** I will use the available tools to retrieve the requested information."],
        "detail": "Planning tool execution...",
        "steps": ["tool_agent_planned"]
    }
    
    try:
        # 1. Tentative avec outils natifs
        llm_with_tools = llm.bind_tools(active_tools)
        
        # Injection d'un rappel spécifique pour Groq (souvent trop bavard au lieu d'appeler l'outil)
        final_skill = load_skill("tool_expert")
        if state.get("llm_provider") == "groq":
            final_skill += "\n\nCRITICAL: You are currently using your NATIVE TOOL API. You MUST return a tool_call and NOTHING ELSE. No conversational text."
            
        response = await llm_with_tools.ainvoke([SystemMessage(content=final_skill)] + cleaned_messages)
    except Exception as e:
        error_str = str(e).lower()
        if "does not support tools" in error_str or "400" in error_str:
            print(f"🔄 Fallback : Modèle incompatible avec l'API d'outils natifs. Utilisation du parsing texte...", flush=True)
            # 2. Fallback : On demande au modèle d'écrire ses outils en format texte
            fallback_skill = load_skill("tool_expert") + "\n\nCRITICAL: Native tool API is disabled for your model. You MUST call tools using this EXACT format: tool_name(arg1='val1', ...)"
            response = await llm.ainvoke([SystemMessage(content=fallback_skill)] + cleaned_messages)
            
            # 3. Tentative de parsing manuel des tool_calls dans le texte
            import re
            import json
            tool_calls = []
            # On cherche des patterns comme list_dir(path='.')
            for tool in active_tools:
                pattern = rf"{tool.name}\((.*?)\)"
                matches = re.finditer(pattern, response.content)
                for match in matches:
                    args_str = match.group(1)
                    # Parsing rudimentaire des arguments
                    try:
                        # On tente de transformer arg='val' en {"arg": "val"}
                        args = {}
                        for arg_match in re.finditer(r"(\w+)\s*=\s*['\"](.*?)['\"]", args_str):
                            args[arg_match.group(1)] = arg_match.group(2)
                        
                        tool_calls.append({
                            "name": tool.name,
                            "args": args,
                            "id": f"call_{tool.name}_{len(tool_calls)}"
                        })
                    except: continue
            
            if tool_calls:
                response.tool_calls = tool_calls
        else:
            print(f"⚠️ Erreur critique du LLM (Tool Parser) : {e}", flush=True)
            from langchain_core.messages import AIMessage
            response = AIMessage(
                content=f"Désolé, j'ai tenté d'utiliser un outil mais j'ai généré une requête mal formatée qui a été rejetée par le système ({str(e)[:50]})."
            )
        
    yield {"messages": [response], "steps": ["tool_agent_execution"]}
