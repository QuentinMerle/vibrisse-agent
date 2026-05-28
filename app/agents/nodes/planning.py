from langchain_core.messages import AIMessage, SystemMessage
from app.agents.state import AgentState
from app.services.llm.llm_factory import get_llm
from app.agents.nodes.utils import create_node, create_edge, clean_messages_for_llm

async def planning_node(state: AgentState):
    yield {"detail": "Génération du plan d'implémentation...", "steps": ["planning_started"]}
    
    prompt = """Tu es un Tech Lead. L'utilisateur demande une modification complexe ou architecturale.
Rédige un plan d'implémentation concis en Markdown avec :
1. **Objectif** : Résumé rapide.
2. **Modifications** : Liste des fichiers et changements prévus.
3. **Questions (optionnel)** : Si besoin de précisions.

IMPORTANT : Ne génère AUCUN code final. Limite-toi au plan.
"""
    
    llm = get_llm(
        provider=state.get("llm_provider", "ollama"),
        model=state.get("selected_model"),
        api_key=state.get("llm_api_key"),
        custom_url=state.get("llm_custom_url"),
        temperature=0.2,
        role="architect"
    )
    
    messages = state.get("messages", [])
    cleaned_messages = clean_messages_for_llm(messages)
    response = await llm.ainvoke([
        SystemMessage(content=prompt),
        *cleaned_messages
    ])
    
    plan_content = response.content
    
    yield {
        "pending_plan": True,
        "current_plan": plan_content,
        "messages": [AIMessage(content=f"J'ai préparé un plan d'implémentation pour cette tâche. Veuillez l'examiner dans le panneau de droite.\n\n<artifact id='plan'>\n{plan_content}\n</artifact>")],
        "thoughts": ["**Planning:** Plan généré. [Cliquez ici pour consulter le plan d'implémentation](vibrisse://plan) ou utilisez les boutons ci-dessous pour valider."],
        "graph_nodes": [create_node("planning", "Planning", "TOOL", "📝")]
    }
