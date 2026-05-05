from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class ChatService:
    def __init__(self, vector_service):
        self.vector_service = vector_service
        self.llm = ChatOllama(model="gemma4:e4b", temperature=0) # On peut ajuster le modèle
        
        # Le prompt magique pour le code
        self.template = """Tu es un expert en développement logiciel. Utilise les extraits de code suivants pour répondre à la question technique.
Si tu ne connais pas la réponse avec ces extraits, dis simplement que tu ne sais pas, ne tente pas d'inventer du code.
Sois concis et technique dans tes explications.

CONTEXTE :
{context}

QUESTION : {question}

REPONSE (en Markdown) :"""
        self.prompt = ChatPromptTemplate.from_template(self.template)

    def _format_docs(self, docs):
        return "\n\n".join(f"--- Fichier: {doc.metadata.get('source')} ---\n{doc.page_content}" for doc in docs)

    async def ask(self, question: str):
        retriever = self.vector_service.get_retriever()
        
        # Construction de la chaîne RAG
        chain = (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        return await chain.ainvoke(question)
