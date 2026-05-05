from typing import List, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.core.config import settings
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import load_skill, calculate_context_usage

async def rerank_documents(query: str, docs: List[Any], state: AgentState) -> List[Any]:
    """Utilise le LLM pour filtrer les documents les plus pertinents."""
    if not docs: return []
    
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        temperature=0
    )
    
    skill_prompt = load_skill("code_reranker")
    docs_text = ""
    for i, doc in enumerate(docs):
        docs_text += f"\n--- EXTRAIT {i} (Source: {doc.metadata.get('source')}) ---\n{doc.page_content[:500]}...\n"
        
    prompt = f"QUESTION: {query}\n\n{docs_text}\n\nIndices pertinents :"
    
    try:
        response = await llm.ainvoke([
            SystemMessage(content=skill_prompt),
            HumanMessage(content=prompt)
        ])
        
        indices_str = response.content.strip()
        if "NONE" in indices_str.upper():
            return docs[:3] # Fallback sur les 3 premiers si le LLM est perdu
            
        indices = [int(idx.strip()) for idx in indices_str.split(",") if idx.strip().isdigit()]
        reranked = [docs[i] for i in indices if i < len(docs)]
        return reranked if reranked else docs[:3]
    except Exception as e:
        print(f"⚠️ Reranking failed: {e}")
        return docs[:5] # Fallback sécurité

async def retrieve_code(state: AgentState):
    question = state.get("question", "")
    vision_desc = state.get("vision_description")
    
    # On enrichit la recherche avec ce qu'on a vu
    search_query = question
    if vision_desc:
        search_query = f"{question} {vision_desc[:200]}"
    
    try:
        yield {"detail": f"Recherche sémantique : '{search_query[:60]}...' dans le code source", "steps": ["retrieving_code"]}
        
        from app.services.rag.vs_instance import vs
        # 1. Récupération large
        docs = await vs.search(search_query)
        
        # 2. Re-ranking moins agressif pour garder du contexte
        if len(docs) > 8:
            print(f"--- 🎯 RE-RANKING : Filtrage de {len(docs)} documents ---", flush=True)
            docs = await rerank_documents(question, docs, state)
            
        context = ""
        for doc in docs:
            source = doc.metadata.get("source", "Inconnu")
            context += f"\n--- FICHIER: {source} ---\n{doc.page_content}\n"
        
        if not context.strip():
            context = f"Note: Recherche RAG infructueuse pour '{search_query}'. Voici le manifeste global :\n{settings.PROJECT_MANIFEST}"
            
        new_state = {"context": context, "steps": ["retrieve_code", f"reranked:{len(docs)}"]}
        temp_state = state.copy()
        temp_state.update(new_state)
        new_state["context_usage"] = calculate_context_usage(temp_state)
        new_state["detail"] = f"Code : {len(docs)} fichiers pertinents trouvés."
        new_state["thoughts"] = [f"**Recherche RAG :** J'ai extrait {len(docs)} fichiers pertinents du projet pour répondre à la question."]
        yield new_state
    except Exception as e:
        print(f"⚠️ Retrieval Error: {e}")
        yield {"context": settings.PROJECT_MANIFEST, "steps": ["retrieve_error"]}
