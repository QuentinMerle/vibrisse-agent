# app/services/llm_service.py
import litellm
import instructor
from openai import OpenAI
from langsmith import traceable
from app.core.config import settings
from app.schemas.core import VerifiedResponse

class LLMService:
    def __init__(self):
        # Configuration globale LiteLLM
        litellm.drop_params = True 
        
        # On utilise le client OpenAI pointant vers l'API compatible d'Ollama (/v1)
        # C'est la méthode la plus stable pour utiliser Instructor avec Ollama en local (Gemma)
        self.client = instructor.from_openai(
            OpenAI(
                base_url=f"{settings.LLM_BASE_URL}/v1",
                api_key="ollama", # Requis par le client OpenAI mais ignoré par Ollama
            ),
            mode=instructor.Mode.JSON
        )

    async def generate_response(self, prompt: str, system_prompt: str = "Tu es un expert en analyse de code.") -> str:
        """
        Génère une réponse de manière asynchrone via LiteLLM.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await litellm.acompletion(
                model=settings.LLM_MODEL,
                messages=messages,
                api_base=settings.LLM_BASE_URL,
                temperature=settings.LLM_TEMPERATURE,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"DEBUG: Model used was {settings.LLM_MODEL}")
            return f"Erreur d'inférence : {type(e).__name__} - {str(e)}"

    @traceable(name="Gemma Guarded Call")
    def generate_guarded_answer(self, query: str, context_documents: list):
        """
        Génère une réponse structurée et vérifiée via Instructor.
        Enregistre l'appel dans LangSmith via le décorateur @traceable.
        """
        # Extraction des métadonnées pour le validateur Pydantic
        # On s'assure que 'file_path' est présent (LangChain utilise 'source')
        metadata_only = []
        for doc in context_documents:
            meta = doc.metadata.copy()
            if "source" in meta and "file_path" not in meta:
                meta["file_path"] = meta["source"]
            metadata_only.append(meta)

        # On nettoie le nom du modèle pour Ollama
        model_name = settings.LLM_MODEL.split('/')[-1]

        response, raw = self.client.chat.completions.create_with_completion(
            model=model_name,
            response_model=VerifiedResponse,
            validation_context={"retrieved_metadata": metadata_only},
            max_retries=3,
            messages=[
                {"role": "system", "content": "Tu es un expert en code. Tu DOIS citer les fichiers fournis."},
                {"role": "user", "content": f"Context: {context_documents}\n\nQuestion: {query}"}
            ]
        )
        return response, raw

# Singleton pour l'injection de dépendances
llm_service = LLMService()

class LLMFactory:
    @staticmethod
    def get_model(structured_model=None):
        """
        Retourne un client configuré (Instructor) pour un modèle spécifique.
        """
        return llm_service.client