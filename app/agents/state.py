import operator
from typing import List, TypedDict, Literal, Annotated, Optional
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class RouteQuery(BaseModel):
    """Sortie structurée pour le routage via Vibrisse Agent"""
    datasource: Literal["vectorstore", "direct_response", "web_and_tools"] = Field(
        ..., description="Décide si la question nécessite le code source, une réponse générale, ou l'utilisation d'outils web/système."
    )
    reasoning: str = Field(description="Explication courte du choix.")

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages] # Historique pour les tools
    question: str
    decision: str
    context: List[str]  # Contiendra les chunks parents (Small-to-Big)
    generation: str
    steps: Annotated[List[str], operator.add]
    token_usage: dict
    context_usage: int # Utilisation du contexte en caractères
    image: Optional[str] # Base64 de l'image (optionnel)
    vision_description: Optional[str]
    pending_review: bool
    selected_model: Optional[str]
    llm_provider: Optional[str]
    llm_api_key: Optional[str]
    thoughts: Annotated[List[str], operator.add] # Journal de réflexion chronologique