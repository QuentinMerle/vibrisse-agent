import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Cpu, ShieldCheck, Plug, Globe, Zap, User } from 'lucide-react';
import { api } from '../services/api';
import LLMTab from './settings/LLMTab';
import MCPTab from './settings/MCPTab';
import SystemTab from './settings/SystemTab';
import './SettingsModal.css';

const SettingsModal = ({ isOpen, onClose, settings, onSave, onResetOnboarding }) => {
  const { t, i18n } = useTranslation();
  const [localSettings, setLocalSettings] = useState(settings);
  const [isValidating, setIsValidating] = useState(false);
  const [validationStatus, setValidationStatus] = useState(null);
  
  // Onglets et MCP State
  const [activeTab, setActiveTab] = useState('llm'); // 'llm', 'mcp', 'general', 'system'
  const [mcpServers, setMcpServers] = useState([]);
  const [isConnectingMcp, setIsConnectingMcp] = useState(false);
  
  // Formulaire nouveau serveur MCP
  const [newMcpId, setNewMcpId] = useState('');
  const [newMcpCmd, setNewMcpCmd] = useState('');
  const [newMcpArgs, setNewMcpArgs] = useState('');

  useEffect(() => {
    setLocalSettings(settings);
    setValidationStatus(null);
    if (isOpen) fetchMcpStatus();
  }, [settings, isOpen]);

  const fetchMcpStatus = async () => {
    try {
      const res = await api.getMcpStatus();
      if (res.status === 'success') {
        setMcpServers(res.details || []);
      }
    } catch (e) {
      console.error("Erreur status MCP", e);
    }
  };

  if (!isOpen) return null;

  const handleTestConnection = async () => {
    setIsValidating(true);
    setValidationStatus(null);
    try {
      const result = await api.validateLLM(localSettings);
      if (result.status === 'success') setValidationStatus('success');
      else {
        setValidationStatus('error');
        alert(`Échec : ${result.message}`);
      }
    } catch (err) {
      setValidationStatus('error');
      alert(`Erreur : ${err.message}`);
    } finally {
      setIsValidating(false);
    }
  };

  const handleConnectMcp = async () => {
    if (!newMcpId || !newMcpCmd) return alert("ID et Commande requis");
    setIsConnectingMcp(true);
    try {
      const args = newMcpArgs.split(" ").filter(a => a.trim() !== "");
      const res = await api.connectMcp({
        server_id: newMcpId,
        command: newMcpCmd,
        args: args
      });
      if (res.status === 'success') {
        setNewMcpId('');
        setNewMcpCmd('');
        setNewMcpArgs('');
        await fetchMcpStatus();
      } else {
        alert("Erreur MCP : " + res.message);
      }
    } catch (e) {
      alert("Erreur réseau");
    } finally {
      setIsConnectingMcp(false);
    }
  };

  const handleDisconnectMcp = async (id) => {
    await api.disconnectMcp(id);
    await fetchMcpStatus();
  };

  const handleSave = () => {
    onSave(localSettings);
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content obsidian-glass settings-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div className="header-title">
            <ShieldCheck className="header-icon" />
            <h2>{t('settings.title')}</h2>
          </div>
          <button className="close-btn" onClick={onClose} aria-label={t('common.close')}>
            <X size={20} />
          </button>
        </div>

        <div className="tabs-container">
          <button className={`tab-btn ${activeTab === 'llm' ? 'active' : ''}`} onClick={() => setActiveTab('llm')}>
            <Cpu size={14} /> {t('settings.tabs_llm')}
          </button>
          <button className={`tab-btn ${activeTab === 'mcp' ? 'active' : ''}`} onClick={() => setActiveTab('mcp')}>
            <Plug size={14} /> {t('settings.tabs_mcp')}
          </button>
          <button className={`tab-btn ${activeTab === 'general' ? 'active' : ''}`} onClick={() => setActiveTab('general')}>
            <Globe size={14} /> {t('settings.tabs_general')}
          </button>
          <button className={`tab-btn ${activeTab === 'system' ? 'active' : ''}`} onClick={() => setActiveTab('system')}>
            <Zap size={14} /> System
          </button>
        </div>

        <div className="modal-body">
          {activeTab === 'llm' ? (
            <LLMTab 
              localSettings={localSettings} 
              setLocalSettings={setLocalSettings} 
            />
          ) : activeTab === 'mcp' ? (
            <MCPTab 
              mcpServers={mcpServers}
              fetchMcpStatus={fetchMcpStatus}
              handleDisconnectMcp={handleDisconnectMcp}
              handleConnectMcp={handleConnectMcp}
              isConnectingMcp={isConnectingMcp}
              newMcpId={newMcpId} setNewMcpId={setNewMcpId}
              newMcpCmd={newMcpCmd} setNewMcpCmd={setNewMcpCmd}
              newMcpArgs={newMcpArgs} setNewMcpArgs={setNewMcpArgs}
            />
          ) : activeTab === 'system' ? (
            <SystemTab onResetOnboarding={onResetOnboarding} />
          ) : (
            <div className="settings-tab-content">
              <div className="settings-section">
                <h3 className="section-title"><Zap size={14} /> {t('settings.section_features')}</h3>
                <div className="settings-grid">
                  <div className="setting-control-card">
                    <div className="card-info">
                      <span className="card-label">Sovereign Routing</span>
                      <span className="card-hint">Arbitrage intelligent Local/Cloud</span>
                    </div>
                    <label className="switch">
                      <input 
                        type="checkbox" 
                        checked={localSettings.sovereignRouting}
                        onChange={(e) => setLocalSettings({ ...localSettings, sovereignRouting: e.target.checked })}
                      />
                      <span className="slider round"></span>
                    </label>
                  </div>

                  <div className="setting-control-card">
                    <div className="card-info">
                      <span className="card-label">Vision Mode</span>
                      <span className="card-hint">Analyse d'images multimodale</span>
                    </div>
                    <label className="switch">
                      <input 
                        type="checkbox" 
                        checked={localSettings.enableVision}
                        onChange={(e) => setLocalSettings({ ...localSettings, enableVision: e.target.checked })}
                      />
                      <span className="slider round"></span>
                    </label>
                  </div>

                  <div className="setting-control-card">
                    <div className="card-info">
                      <span className="card-label">Expert Review</span>
                      <span className="card-hint">Vérification post-génération</span>
                    </div>
                    <label className="switch">
                      <input 
                        type="checkbox" 
                        checked={localSettings.enableExpertReview}
                        onChange={(e) => setLocalSettings({ ...localSettings, enableExpertReview: e.target.checked })}
                      />
                      <span className="slider round"></span>
                    </label>
                  </div>
                </div>
              </div>

              <div className="settings-section">
                <h3 className="section-title"><User size={14} /> {t('settings.persona_label') || 'Rôle Actif (Persona)'}</h3>
                <p className="settings-description">{t('settings.persona_hint') || 'Configure le comportement global de l\'agent'}</p>
                <div className="persona-selector-grid">
                  {[
                    { id: 'generalist', title: t('settings.persona_generalist') || 'Généraliste', icon: '🧭', desc: 'Polyvalent & rapide' },
                    { id: 'coder', title: t('settings.persona_coder') || 'Expert Coder', icon: '💻', desc: 'Refactoring & debug' },
                    { id: 'architect', title: t('settings.persona_architect') || 'System Architect', icon: '🏗️', desc: 'Design & plans' },
                    { id: 'writer', title: t('settings.persona_writer') || 'Tech Writer', icon: '📚', desc: 'Documentation' },
                    { id: 'analyst', title: t('settings.persona_analyst') || 'Data Scientist', icon: '📊', desc: 'Logique & données' }
                  ].map(p => (
                    <button
                      key={p.id}
                      type="button"
                      className={`persona-setting-card ${localSettings.activePersona === p.id || (!localSettings.activePersona && p.id === 'generalist') ? 'active' : ''}`}
                      onClick={() => setLocalSettings({ ...localSettings, activePersona: p.id })}
                    >
                      <span className="persona-card-icon">{p.icon}</span>
                      <div className="persona-card-meta">
                        <h4>{p.title.split(' (')[0]}</h4>
                        <p>{p.desc}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="settings-section">
                <h3 className="section-title"><Plug size={14} /> {t('settings.section_api_keys')}</h3>
                <div className="api-keys-list">
                  <div className="api-key-item">
                    <div className="key-header">
                      <Globe size={12} />
                      <label>Tavily Search</label>
                    </div>
                    <input 
                      type="password" 
                      className="settings-input"
                      placeholder="tvly-..."
                      value={localSettings.tavilyApiKey || ''}
                      onChange={(e) => setLocalSettings({ ...localSettings, tavilyApiKey: e.target.value })}
                    />
                  </div>

                  <div className="api-key-item">
                    <div className="key-header">
                      <Cpu size={12} />
                      <label>GitHub Integration</label>
                    </div>
                    <input 
                      type="password" 
                      className="settings-input"
                      placeholder="ghp_..."
                      value={localSettings.githubToken || ''}
                      onChange={(e) => setLocalSettings({ ...localSettings, githubToken: e.target.value })}
                    />
                  </div>
                </div>
              </div>

              <div className="settings-section">
                <h3 className="section-title"><Globe size={14} /> {t('settings.language')}</h3>
                <div className="language-selector-grid">
                  <button 
                    className={`lang-btn ${i18n.language === 'fr' ? 'active' : ''}`}
                    onClick={() => i18n.changeLanguage('fr')}
                  >
                    <span className="lang-iso">FR</span>
                    <span className="lang-name">{t('settings.language_fr')}</span>
                  </button>
                  <button 
                    className={`lang-btn ${i18n.language === 'en' ? 'active' : ''}`}
                    onClick={() => i18n.changeLanguage('en')}
                  >
                    <span className="lang-iso">EN</span>
                    <span className="lang-name">{t('settings.language_en')}</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          {activeTab === 'llm' && (
            <div className="validation-info">
              {isValidating && <span className="validating-text"><div className="spinner-mini" /> {t('settings.status_verifying')}</span>}
              {validationStatus === 'success' && <span className="success-text">✓ {t('settings.status_success')}</span>}
              {validationStatus === 'error' && <span className="error-text">✗ {t('settings.status_error')}</span>}
            </div>
          )}
          <div style={{flex: 1}}></div>
          <button className="secondary-btn" onClick={onClose}>{t('settings.btn_cancel')}</button>
          {activeTab === 'llm' && (
            <button 
              className="test-btn" 
              onClick={handleTestConnection} 
              disabled={isValidating || (localSettings.provider !== 'ollama' && localSettings.provider !== 'vllm' && !localSettings.apiKey)}
            >
              {t('settings.btn_test')}
            </button>
          )}
          <button className="primary-btn" onClick={handleSave}>{t('settings.btn_save')}</button>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
