import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

load_dotenv()

class LLMFactory:
    @staticmethod
    def get_model(purpose: str = "generation"):
        """
        purpose: "generation" (pour le chat) ou "evaluation" (pour le juge)
        """
        mode = os.getenv("LLM_MODE", "local").lower()
        
        if mode == "cloud":
            # Le nom exact du modèle Flash
            model_name = "gemini-1.5-flash-latest"
            print(f"☁️ Using Gemini ({model_name}) for {purpose}")
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        else:
            model_name = "gemma4:e4b" if purpose == "generation" else "gemma4:e4b"
            print(f"🏠 Using Local Ollama ({model_name}) for {purpose}")
            return ChatOllama(model=model_name, base_url="http://localhost:11434")

    @staticmethod
    def get_embeddings():
        mode = os.getenv("LLM_MODE", "local").lower()
        if mode == "cloud":
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        else:
            return OllamaEmbeddings(model="nomic-embed-text")