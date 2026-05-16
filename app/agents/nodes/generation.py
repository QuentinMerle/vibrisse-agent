import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agents.state import AgentState
from app.core.config import settings
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import extract_thought, clean_mentions, load_skill, create_node, create_edge

async def generate_answer(state: AgentState):
    context = state.get("context", "")
    messages = state.get("messages", [])
    vision_desc = state.get("vision_description")
    
    print(f"--- 📝 GENERATION: Processing {len(messages)} messages ---", flush=True)
    
    # On nettoie les messages pour le LLM (mentions @[display](id) -> @display)
    cleaned_messages = []
    for m in messages:
        # On vérifie si c'est un objet message LangChain
        if hasattr(m, "content"):
            content = m.content
            if isinstance(content, str):
                # On utilise une approche plus simple pour copier le message
                from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
                new_content = clean_mentions(content)
                if isinstance(m, HumanMessage): cleaned_messages.append(HumanMessage(content=new_content))
                elif isinstance(m, AIMessage): cleaned_messages.append(AIMessage(content=new_content, tool_calls=getattr(m, "tool_calls", [])))
                elif isinstance(m, ToolMessage): cleaned_messages.append(m) # On ne touche pas aux résultats d'outils
                else: cleaned_messages.append(m)
            else:
                cleaned_messages.append(m)
        else:
            # Fallback si c'est un tuple ou autre
            cleaned_messages.append(m)
 
    worker = state.get("active_worker", "general")
    print(f"--- 👷 WORKER: {worker} ---", flush=True)
    
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        custom_url=state.get("llm_custom_url"),
        role=worker
    )
    
    # On charge le skill correspondant au worker
    skill_map = {
        "coder": "code_expert",
        "writer": "technical_writer",
        "architect": "system_architect",
        "general": "code_expert"
    }
    skill_name = skill_map.get(worker, "code_expert")
    base_instruction = load_skill(skill_name)
    
    # Construction du prompt final
    vision_context = f"\n\n[CONTEXTE VISUEL FOURNI PAR LE SYSTÈME]\n{vision_desc}\n(Note: Utilise cette description comme si tu voyais l'image toi-même.)" if vision_desc else ""
    project_profile = settings.get_project_profile()
    
    # Injection AGRESSIVE de la vision dans le dernier message de l'utilisateur
    if vision_desc and cleaned_messages and isinstance(cleaned_messages[-1], HumanMessage):
        last_msg = cleaned_messages[-1]
        cleaned_messages[-1] = HumanMessage(content=last_msg.content + vision_context)
        print("--- 👁️ VISION INJECTED into last HumanMessage ---", flush=True)

    # Extraction explicite des résultats d'outils
    tool_results = []
    for m in messages:
        if m.type == 'tool':
            tool_results.append(f"TOOL RESULT ({getattr(m, 'name', 'unknown')}): {m.content}")
    
    tool_context = "\n".join(tool_results) if tool_results else "No tool results yet."

    instruction = f"""{base_instruction}

CRITICAL: Respond in the user's language (French/English).
SOURCE OF TRUTH:
1. TOOL RESULTS: {tool_context}
2. PROJECT CONTEXT: {context if context else "No context."}
3. PROJECT PROFILE: {project_profile}

ALWAYS START with a <thought> tag for your internal strategy. 
CRITICAL: Close your thought with </thought> before writing your final response.
"""
 
    yield {
        "thoughts": ["**Drafting:** Processing request..."],
        "detail": "Drafting final response...",
        "steps": ["generation_started"],
        "graph_nodes": [create_node("worker", worker.capitalize(), "WORKER", "👷")],
        "graph_edges": [create_edge("supervisor", "worker")]
    }

    full_message = ""
    last_thought = ""
    
    try:
        async for chunk in llm.astream([SystemMessage(content=instruction)] + cleaned_messages):
            content = chunk.content if hasattr(chunk, "content") else str(chunk)
            full_message += content
            
            # Streaming intelligent de la pensée pendant la génération
            current_thought = extract_thought(full_message)
            if current_thought and current_thought != last_thought:
                last_thought = current_thought
                yield {
                    "thoughts": [f"**Thinking:** {current_thought}"],
                    "detail": "Streaming thoughts...",
                    "steps": ["generation_streaming"]
                }
    except Exception as e:
        print(f"⚠️ Generation Error: {e}", flush=True)
    
    if not full_message.strip():
        try:
            resp = await llm.ainvoke([SystemMessage(content=instruction)] + cleaned_messages)
            full_message = resp.content
        except Exception as e:
            print(f"⚠️ Fallback Generation Error: {e}", flush=True)
    

    final_thought = extract_thought(full_message)
    yield {
        "generation": full_message, 
        "steps": ["generation_complete"],
        "thoughts": [f"**Analysis:** {final_thought}"] if final_thought else ["**Analysis:** Response generated."]
    }

