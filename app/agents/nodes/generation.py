import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agents.state import AgentState
from app.core.config import settings
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import extract_thought, clean_mentions, load_skill

async def generate_answer(state: AgentState):
    context = state.get("context", "")
    messages = state.get("messages", [])
    vision_desc = state.get("vision_description")
    
    # On nettoie les messages pour le LLM (mentions @[display](id) -> @display)
    cleaned_messages = []
    for m in messages:
        if hasattr(m, "content") and isinstance(m.content, str):
            # On crée une copie du message avec le contenu nettoyé via .copy()
            msg_copy = m.copy(update={"content": clean_mentions(m.content)})
            cleaned_messages.append(msg_copy)
        else:
            cleaned_messages.append(m)

    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key")
    )
    
    # Building the precision prompt
    vision_context = f"\n--- IMAGE VISUAL ANALYSIS ---\n{vision_desc}\n" if vision_desc else ""
    rag_context = f"\n--- PROJECT CONTEXT (SOURCE OF TRUTH) ---\n{context}\n" if context else ""
    
    # Getting project profile (Manifest generated on ingestion)
    project_profile = settings.get_project_profile()
    
    instruction = f"""You are the Senior Technical Expert of Vibrisse.
Your mission is to answer the user's question with precision and professionalism.

CRITICAL: You must respond in the SAME LANGUAGE as the user's last message. 
If the user speaks English, respond in English. If the user speaks French, respond in French.

AVAILABLE SOURCES:
1. VISUAL ANALYSIS: {vision_desc if vision_desc else "No image provided."}
2. PROJECT CONTEXT (RAG): {context if context else "No relevant source files found in code."}
3. TOOLS & WEB: If 'tool' type messages are present in history, use them as the source of truth for real-time or external data.

--- ANALYZED PROJECT PROFILE ---
{project_profile}

CRITICAL RULES:
- Priority to sources: Use the sources above to answer. If info comes from web search, synthesize it.
- Technical Fidelity: If the question concerns code, strictly adopt the stack and conventions described in the PROJECT PROFILE.
- Versatile Expertise: While your expertise is technical, you must answer general questions (weather, news) if and only if research tools provided the data.
- ALWAYS START with a <thought> tag to detail your technical reasoning or synthesis strategy in English.
"""

    # Source analysis for initial thought
    source_info = "general knowledge"
    if context:
        source_info = "project context"
    elif vision_desc:
        source_info = "visual analysis"
    
    # On ne considère les outils que s'ils sont récents dans l'historique ou si c'est la raison de la réponse
    recent_messages = messages[-3:] if len(messages) >= 3 else messages
    if any(msg.type == 'tool' or (isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls) for msg in recent_messages):
        source_info = "web search/tool results"
    
    yield {
        "thoughts": [f"**Drafting:** Synthesizing a response based on {source_info}."],
        "detail": "Drafting final response...",
        "steps": ["generation_started"]
    }

    full_message = ""
    # On utilise cleaned_messages au lieu de messages
    async for chunk in llm.astream([SystemMessage(content=instruction)] + cleaned_messages):
        content = chunk.content if hasattr(chunk, "content") else str(chunk)
        full_message += content
        yield chunk
    
    # Sécurité : Si le stream est resté vide, on tente une invocation directe
    if not full_message.strip():
        print("⚠️ Stream vide détecté, tentative de fallback ainvoke...", flush=True)
        fallback_resp = await llm.ainvoke([SystemMessage(content=instruction)] + messages)
        full_message = fallback_resp.content
        # On n'émet pas de chunk ici car le stream est fini, mais on remplit 'generation'
    
    # Store final result in 'generation' for final synthesis
    thought = extract_thought(full_message)
    yield {
        "generation": full_message, 
        "steps": ["generation_complete"],
        "thoughts": [f"**Analysis:** {thought}"] if thought else ["**Analysis:** Response generated and structured."]
    }

async def finalize_answer(state: AgentState):
    """Transforme la génération finale en un message structuré pour l'historique."""
    content = state.get("generation", "")
    thoughts = state.get("thoughts", [])
    print(f"--- 🏁 FINALIZE : Synthèse de {len(thoughts)} pensées ---", flush=True)
    
    # Extraction propre du contenu textuel
    if hasattr(content, "content"):
        content = content.content
    elif isinstance(content, dict) and "content" in content:
        content = content["content"]
        
    if not content:
        content = "Sorry, I could not generate a response."
    
    # Nettoyage final des balises résiduelles dans le corps du message
    clean_content = content
    patterns = [r"<thought>.*?</thought>", r"<think>.*?</think>", r"<thinking>.*?</thinking>"]
    for p in patterns:
        clean_content = re.sub(p, "", clean_content, flags=re.DOTALL | re.IGNORECASE).strip()
        
    if not clean_content:
        # Fallback si le modèle a absolument tout écrit à l'intérieur de ses balises de pensée
        clean_content = "✅ Operation complete. (Technical details in logs)"
        
    # Construction d'une chronologie de pensée élégante et structurée
    # On filtre les doublons ou pensées vides
    unique_thoughts = []
    for t in thoughts:
        if t and t not in unique_thoughts:
            unique_thoughts.append(t)
            
    # On transmet la chronologie via les métadonnées, pas dans le texte
    final_message = AIMessage(
        content=clean_content,
        additional_kwargs={
            "thoughts_history": unique_thoughts,
            "context": state.get("context", "")
        }
    )
    
    return {"messages": [final_message], "steps": ["final_response"]}

async def expert_review_node(state: AgentState):
    """Vérifie la réponse (brouillon) et l'améliore si nécessaire."""
    draft_answer = state.get("generation", "")
    if not draft_answer:
        yield {"steps": ["expert_review_skipped"]}
        return
    
    messages = state.get("messages", [])
    
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        temperature=0.1
    )
    
    expert_prompt = """You are the Quality Control Engineer of Vibrisse.
Your mission: Return ONLY the CODE and technical explanations, as if you were the first to speak.

FORMAL PROHIBITIONS (CRITICAL ERROR OTHERWISE):
- NEVER refer to "the previous proposal" or "the draft".
- NEVER start with "Absolutely", "Here is", "The proposal", etc.
- Produce ONLY the useful final content (Title, Explanation, Code).
- You MUST include a <thought> tag at the beginning for your reasoning.
"""
    
    print(f"--- 🛡️ EXPERT: Review in progress ---", flush=True)
    # Inform user about expert review
    yield {"detail": "Critical analysis and technical optimization of the response...", "steps": ["expert_review_started"]}
    
    response = await llm.ainvoke([SystemMessage(content=expert_prompt)] + messages + [HumanMessage(content=f"Draft to review:\n{draft_answer}")])
    
    # L'expert ne doit pas polluer la réponse avec du meta-talk
    thought = extract_thought(response.content)
    # On nettoie la réponse de l'expert pour ne garder que le contenu utile
    clean_expert_content = response.content
    for p in [r"<thought>.*?</thought>", r"<think>.*?</think>", r"<thinking>.*?</thinking>"]:
        clean_expert_content = re.sub(p, "", clean_expert_content, flags=re.DOTALL | re.IGNORECASE).strip()

    yield {
        "generation": clean_expert_content, 
        "steps": ["expert_review_passed"], 
        "detail": "Technical optimization completed.",
        "thoughts": [f"**Expert Optimization:** {thought}"] if thought else ["**Expert Optimization:** Response validated and optimized for the technical stack."]
    }
