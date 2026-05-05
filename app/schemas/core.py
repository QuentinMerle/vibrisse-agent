from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class CodeCitation(BaseModel):
    file_path: str = Field(..., description="Chemin exact du fichier source")
    function_name: Optional[str] = Field(None, description="Nom de la fonction détectée par l'AST")

class VerifiedResponse(BaseModel):
    answer: str
    citations: List[CodeCitation]

    @field_validator("citations")
    @classmethod
    def must_have_valid_citations(cls, v, info):
        # 1. On force la présence de citations si on veut une réponse sourcée
        if not v:
            raise ValueError("Tu dois citer au moins un fichier du contexte pour justifier ta réponse.")
        
        # 2. On vérifie l'existence réelle
        valid_metadata = info.context.get("retrieved_metadata", [])
        valid_files = {m['file_path'] for m in valid_metadata}
        
        for citation in v:
            if citation.file_path not in valid_files:
                raise ValueError(f"Fichier inconnu : {citation.file_path}")
        return v