async def finalize_answer(state: AgentState):
    """Transforme la génération finale en un message structuré pour l'historique."""
    content = state.get("generation", "")
    thoughts = state.get("thoughts", [])
    
    # Extraction robuste du contenu
    if not content and state.get("messages"):
        # Si generation est vide, on tente de récupérer le dernier message de l'assistant
        last_msg = state["messages"][-1]
        if hasattr(last_msg, "content"):
            content = last_msg.content
            
    if hasattr(content, "content"):
        content = content.content
        
    if not content or str(content).strip() == "":
        print("⚠️ Warning: finalize_answer received empty content, using fallback message.", flush=True)
        content = "✅ Opération terminée avec succès."
    
    # Nettoyage des balises de pensée
    clean_content = str(content)
    patterns = [r"<thought>.*?</thought>", r"<think>.*?</think>", r"<thinking>.*?</thinking>"]
    for p in patterns:
        clean_content = re.sub(p, "", clean_content, flags=re.DOTALL | re.IGNORECASE).strip()
    
    # Nettoyage des balises orphelines (ex: <thought> sans </thought>)
    clean_content = re.sub(r'</?(thought|think|thinking)>', '', clean_content, flags=re.IGNORECASE).strip()
        
    # Si après nettoyage il ne reste rien, on tente de récupérer le contenu des balises thought
    # (Cas fréquent où le petit modèle met TOUTE sa réponse dans <thought>)
    if not clean_content or len(clean_content) < 150:
        # On cherche à extraire les pensées brutes du contenu original si possible
        raw_thought = extract_thought(content)
        if raw_thought and len(raw_thought) > len(clean_content):
            clean_content = raw_thought
        elif thoughts and len(" ".join(thoughts)) > 150:
            # Fallback sur la liste des pensées du state si elles sont riches
            all_thoughts = "\n\n".join(thoughts) if isinstance(thoughts, list) else str(thoughts)
            clean_content = all_thoughts.replace("**Analysis:**", "").replace("**Expert Optimization:**", "").replace("**Thinking:**", "").strip()
            
    if not clean_content or len(clean_content) < 2:
        clean_content = "✅ J'ai terminé ma réflexion. (Consulte la console de réflexion pour les détails)"
            
    final_message = AIMessage(
        content=clean_content,
        additional_kwargs={
            "thoughts_history": thoughts,
            "context": state.get("context", ""),
            "graph_nodes": state.get("graph_nodes", []),
            "graph_edges": state.get("graph_edges", [])
        }
    )
    
    return {
        "messages": [final_message], 
        "steps": ["final_response"],
        "graph_nodes": state.get("graph_nodes", []),
        "graph_edges": state.get("graph_edges", []),
        "vision_description": None # On vide la mémoire visuelle après usage
    }

async def expert_review_node(state: AgentState):
    """Vérifie la réponse (brouillon) et l'améliore si nécessaire."""
    llm_model = state.get("selected_model", "").lower()
    is_small_model = any(size in llm_model for size in ["3b", "4b", "7b", "8b", "9b"])
    draft_answer = state.get("generation", "")
    
    if not draft_answer or is_small_model:
        print(f"--- 🛡️ EXPERT: Review skipped (Model {llm_model} is too small or no draft) ---", flush=True)
        yield {"steps": ["expert_review_skipped"]}
        return
    
    messages = state.get("messages", [])
    
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        custom_url=state.get("llm_custom_url"),
        temperature=0.1,
        role="reviewer"
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

    # On ne remplace par l'expert QUE si sa réponse est valide et non vide
    final_gen = clean_expert_content if clean_expert_content else draft_answer
    
    yield {
        "generation": final_gen, 
        "steps": ["expert_review_passed"], 
        "detail": "Technical optimization completed.",
        "thoughts": [f"**Expert Optimization:** {thought}"] if thought else ["**Expert Optimization:** Response validated and optimized for the technical stack."]
    }
