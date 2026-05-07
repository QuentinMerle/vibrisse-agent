from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState, RouteQuery
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import load_skill
import re
import json

async def router_node(state: AgentState):
    question = state.get("question", "").lower()
    vision_desc = state.get("vision_description")
    
    # 2. Heuristics (Only for OBVIOUS technical triggers to assist small models)
    tech_triggers = [
        "list", "ls", "lister", "read", "cat", "lire", "explore", "explorer", "search", "chercher", "trouver", "find",
        "weather", "météo", "actualités", "news", "save", "sauvegarde", "enregistre", "écris", "write"
    ]
    if question.startswith("/") or any(k in question for k in tech_triggers):
        yield {
            "decision": "web_and_tools", 
            "active_worker": "coder",
            "steps": ["router: technical fast-track"],
            "thoughts": ["__RESET__", "**Intent:** Technical command detected. Routing to Coder Expert with tool access."]
        }
        return

    # 3. Appel LLM pour une décision sémantique fine
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        temperature=0,
        role="supervisor"
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
        
        # Tentative 1 : Regex pour trouver un bloc JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        datasource = None
        worker = None
        reasoning = None
        
        if match:
            try:
                data = json.loads(match.group(0))
                datasource = data.get("datasource")
                worker = data.get("worker")
                reasoning = data.get("reasoning")
            except:
                pass # On tente le fallback XML si le JSON est corrompu
        
        # Tentative 1.5 : Regex pour XML (Fallback pour modèles type 7B/8B instables sur JSON)
        if not datasource:
            match_ds = re.search(r'<datasource>(.*?)</datasource>', text, re.IGNORECASE | re.DOTALL)
            match_wk = re.search(r'<worker>(.*?)</worker>', text, re.IGNORECASE | re.DOTALL)
            match_rs = re.search(r'<reasoning>(.*?)</reasoning>', text, re.IGNORECASE | re.DOTALL)
            
            if match_ds: datasource = match_ds.group(1).strip()
            if match_wk: worker = match_wk.group(1).strip()
            if match_rs: reasoning = match_rs.group(1).strip()

        # Tentative 2 : Fallback par mots-clés si tout a échoué
        if not datasource:
            if "web_and_tools" in text.lower(): datasource = "web_and_tools"
            elif "vectorstore" in text.lower(): datasource = "vectorstore"
            else: datasource = "direct_response"
            reasoning = "Keyword fallback"

        if not worker:
            if "coder" in text.lower(): worker = "coder"
            elif "writer" in text.lower(): worker = "writer"
            elif "architect" in text.lower(): worker = "architect"
            else: worker = "general"
        
        if not reasoning: reasoning = "Inferred intent"

        # Validation du datasource pour éviter de casser le graphe LangGraph
        ALLOWED_DATASOURCES = ["vectorstore", "direct_response", "web_and_tools"]
        if datasource not in ALLOWED_DATASOURCES:
            print(f"⚠️ Router hallucination: '{datasource}' is not allowed. Falling back to direct_response.", flush=True)
            datasource = "direct_response"

        yield {
            "decision": datasource, 
            "active_worker": worker,
            "steps": [f"router: {datasource} (worker: {worker})"],
            "thoughts": ["__RESET__", f"**Intent:** {reasoning} (Expert: {worker})"]
        }
        return
        
    except Exception as e:
        print(f"⚠️ Router failed: {e}. Defaulting to direct response.", flush=True)
        yield {"decision": "direct_response", "steps": ["router: error fallback"]}
        return
