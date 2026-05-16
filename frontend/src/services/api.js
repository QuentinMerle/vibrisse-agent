// Configuration de l'API - Mode Unifié
const API_ROOT = window.location.origin.includes("localhost") 
  ? "http://localhost:8001/api" 
  : "/api";

// Caches simples en mémoire
const modelCache = new Map();
const limitCache = new Map();
const capsCache = new Map();

export const api = {
  // SYSTEM
  checkHealth: async () => {
    const res = await fetch(`${API_ROOT}/system/health`);
    return res.json();
  },
  getConfig: async () => {
    const res = await fetch(`${API_ROOT}/system/config`);
    return res.json();
  },
  getFiles: async () => {
    const res = await fetch(`${API_ROOT}/system/files`);
    return res.json();
  },
  getModels: async (provider, apiKey, customUrl) => {
    const prov = provider || 'ollama';
    const cacheKey = `${prov}:${apiKey || 'default'}:${customUrl || 'default'}`;
    
    if (modelCache.has(cacheKey)) {
      return { models: modelCache.get(cacheKey), fromCache: true };
    }

    let url = `${API_ROOT}/system/models?provider=${prov}`;
    if (apiKey) url += `&api_key=${encodeURIComponent(apiKey)}`;
    if (customUrl) url += `&custom_url=${encodeURIComponent(customUrl)}`;
    
    const res = await fetch(url);
    const data = await res.json();
    
    if (data.models && data.models.length > 0) {
      modelCache.set(cacheKey, data.models);
    }
    return data;
  },
  getModelLimit: async (model) => {
    if (limitCache.has(model)) return { limit: limitCache.get(model), fromCache: true };
    
    const res = await fetch(`${API_ROOT}/system/models/limit/${model}`);
    const data = await res.json();
    if (data.limit) limitCache.set(model, data.limit);
    return data;
  },
  getCapabilities: async (provider, model) => {
    const cacheKey = `${provider}:${model}`;
    if (capsCache.has(cacheKey)) return { ...capsCache.get(cacheKey), fromCache: true };

    const res = await fetch(`${API_ROOT}/system/capabilities?provider=${provider}&model=${model || ''}`);
    const data = await res.json();
    if (data) capsCache.set(cacheKey, data);
    return data;
  },
  clearCache: async () => {
    const res = await fetch(`${API_ROOT}/system/cache/clear`, { method: "POST" });
    return res.json();
  },
  updateGlobalModel: async (data) => {
    const res = await fetch(`${API_ROOT}/system/config/model`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    return res.json();
  },
  updateSettings: async (data) => {
    const res = await fetch(`${API_ROOT}/system/config/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    return res.json();
  },
  updateTargetPath: async (path) => {
    const res = await fetch(`${API_ROOT}/system/config/target`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path })
    });
    return res.json();
  },

  // MCP (Model Context Protocol)
  getMcpStatus: async () => {
    const res = await fetch(`${API_ROOT}/system/mcp/status`);
    return res.json();
  },
  connectMcp: async (payload) => {
    const res = await fetch(`${API_ROOT}/system/mcp/connect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload) // { server_id, command, args, env }
    });
    return res.json();
  },
  disconnectMcp: async (serverId) => {
    const res = await fetch(`${API_ROOT}/system/mcp/disconnect/${serverId}`, {
      method: "POST"
    });
    return res.json();
  },

  // THREADS
  getThreads: async () => {
    const res = await fetch(`${API_ROOT}/threads/`);
    return res.json();
  },
  getThreadHistory: async (threadId) => {
    const res = await fetch(`${API_ROOT}/threads/${threadId}`);
    return res.json();
  },
  deleteThread: async (threadId) => {
    const res = await fetch(`${API_ROOT}/threads/${threadId}`, { method: "DELETE" });
    return res.json();
  },

  // CHAT
  chat: (payload, signal, llmSettings = {}) => {
    const headers = { "Content-Type": "application/json" };
    
    // Détection de la clé spécifique au provider
    const apiKey = llmSettings.apiKeys ? llmSettings.apiKeys[llmSettings.provider] : llmSettings.apiKey;

    if (llmSettings.provider) headers["X-Vibrisse-Provider"] = llmSettings.provider;
    if (apiKey) headers["X-Vibrisse-Api-Key"] = apiKey;
    
    const customUrl = llmSettings.customUrls ? llmSettings.customUrls[llmSettings.provider] : llmSettings.customUrl;
    if (customUrl) headers["X-Vibrisse-Custom-Url"] = customUrl;
    
    // Le modèle dans le payload (choix manuel) est prioritaire sur le modèle des settings
    // SAUF si on est sur un provider cloud, où on veut le modèle configuré spécifiquement
    const finalModel = (llmSettings.provider && llmSettings.provider !== 'ollama') 
      ? (llmSettings.model || payload.model)
      : (payload.model || llmSettings.model);

    if (finalModel) headers["X-Vibrisse-Model"] = finalModel;
    headers["X-Vibrisse-Sovereign-Routing"] = llmSettings.sovereignRouting ? "true" : "false";

    return fetch(`${API_ROOT}/chat/`, {
      method: "POST",
      headers,
      signal,
      body: JSON.stringify(payload)
    });
  },
  approveCommand: (payload) => {
    return fetch(`${API_ROOT}/chat/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  },
  validateLLM: async (payload) => {
    // Si l'objet settings est passé, on extrait la bonne clé
    const apiKey = payload.apiKeys ? payload.apiKeys[payload.provider] : payload.apiKey;
    const customUrl = payload.customUrls ? payload.customUrls[payload.provider] : payload.customUrl;
    
    const res = await fetch(`${API_ROOT}/system/validate-llm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, apiKey, customUrl })
    });
    return res.json();
  },
  evaluateRAG: async (data) => {
    const res = await fetch(`${API_ROOT}/system/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    return res.json();
  }
};
