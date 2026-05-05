from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import load_skill, calculate_context_usage

async def vision_node(state: AgentState):
    image_b64 = state.get("image")
    if not image_b64:
        yield {"vision_description": "Aucune image n'a été fournie pour l'analyse.", "steps": ["vision_skipped"]}
        return
    
    question = state.get("question", "Décris cette image en détail.")
    model = state.get("selected_model")
    
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=model,
        api_key=state.get("llm_api_key")
    )
    
    skill_vision = load_skill("vision_analyst")
    prompt = [
        SystemMessage(content=skill_vision),
        HumanMessage(content=[
            {"type": "text", "text": question},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
        ])
    ]
    
    try:
        print(f"--- 👁️ VISION : Analyse en cours avec {model} ---", flush=True)
        yield {"detail": "Analyse visuelle de l'image (composition, style, composants)...", "steps": ["vision_analysis_started"]}
        
        response = await llm.ainvoke(prompt)
        print(f"--- 👁️ VISION : Résultat : {response.content[:100]}...", flush=True)
        new_state = {"vision_description": response.content, "steps": ["vision_analysis"]}
        # Calcul de l'usage mis à jour
        temp_state = state.copy()
        temp_state.update(new_state)
        new_state["context_usage"] = calculate_context_usage(temp_state)
        new_state["detail"] = "Vision : Analyse terminée."
        new_state["thoughts"] = [f"**Analyse Visuelle :** {response.content}"]
        yield new_state
    except Exception as e:
        print(f"⚠️ Vision Error: {e}")
        yield {"vision_description": f"Erreur technique lors de l'analyse d'image : {str(e)}", "steps": ["vision_error"]}
