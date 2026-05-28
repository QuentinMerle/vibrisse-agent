import operator
from typing import List, TypedDict, Literal, Annotated, Optional
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class RouteQuery(BaseModel):
    """Sortie structurée pour le routage/supervision via Vibrisse Agent"""
    datasource: Literal["vectorstore", "direct_response", "web_and_tools"] = Field(
        ..., description="Décide du flux technique (RAG, Direct, Outils)."
    )
    worker: Literal["coder", "writer", "architect", "general"] = Field(
        default="general", description="Définit le profil d'expertise (casquette) à utiliser."
    )
    reasoning: str = Field(description="Explication courte du choix stratégique.")

def thoughts_reducer(old: List[str], new: List[str]) -> List[str]:
    """Reducer personnalisé pour gérer le journal de réflexion. 
    Si la nouvelle liste commence par '__RESET__', on vide l'historique."""
    if new and new[0] == "__RESET__":
        return new[1:]
    return (old or []) + (new or [])

def dict_reducer(old: dict, new: dict) -> dict:
    """Reducer pour mettre à jour un dictionnaire (ex: artifacts)."""
    res = old.copy() if old else {}
    if new:
        res.update(new)
    return res

def unique_nodes_reducer(old: List[dict], new: List[dict]) -> List[dict]:
    """Combine les nœuds en évitant les doublons par ID."""
    node_map = {n['id']: n for n in (old or [])}
    for n in (new or []):
        node_map[n['id']] = n
    return list(node_map.values())

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages] # Historique pour les tools
    question: str
    decision: str
    active_worker: str # Nom du worker actuellement en charge
    context: List[str]  # Contiendra les chunks parents (Small-to-Big)
    generation: str
    steps: Annotated[List[str], operator.add]
    token_usage: dict
    context_usage: int # Utilisation du contexte en caractères
    image: Optional[str] # Base64 de l'image (optionnel)
    vision_description: Optional[str]
    pending_review: bool
    pending_plan: Optional[bool] # Attend l'approbation du plan
    current_plan: Optional[str]  # Le plan proposé
    artifacts: Annotated[dict, dict_reducer] # Stocke l'état des documents vivants
    selected_model: Optional[str]
    llm_provider: Optional[str]
    llm_api_key: Optional[str]
    llm_custom_url: Optional[str] # URL pour OpenAI Custom (vLLM, LM Studio, etc.)
    offload_proposal: Optional[dict] # Détails de la proposition de délestage
    thoughts: Annotated[List[str], thoughts_reducer] # Journal de réflexion chronologique
    graph_nodes: Annotated[List[dict], unique_nodes_reducer] # Nœuds pour la visualisation (Thought Graph)
    graph_edges: Annotated[List[dict], operator.add] # Arêtes pour la visualisation