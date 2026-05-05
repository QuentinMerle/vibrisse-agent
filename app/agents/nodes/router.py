from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState, RouteQuery
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import load_skill

async def router_node(state: AgentState):
    question = state.get("question", "").lower()
    vision_desc = state.get("vision_description")
    
    # 2. Heuristiques (Uniquement pour les déclencheurs ÉVIDENTS)
    if question.startswith("/") or any(k in question for k in ["météo", "actualités", "news", "sauvegarde", "enregistre", "écris", "write"]):
        yield {"decision": "web_and_tools", "steps": ["router: fast-track tools"]}
        return

    # 3. Appel LLM pour une décision sémantique fine
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        temperature=0
    )
    
    skill_prompt = load_skill("orchestrator")
    
    try:
        # On informe l'utilisateur qu'on analyse son intention
        yield {"detail": "Analyse de l'intention et choix de la stratégie technique...", "steps": ["router_started"]}
        
        # On tente le routage structuré pour une fiabilité maximale
        structured_llm = llm.with_structured_output(RouteQuery)
        
        content = f"QUESTION : {question}"
        if vision_desc:
            content = f"ANALYSE VISUELLE : {vision_desc}\n\nQUESTION DE L'UTILISATEUR : {question}"

        result = await structured_llm.ainvoke([
            SystemMessage(content=skill_prompt),
            HumanMessage(content=content)
        ])
        
        yield {
            "decision": result.datasource, 
            "steps": [f"router: {result.datasource}"],
            "thoughts": [f"**Intention :** {result.reasoning}"]
        }
        return
    except Exception as e:
        print(f"⚠️ Router Structured Output failed: {e}. Falling back to text parsing.", flush=True)
        # Fallback : Mode texte classique si le modèle ne supporte pas le mode structuré
        response = await llm.ainvoke([
            SystemMessage(content=skill_prompt + "\n\nRÉPONDS PAR UN SEUL MOT : 'vectorstore', 'web_and_tools', ou 'direct_response'."),
            HumanMessage(content=content)
        ])
        decision = response.content.strip().lower()
        if "vectorstore" in decision:
            yield {"decision": "vectorstore", "steps": ["router: technical text"]}
        elif "web_and_tools" in decision:
            yield {"decision": "web_and_tools", "steps": ["router: force tools"]}
        else:
            yield {"decision": "direct_response", "steps": ["router: direct response"]}
        return
