import { useState, useEffect } from 'react';
import { api } from '../services/api';

export const useSettings = () => {
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('vibrisse_llm_settings');
    let data = saved ? JSON.parse(saved) : {
      provider: 'ollama',
      model: '',
      apiKey: '',
      apiKeys: {},
      sovereignRouting: true,
      tavilyApiKey: '',
      githubToken: '',
      enableWebSearch: true,
      enableVision: true,
      enableExpertReview: true
    };
    
    // Migration: si on a une ancienne apiKey mais pas de apiKeys, on l'injecte
    if (data.apiKey && (!data.apiKeys || Object.keys(data.apiKeys).length === 0)) {
      data.apiKeys = { [data.provider]: data.apiKey };
    }
    
    return data;
  });

  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem('vibrisse_llm_settings', JSON.stringify(settings));
  }, [settings]);

  // Sync with backend on mount
  useEffect(() => {
    api.getConfig().then(config => {
      if (config.api_keys) {
        setSettings(prev => ({
          ...prev,
          tavilyApiKey: config.api_keys.tavily || prev.tavilyApiKey,
          githubToken: config.api_keys.github || prev.githubToken,
          enableWebSearch: config.features?.search ?? prev.enableWebSearch,
          enableVision: config.features?.vision ?? prev.enableVision,
          enableExpertReview: config.features?.expert_review ?? prev.enableExpertReview,
          apiKeys: {
            ...prev.apiKeys,
            groq: config.api_keys.groq || prev.apiKeys.groq,
            openrouter: config.api_keys.openrouter || prev.apiKeys.openrouter,
            google: config.api_keys.google || prev.apiKeys.google,
          }
        }));
      }
    });
  }, []);

  const updateSettings = (newSettings) => {
    setSettings(newSettings);
    if (newSettings.provider) localStorage.setItem('vibrisse_provider', newSettings.provider);
    if (newSettings.apiKey) localStorage.setItem('vibrisse_api_key', newSettings.apiKey);
    if (newSettings.customUrl) localStorage.setItem('vibrisse_custom_url', newSettings.customUrl);
    if (newSettings.model) localStorage.setItem('vibrisse_model', newSettings.model);
    localStorage.setItem('vibrisse_sovereign_routing', newSettings.sovereignRouting);
    
    // Persistance Backend pour le modèle global
    if (newSettings.model || newSettings.provider) {
      api.updateGlobalModel({
        model: newSettings.model || '',
        provider: newSettings.provider || 'ollama'
      }).catch(err => console.error("Failed to update global model in backend:", err));
    }

    // Persistance Backend pour les clés API sensibles (Tavily, etc.)
    api.updateSettings({
      tavily_api_key: newSettings.tavilyApiKey,
      github_token: newSettings.githubToken,
      enable_web_search: newSettings.enableWebSearch,
      enable_vision: newSettings.enableVision,
      enable_expert_review: newSettings.enableExpertReview,
      groq_api_key: newSettings.apiKeys?.groq,
      openrouter_api_key: newSettings.apiKeys?.openrouter,
      google_api_key: newSettings.apiKeys?.google
    }).catch(err => console.error("Failed to persist settings to backend:", err));
  };

  return {
    settings,
    updateSettings,
    isSettingsOpen,
    setIsSettingsOpen
  };
};
