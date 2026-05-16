import React, { useState, useEffect } from 'react';
import { Server, Cpu, Key, ChevronDown, Loader2, Check, RotateCw } from 'lucide-react';
import { api } from '../../services/api';

const LLMTab = ({ localSettings, setLocalSettings }) => {
  const [availableModels, setAvailableModels] = useState([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = React.useRef(null);

  const providers = [
    { id: 'ollama', name: 'Ollama (Local)', icon: <Server size={16} /> },
    { id: 'vllm', name: 'Custom', icon: <Server size={16} /> },
    { id: 'ollama_cloud', name: 'Ollama Cloud', icon: <Cpu size={16} /> },
    { id: 'openrouter', name: 'OpenRouter', icon: <Cpu size={16} /> },
    { id: 'groq', name: 'Groq', icon: <Cpu size={16} /> },
  ];

  const fetchModels = React.useCallback(async () => {
    const needsKey = ['ollama_cloud', 'openrouter', 'groq'].includes(localSettings.provider);
    if (needsKey && !localSettings.apiKey && !localSettings.apiKeys?.[localSettings.provider]) {
      setAvailableModels([]);
      return;
    }

    setIsLoadingModels(true);
    try {
      const key = localSettings.apiKeys?.[localSettings.provider] || localSettings.apiKey;
      const customUrl = localSettings.customUrls?.[localSettings.provider] || localSettings.customUrl;
      const res = await api.getModels(localSettings.provider, key, customUrl);
      if (res.models) {
        setAvailableModels(res.models);
      }
    } catch (e) {
      console.error("Erreur chargement modèles", e);
    } finally {
      setIsLoadingModels(false);
    }
  }, [localSettings.provider, localSettings.apiKeys, localSettings.apiKey, localSettings.customUrls, localSettings.customUrl]);

  // Fetch models whenever provider or settings change
  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  // Fermer le dropdown au clic extérieur
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredModels = availableModels.filter(m => 
    m.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="tab-content fade-in">
      <p className="settings-description">
        Choisissez le moteur d'intelligence artificielle de votre agent.
      </p>
      <div className="settings-group">
        <label>Fournisseur</label>
        <div className="provider-grid">
          {providers.map(p => (
            <button
              key={p.id}
              className={`provider-card ${localSettings.provider === p.id ? 'active' : ''}`}
              onClick={() => {
                setLocalSettings({ ...localSettings, provider: p.id, model: '' });
                setSearchTerm('');
              }}
            >
              {p.icon}
              <span>{p.name}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="settings-group">
        <div className="setting-header">
          <label className="setting-label">Modèle spécifique</label>
          <button 
            className="refresh-btn" 
            onClick={fetchModels} 
            title="Rafraîchir la liste"
            disabled={isLoadingModels}
          >
            <RotateCw size={14} className={isLoadingModels ? 'spin' : ''} />
          </button>
        </div>
        <div className="custom-model-select" ref={dropdownRef}>
          <div 
            className={`select-trigger ${isOpen ? 'active' : ''}`}
            onClick={() => !isLoadingModels && setIsOpen(!isOpen)}
          >
            <Cpu className="input-icon" size={16} />
            <span className={`selected-value ${!localSettings.model ? 'placeholder' : ''}`}>
              {isLoadingModels ? "Chargement..." : (localSettings.model || "Saisissez ou choisissez un modèle")}
            </span>
            <div className="input-suffix">
              {isLoadingModels ? <Loader2 size={14} className="animate-spin" /> : <ChevronDown size={14} className={isOpen ? 'rotate' : ''} />}
            </div>
          </div>

          {isOpen && (
            <div className="select-dropdown-menu obsidian-glass fade-in">
              <div className="search-box">
                <input 
                  type="text" 
                  placeholder="Rechercher un modèle..." 
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  autoFocus
                  onClick={e => e.stopPropagation()}
                />
              </div>
              <div className="models-list">
                {filteredModels.length > 0 ? (
                  filteredModels.map(m => (
                    <div 
                      key={m} 
                      className={`model-option ${localSettings.model === m ? 'active' : ''}`}
                      onClick={() => {
                        setLocalSettings({ ...localSettings, model: m });
                        setIsOpen(false);
                      }}
                    >
                      <span>{m}</span>
                      {localSettings.model === m && <Check size={14} className="check-icon" />}
                    </div>
                  ))
                ) : (
                  <div className="no-results">Aucun modèle trouvé</div>
                )}
              </div>
            </div>
          )}
        </div>
        <small>
          {availableModels.length > 0 
            ? `${availableModels.length} modèles détectés pour ce provider.` 
            : "Saisissez le nom du modèle manuellement ou attendez la détection."}
        </small>
      </div>

      {localSettings.provider === 'vllm' && (
        <div className="settings-group">
          <label htmlFor="custom-url">URL du Serveur Custom</label>
          <div className="input-wrapper">
            <Server className="input-icon" size={16} />
            <input
              id="custom-url"
              type="text"
              placeholder="http://votre-serveur:8000/v1"
              value={localSettings.customUrls?.[localSettings.provider] || 'http://localhost:8000/v1'}
              onChange={e => {
                const val = e.target.value;
                setLocalSettings(prev => ({
                  ...prev,
                  customUrls: { ...prev.customUrls, [prev.provider]: val },
                  // On garde customUrl synchronisé
                  customUrl: val
                }));
              }}
            />
          </div>
        </div>
      )}

      {localSettings.provider !== 'ollama' && (
        <div className="settings-group">
          <label htmlFor="api-key">Clé API {localSettings.provider === 'ollama_cloud' ? '(Obligatoire)' : ''}</label>
          <div className="input-wrapper">
            <Key className="input-icon" size={16} />
            <input
              id="api-key"
              type="password"
              placeholder={`Saisissez votre clé API pour ${localSettings.provider}...`}
              value={localSettings.apiKeys?.[localSettings.provider] || ''}
              onChange={e => {
                const val = e.target.value;
                setLocalSettings(prev => ({
                  ...prev,
                  apiKeys: { ...prev.apiKeys, [prev.provider]: val },
                  // On garde apiKey synchronisé pour la compatibilité descendante au cas où
                  apiKey: val
                }));
              }}
            />
          </div>
          <small className="security-note">Stockée localement dans votre navigateur uniquement.</small>
        </div>
      )}
    </div>
  );
};

export default LLMTab;
