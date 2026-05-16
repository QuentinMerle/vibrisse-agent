from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState, RouteQuery
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import load_skill, create_node, create_edge
from app.services.core.sovereign_service import SovereignService
import re
import json

async def router_node(state: AgentState):
    question = state.get("question", "").lower()
    vision_desc = state.get("vision_description")
    
    # 1. Sovereign Routing (Smart Offloading) Sentinel
    provider = state.get("llm_provider", "ollama")
    offload_analysis = {"can_offload": False}
    if state.get("sovereign_routing", True):
        offload_analysis = SovereignService.analyze_offload_opportunity(
            query=question,
            provider=provider,
            model=state.get("selected_model")
        )
        print(f"⚖️ Sovereign Analysis: {offload_analysis}", flush=True)
    
    if offload_analysis["can_offload"] and not state.get("offload_proposal"):
        # On injecte la proposition dans l'état pour que l'UI puisse l'afficher
        yield {
            "offload_proposal": offload_analysis,
            "thoughts": [
                "__RESET__", 
                f"**Sovereign Hint:** {offload_analysis['reason']}. This could be handled locally to save tokens."
            ],
            "detail": "Sovereign Routing proposal active. Waiting for user choice...",
            "decision": "wait_for_offload_choice" # Indicateur pour le graphe
        }
        return

    # 2. Heuristics (Only for OBVIOUS technical triggers to assist small models)
    tech_triggers = [
        "list", "ls", "lister", "read", "cat", "lire", "explore", "explorer", "search", "chercher", "trouver", "find",
        "weather", "météo", "actualités", "news", "save", "sauvegarde", "enregistre", "écris", "write",
        "ajoute", "add", "souvenir", "memory", "mcp", "outil"
    ]
    if question.startswith("/") or any(k in question for k in tech_triggers):
        yield {
            "decision": "web_and_tools", 
            "active_worker": "coder",
            "steps": ["router: technical fast-track"],
            "thoughts": ["__RESET__", "**Intent:** Technical command detected. Routing to Coder Expert with tool access."],
            "graph_nodes": [
                create_node("supervisor", "Supervisor", "SUPERVISOR", "🧠"),
                create_node("worker", "Coder", "WORKER", "👷")
            ],
            "graph_edges": [create_edge("supervisor", "worker")]
        }
        return

    # 3. Appel LLM pour une décision sémantique fine
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        custom_url=state.get("llm_custom_url"),
        temperature=0,
        role="supervisor"
    )
    
    skill_prompt = load_skill("orchestrator")
    
    try:
        # Inform user about intent analysis
        yield {"detail": "Analyzing intent and choosing technical strategy...", "steps": ["router_started"]}
        
        # On récupère l'historique pour donner du contexte au Supervisor
        messages = state.get("messages", [])
        history_context = ""
        if len(messages) > 1:
            # On prend les 4 derniers messages pour avoir du contexte sans exploser les tokens
            history_context = "\n--- CONTEXTE PRÉCÉDENT ---\n"
            for m in messages[-4:]:
                role = "USER" if isinstance(m, HumanMessage) else "AGENT"
                content = m.content if isinstance(m.content, str) else "Image/Multi-modal content"
                history_context += f"{role}: {content[:200]}...\n"

        content = f"{history_context}\nCURRENT QUESTION: {question}"
        if vision_desc:
            content = f"VISUAL ANALYSIS OF CURRENT IMAGE: {vision_desc}\n\n{history_context}\nCURRENT QUESTION: {question}"

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
            "thoughts": ["__RESET__", f"**Intent:** {reasoning} (Expert: {worker})"],
            "graph_nodes": [
                create_node("supervisor", "Supervisor", "SUPERVISOR", "🧠"),
                create_node("worker", worker.capitalize(), "WORKER", "👷")
            ],
            "graph_edges": [create_edge("supervisor", "worker")]
        }
        return
        
    except Exception as e:
        print(f"⚠️ Router failed: {e}. Defaulting to direct response.", flush=True)
        yield {"decision": "direct_response", "steps": ["router: error fallback"]}
        return
