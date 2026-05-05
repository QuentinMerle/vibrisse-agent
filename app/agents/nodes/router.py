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
        
        content = f"QUESTION : {question}"
        if vision_desc:
            content = f"ANALYSE VISUELLE : {vision_desc}\n\nQUESTION DE L'UTILISATEUR : {question}"

        # On demande du texte brut avec un format strict pour éviter les délires du JSON natif sur petits modèles
        response = await llm.ainvoke([
            SystemMessage(content=skill_prompt + "\n\nIMPORTANT: RÉPONDS UNIQUEMENT AU FORMAT JSON. PAS DE TEXTE AVANT OU APRÈS."),
            HumanMessage(content=content)
        ])
        
        # Extraction robuste du JSON (même s'il y a du texte autour ou s'il est tronqué)
        text = response.content
        import json
        import re
        
        # Tentative 1 : Regex pour trouver un bloc JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                datasource = data.get("datasource", "direct_response")
                reasoning = data.get("reasoning", "Analyse sémantique")
            except:
                raise ValueError("JSON mal formé")
        else:
            # Tentative 2 : Fallback texte direct si le modèle n'a pas mis d'accolades
            if "web_and_tools" in text.lower(): datasource = "web_and_tools"
            elif "vectorstore" in text.lower(): datasource = "vectorstore"
            else: datasource = "direct_response"
            reasoning = "Extraction par mots-clés"

        yield {
            "decision": datasource, 
            "steps": [f"router: {datasource}"],
            "thoughts": [f"**Intention :** {reasoning}"]
        }
        return
        
    except Exception as e:
        print(f"⚠️ Router failed: {e}. Defaulting to direct response.", flush=True)
        yield {"decision": "direct_response", "steps": ["router: error fallback"]}
        return
