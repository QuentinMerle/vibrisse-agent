# app/services/finops.py

# Tarification simulée pour l'aspect éducatif (ex: GPT-4o pricing)
# Prix pour 1000 tokens (1k)
MODEL_PRICING = {
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
    "gemma4:e4b": {"prompt": 0.005, "completion": 0.015}, # On simule un coût pour Gemma
    "default": {"prompt": 0.005, "completion": 0.015}
}

def calculate_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calcule le coût en dollars basé sur le nombre de tokens."""
    # Nettoyage du nom du modèle (ex: ollama/gemma4:e4b -> gemma4:e4b)
    clean_model = model_name.split("/")[-1]
    
    pricing = MODEL_PRICING.get(clean_model, MODEL_PRICING["default"])
    
    prompt_cost = (prompt_tokens / 1000.0) * pricing["prompt"]
    completion_cost = (completion_tokens / 1000.0) * pricing["completion"]
    
    return prompt_cost + completion_cost

def update_token_usage(state_usage: dict, new_usage: dict, model_name: str) -> dict:
    """Met à jour l'état d'usage global avec une nouvelle requête."""
    if not state_usage:
        state_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_cost": 0.0}
        
    p_tokens = new_usage.get("prompt_tokens", 0)
    c_tokens = new_usage.get("completion_tokens", 0)
    
    cost = calculate_cost(model_name, p_tokens, c_tokens)
    
    return {
        "prompt_tokens": state_usage.get("prompt_tokens", 0) + p_tokens,
        "completion_tokens": state_usage.get("completion_tokens", 0) + c_tokens,
        "total_cost": state_usage.get("total_cost", 0.0) + cost
    }
