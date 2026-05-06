from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import load_skill, calculate_context_usage

async def vision_node(state: AgentState):
    image_b64 = state.get("image")
    if not image_b64:
        yield {"vision_description": "No image was provided for analysis.", "steps": ["vision_skipped"]}
        return
    
    question = state.get("question", "Describe this image in detail.")
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
        print(f"--- 👁️ VISION: Analysis in progress with {model} ---", flush=True)
        yield {"detail": "Visual analysis of image (composition, style, components)...", "steps": ["vision_analysis_started"]}
        
        response = await llm.ainvoke(prompt)
        print(f"--- 👁️ VISION : Résultat : {response.content[:100]}...", flush=True)
        new_state = {"vision_description": response.content, "steps": ["vision_analysis"]}
        # Calcul de l'usage mis à jour
        temp_state = state.copy()
        temp_state.update(new_state)
        new_state["context_usage"] = calculate_context_usage(temp_state)
        new_state["detail"] = "Vision: Analysis completed."
        new_state["thoughts"] = ["__RESET__", f"**Visual Analysis:** {response.content}"]
        yield new_state
    except Exception as e:
        print(f"⚠️ Vision Error: {e}")
        yield {"vision_description": f"Technical error during image analysis: {str(e)}", "steps": ["vision_error"]}
