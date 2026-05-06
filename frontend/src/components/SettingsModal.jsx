import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Cpu, ShieldCheck, Plug, Globe } from 'lucide-react';
import { api } from '../services/api';
import LLMTab from './settings/LLMTab';
import MCPTab from './settings/MCPTab';
import './SettingsModal.css';

const SettingsModal = ({ isOpen, onClose, settings, onSave }) => {
  const { t, i18n } = useTranslation();
  const [localSettings, setLocalSettings] = useState(settings);
  const [isValidating, setIsValidating] = useState(false);
  const [validationStatus, setValidationStatus] = useState(null);
  
  // Onglets et MCP State
  const [activeTab, setActiveTab] = useState('llm'); // 'llm' ou 'mcp'
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
        </div>

        <div className="modal-body" style={{ minHeight: '350px' }}>
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
          ) : (
            <div className="settings-tab-content">
              <div className="setting-group">
                <label className="setting-label">
                  <Globe size={14} style={{ marginRight: '8px' }} />
                  {t('settings.language')}
                </label>
                <div className="language-selector-grid">
                  <button 
                    className={`lang-btn ${i18n.language === 'fr' ? 'active' : ''}`}
                    onClick={() => i18n.changeLanguage('fr')}
                  >
                    🇫🇷 {t('settings.language_fr')}
                  </button>
                  <button 
                    className={`lang-btn ${i18n.language === 'en' ? 'active' : ''}`}
                    onClick={() => i18n.changeLanguage('en')}
                  >
                    🇺🇸 {t('settings.language_en')}
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
              disabled={isValidating || (localSettings.provider !== 'ollama' && !localSettings.apiKey)}
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
