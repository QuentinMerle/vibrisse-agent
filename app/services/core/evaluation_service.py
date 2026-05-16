import os
import logging
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class EvaluationService:
    def __init__(self):
        try:
            self.judge_llm = self._init_judge_llm()
        except Exception as e:
            logger.error(f"EvaluationService init failed: {e}")
            self.judge_llm = None

    def _init_judge_llm(self):
        """Initialise le modèle LLM qui servira de juge pour l'évaluation."""
        try:
            from langchain_ollama import ChatOllama
            from langchain_core.language_models.chat_models import BaseChatModel
            from langchain_core.messages import BaseMessage, AIMessage
            from langchain_core.outputs import ChatResult, ChatGeneration
            from pydantic import Field
            
            model_name = settings.RAGAS_MODEL.split("/")[-1]
            logger.info(f"Using local Ragas judge: {model_name}")
            
            raw_llm = ChatOllama(
                model=model_name,
                base_url=settings.LLM_BASE_URL,
                temperature=0,
            )
            
            # Classe robuste héritant de BaseChatModel pour tromper Ragas proprement
            class LocalJSONJudge(BaseChatModel):
                raw_llm: ChatOllama = Field(exclude=True)
                
                def _clean(self, text: str) -> str:
                    import re
                    json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
                    return json_match.group(0) if json_match else text.replace('```json', '').replace('```', '').strip()

                def _generate(self, messages, stop=None, run_manager=None, **kwargs):
                    res = self.raw_llm.invoke(messages, stop=stop, **kwargs)
                    content = self._clean(res.content if hasattr(res, 'content') else str(res))
                    return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

                async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
                    res = await self.raw_llm.ainvoke(messages, stop=stop, **kwargs)
                    content = self._clean(res.content if hasattr(res, 'content') else str(res))
                    return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

                @property
                def _llm_type(self) -> str:
                    return "local-json-judge"

            return LocalJSONJudge(raw_llm=raw_llm)
            
        except Exception as e:
            logger.error(f"Failed to init Ragas judge LLM: {e}")
            return None

    async def evaluate_interaction(self, question: str, contexts: List[str], generation: str) -> Dict[str, Any]:
        """Évalue une interaction RAG unique via les métriques Ragas."""
        try:
            from ragas.metrics import Faithfulness, AnswerRelevancy
            from ragas import aevaluate
            from datasets import Dataset
            from langchain_ollama import OllamaEmbeddings
        except ImportError as e:
            logger.error(f"Ragas dependencies not found: {e}")
            return {"status": "error", "message": f"Dépendances Ragas manquantes: {e}"}

        if not self.judge_llm:
            return {"status": "error", "message": "Judge LLM not initialized"}

        try:
            model_name = settings.RAGAS_MODEL.split("/")[-1]
            logger.info(f"[RAGAS] Évaluation lancée avec {model_name}...")
            
            # Correction du format des contextes
            processed_contexts = contexts
            if isinstance(contexts, str):
                processed_contexts = [c.strip() for c in contexts.split("--- FICHIER:") if c.strip()]
            
            # Préparation des données
            data_dict = {
                "question": [question],
                "contexts": [processed_contexts],
                "answer": [generation]
            }
            dataset = Dataset.from_dict(data_dict)

            # Initialisation explicite des métriques avec les bons modèles
            embedding_model = settings.RAGAS_EMBEDDING_MODEL.split("/")[-1]
            local_embeddings = OllamaEmbeddings(model=embedding_model)
            
            # On crée de NOUVELLES instances pour être sûr qu'elles utilisent nos modèles
            m_faithfulness = Faithfulness(llm=self.judge_llm)
            m_relevancy = AnswerRelevancy(llm=self.judge_llm, embeddings=local_embeddings)

            # Exécution de l'évaluation
            result = await aevaluate(
                dataset=dataset,
                metrics=[m_faithfulness, m_relevancy],
                llm=self.judge_llm,
                embeddings=local_embeddings
            )

            # Ragas 0.4+ renvoie un objet EvaluationResult
            # On le convertit proprement pour extraire les scores du premier (et seul) échantillon
            try:
                import math
                scores_list = result.to_pandas().to_dict('records')
                first_record = scores_list[0] if scores_list else {}
                
                def safe_float(v):
                    try:
                        f = float(v)
                        return 0.0 if math.isnan(f) or math.isinf(f) else f
                    except:
                        return 0.0

                f_score = safe_float(first_record.get("faithfulness", 0.0))
                r_score = safe_float(first_record.get("answer_relevancy", 0.0))
            except Exception as e:
                logger.error(f"Error parsing Ragas result: {e}")
                f_score = 0.0
                r_score = 0.0

            return {
                "status": "success",
                "faithfulness": f_score,
                "answer_relevancy": r_score,
                "global_score": (f_score + r_score) / 2
            }
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            logger.error(f"Ragas evaluation failed: {error_detail}")
            return {
                "status": "error", 
                "message": str(e),
                "detail": error_detail if settings.APP_DEBUG else None
            }

evaluation_service = EvaluationService()
