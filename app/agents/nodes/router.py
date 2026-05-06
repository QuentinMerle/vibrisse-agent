from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState, RouteQuery
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import load_skill

async def router_node(state: AgentState):
    question = state.get("question", "").lower()
    vision_desc = state.get("vision_description")
    
    # 2. Heuristics (Only for OBVIOUS triggers)
    if question.startswith("/") or any(k in question for k in ["weather", "météo", "actualités", "news", "save", "sauvegarde", "enregistre", "écris", "write"]):
        yield {
            "decision": "web_and_tools", 
            "steps": ["router: fast-track tools"],
            "thoughts": ["__RESET__", "**Intent:** Priority fast-track to system tools triggered by keywords."]
        }
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
        # Inform user about intent analysis
        yield {"detail": "Analyzing intent and choosing technical strategy...", "steps": ["router_started"]}
        
        content = f"QUESTION: {question}"
        if vision_desc:
            content = f"VISUAL ANALYSIS: {vision_desc}\n\nUSER QUESTION: {question}"

        # We request raw text with a strict format to avoid JSON hallucination on small models
        response = await llm.ainvoke([
            SystemMessage(content=skill_prompt + "\n\nIMPORTANT: RESPOND ONLY IN JSON FORMAT. NO TEXT BEFORE OR AFTER."),
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
                reasoning = data.get("reasoning", "Semantic analysis")
            except:
                raise ValueError("JSON mal formé")
        else:
            # Tentative 2 : Fallback texte direct si le modèle n'a pas mis d'accolades
            if "web_and_tools" in text.lower(): datasource = "web_and_tools"
            elif "vectorstore" in text.lower(): datasource = "vectorstore"
            else: datasource = "direct_response"
            reasoning = "Keyword extraction"

        # Validation du datasource pour éviter de casser le graphe LangGraph
        ALLOWED_DATASOURCES = ["vectorstore", "direct_response", "web_and_tools"]
        if datasource not in ALLOWED_DATASOURCES:
            print(f"⚠️ Router hallucination: '{datasource}' is not allowed. Falling back to direct_response.", flush=True)
            datasource = "direct_response"

        yield {
            "decision": datasource, 
            "steps": [f"router: {datasource}"],
            "thoughts": ["__RESET__", f"**Intent:** {reasoning}"]
        }
        return
        
    except Exception as e:
        print(f"⚠️ Router failed: {e}. Defaulting to direct response.", flush=True)
        yield {"decision": "direct_response", "steps": ["router: error fallback"]}
        return
