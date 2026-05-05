import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agents.state import AgentState
from app.core.config import settings
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import extract_thought

async def generate_answer(state: AgentState):
    context = state.get("context", "")
    messages = state.get("messages", [])
    vision_desc = state.get("vision_description")
    
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key")
    )
    
    # Construction du prompt ultra-précis
    vision_context = f"\n--- ANALYSE VISUELLE DE L'IMAGE ---\n{vision_desc}\n" if vision_desc else ""
    rag_context = f"\n--- CONTEXTE DU PROJET (SOURCE DE VÉRITÉ) ---\n{context}\n" if context else ""
    
    # Récupération du profil du projet (Manifeste généré à l'ingestion)
    project_profile = settings.get_project_profile()
    
    instruction = f"""Tu es l'Expert Technique Senior de Vibrisse.
Ta mission est de répondre à la question de l'utilisateur avec précision et professionnalisme.

SOURCES DISPONIBLES :
1. ANALYSE VISUELLE : {vision_desc if vision_desc else "Aucune image fournie."}
2. CONTEXTE DU PROJET (RAG) : {context if context else "Aucun fichier source pertinent trouvé dans le code."}
3. OUTILS & WEB : Si des messages de type 'tool' sont présents dans l'historique, utilise-les comme source de vérité pour les données temps réel ou externes.

--- PROFIL DU PROJET ANALYSÉ ---
{project_profile}

RÈGLES CRITIQUES :
- Priorité aux sources : Utilise les sources ci-dessus pour répondre. Si l'information vient d'une recherche web, synthétise-la.
- Fidélité Technique : Si la question concerne le code, adopte strictement la stack et les conventions décrites dans le PROFIL DU PROJET.
- Expertise Polyvalente : Bien que ton expertise soit technique, tu dois répondre aux questions générales (météo, actualité) si et seulement si les outils de recherche t'ont fourni les données.
- COMMENCE TOUJOURS par une balise <thought> pour détailler ton raisonnement technique ou ta stratégie de synthèse en français.
"""

    # Analyse de la source pour la pensée initiale
    source_info = "fichiers locaux" if context else "connaissances générales"
    if vision_desc: source_info = "analyse visuelle"
    if any(msg.type == 'tool' or (isinstance(msg, AIMessage) and msg.tool_calls) for msg in messages):
        source_info = "résultats de recherche web/outils"
    
    yield {
        "thoughts": [f"**Rédaction :** Je synthétise une réponse basée sur les {source_info}."],
        "detail": "Rédaction de la réponse finale...",
        "steps": ["generation_started"]
    }

    full_message = ""
    async for chunk in llm.astream([SystemMessage(content=instruction)] + messages):
        content = chunk.content if hasattr(chunk, "content") else str(chunk)
        full_message += content
        yield chunk
    
    # Sécurité : Si le stream est resté vide, on tente une invocation directe
    if not full_message.strip():
        print("⚠️ Stream vide détecté, tentative de fallback ainvoke...", flush=True)
        fallback_resp = await llm.ainvoke([SystemMessage(content=instruction)] + messages)
        full_message = fallback_resp.content
        # On n'émet pas de chunk ici car le stream est fini, mais on remplit 'generation'
    
    # On stocke le résultat final dans 'generation' pour la synthèse finale
    thought = extract_thought(full_message)
    yield {
        "generation": full_message, 
        "steps": ["generation_complete"],
        "thoughts": [f"**Analyse :** {thought}"] if thought else ["**Analyse :** La réponse a été générée et structurée."]
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
        content = "Désolé, je n'ai pas pu générer de réponse."
    
    # Nettoyage final des balises résiduelles dans le corps du message
    clean_content = content
    patterns = [r"<thought>.*?</thought>", r"<think>.*?</think>", r"<thinking>.*?</thinking>"]
    for p in patterns:
        clean_content = re.sub(p, "", clean_content, flags=re.DOTALL | re.IGNORECASE).strip()
        
    if not clean_content:
        # Fallback si le modèle a absolument tout écrit à l'intérieur de ses balises de pensée
        clean_content = "✅ Opération terminée. (Résultat technique dans les logs)"
        
    # Construction d'une chronologie de pensée élégante et structurée
    # On filtre les doublons ou pensées vides
    unique_thoughts = []
    for t in thoughts:
        if t and t not in unique_thoughts:
            unique_thoughts.append(t)
            
    # On transmet la chronologie via les métadonnées, pas dans le texte
    final_message = AIMessage(
        content=clean_content,
        additional_kwargs={"thoughts_history": unique_thoughts}
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
    
    expert_prompt = """Tu es l'Ingénieur de Contrôle Qualité de Vibrisse.
Ta mission : Renvoyer UNIQUEMENT le CODE et les explications techniques, comme si tu étais le premier à parler.

INTERDICTIONS FORMELLES (SOUS PEINE D'ERREUR CRITIQUE) :
- Ne fais JAMAIS référence à "la proposition précédente" ou "le brouillon".
- Ne commence JAMAIS par "Absolument", "Voici", "La proposition", etc.
- Produis UNIQUEMENT le contenu final utile (Titre, Explication, Code).
- Tu DOIS inclure une balise <thought> au début pour ton raisonnement.
"""
    
    print(f"--- 🛡️ EXPERT : Revue en cours ---", flush=True)
    # On informe l'utilisateur qu'on passe en revue la réponse
    yield {"detail": "Analyse critique et optimisation technique de la réponse...", "steps": ["expert_review_started"]}
    
    response = await llm.ainvoke([SystemMessage(content=expert_prompt)] + messages + [HumanMessage(content=f"Brouillon à réviser :\n{draft_answer}")])
    
    # L'expert ne doit pas polluer la réponse avec du meta-talk
    thought = extract_thought(response.content)
    # On nettoie la réponse de l'expert pour ne garder que le contenu utile
    clean_expert_content = response.content
    for p in [r"<thought>.*?</thought>", r"<think>.*?</think>", r"<thinking>.*?</thinking>"]:
        clean_expert_content = re.sub(p, "", clean_expert_content, flags=re.DOTALL | re.IGNORECASE).strip()

    yield {
        "generation": clean_expert_content, 
        "steps": ["expert_review_passed"], 
        "detail": "Optimisation technique terminée.",
        "thoughts": [f"**Optimisation Expert :** {thought}"] if thought else ["**Optimisation Expert :** La réponse a été validée et optimisée pour la stack technique."]
    }
