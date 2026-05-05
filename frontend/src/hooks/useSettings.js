import { useState, useEffect } from 'react';

export const useSettings = () => {
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('vibrisse_llm_settings');
    let data = saved ? JSON.parse(saved) : {
      provider: 'ollama',
      model: '',
      apiKey: '',
      apiKeys: {}
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

  const updateSettings = (newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  return {
    settings,
    updateSettings,
    isSettingsOpen,
    setIsSettingsOpen
  };
};
