import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { ChevronDown, HelpCircle, Eye, Globe, ShieldCheck, Check } from 'lucide-react';
import VibrisseAvatar from './chat/VibrisseAvatar';
import { api } from '../services/api';
import './ChatHeader.css';


const ChatHeader = ({ config, availableModels, selectedModel, contextUsage, contextLimit, onSelectModel, onResetSession, llmSettings }) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [dynamicFeatures, setDynamicFeatures] = useState({ vision: false, search: false, expert_review: true });
  const dropdownRef = useRef(null);

  const displayModel = llmSettings?.provider && llmSettings.provider !== 'ollama' 
    ? llmSettings.model || 'DEFAULT'
    : selectedModel;

  const currentProvider = llmSettings?.provider || 'ollama';

  // Fetch capabilities dynamically
  useEffect(() => {
    const fetchCaps = async () => {
      try {
        const caps = await api.getCapabilities(currentProvider, displayModel);
        setDynamicFeatures(caps);
      } catch (err) {
        console.error("Erreur récup capabilities:", err);
      }
    };
    fetchCaps();
  }, [currentProvider, displayModel]);

  // Fermer le dropdown si on clique ailleurs ou sur Echap
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
      
      if (isOpen) {
        const items = dropdownRef.current?.querySelectorAll('.dropdown-item');
        if (!items || items.length === 0) return;
        
        const currentIndex = Array.from(items).indexOf(document.activeElement);
        
        if (event.key === "ArrowDown") {
          event.preventDefault();
          const nextIndex = (currentIndex + 1) % items.length;
          items[nextIndex].focus();
        } else if (event.key === "ArrowUp") {
          event.preventDefault();
          const prevIndex = (currentIndex - 1 + items.length) % items.length;
          items[prevIndex].focus();
        }
      } else if (event.key === "ArrowDown" && document.activeElement === dropdownRef.current?.querySelector('.dropdown-trigger')) {
        // Ouvrir le menu avec la flèche du bas
        event.preventDefault();
        setIsOpen(true);
        setTimeout(() => {
          const firstItem = dropdownRef.current?.querySelector('.dropdown-item');
          firstItem?.focus();
        }, 0);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const models = availableModels.length > 0 ? availableModels : [config.model];

  return (
    <header className="header">
      <div className="header-left">
        <div className="logo-wrap">
          <VibrisseAvatar size={20} containerSize={36} />
        </div>
        <span className="brand-name">{t('header.brand')}</span>
        <button className="help-trigger" data-tooltip={t('header.help_tooltip')} aria-label={t('header.help_tooltip')}>
          <HelpCircle size={14} className="help-icon" aria-hidden="true" />
        </button>
      </div>

      <div className="header-right">
        <div className="model-status-group">
          {/* Model Selector / Display */}
          {llmSettings?.provider && llmSettings.provider !== 'ollama' ? (
            <div className="model-display-static">
              <span className="current-model">
                {(llmSettings.provider === 'vllm' ? 'CUSTOM' : llmSettings.provider.toUpperCase())} : {displayModel.toUpperCase()}
              </span>
            </div>
          ) : (
            <div className="custom-dropdown" ref={dropdownRef}>
              <button 
                className={`dropdown-trigger ${isOpen ? 'active' : ''}`}
                onClick={() => setIsOpen(!isOpen)}
                aria-haspopup="listbox"
                aria-expanded={isOpen}
                aria-label={t('header.model_label', { model: selectedModel })}
              >
                <span className="current-model">{displayModel.toUpperCase()}</span>
                <ChevronDown size={14} className={`dropdown-icon ${isOpen ? 'open' : ''}`} aria-hidden="true" />
              </button>

              {isOpen && (
                <div className="dropdown-menu" role="listbox">
                  {models.map((m) => (
                    <button 
                      key={m} 
                      className={`dropdown-item ${m === selectedModel ? 'active' : ''}`}
                      role="option"
                      aria-selected={m === selectedModel}
                      onClick={() => {
                        onSelectModel(m);
                        setIsOpen(false);
                      }}
                    >
                      <span className="model-name">{m.toUpperCase()}</span>
                      {m === selectedModel && <Check size={14} className="check-icon" aria-hidden="true" />}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
          
          <div className="capabilities-group">
            <div className={`capability-dot ${!dynamicFeatures.vision ? 'disabled' : ''}`} data-tooltip={dynamicFeatures.vision ? t('header.vision_active') : t('header.vision_inactive')}>
              <Eye size={12} />
              {dynamicFeatures.vision && <span className="active-dot" />}
            </div>
            
            <div className={`capability-dot ${!dynamicFeatures.search ? 'disabled' : ''}`} data-tooltip={dynamicFeatures.search ? t('header.search_active') : t('header.search_inactive')}>
              <Globe size={12} />
              {dynamicFeatures.search && <span className="active-dot" />}
            </div>
            
            <div className={`capability-dot ${!dynamicFeatures.expert_review ? 'disabled' : ''}`} data-tooltip={dynamicFeatures.expert_review ? t('header.expert_active') : t('header.expert_inactive')}>
              <ShieldCheck size={12} />
              {dynamicFeatures.expert_review && <span className="active-dot" />}
            </div>
          </div>
        </div>
        
        <div className="header-divider" />
        
        <button 
          className="clean-cache-btn" 
          onClick={onResetSession}
          data-tooltip={t('header.reset_session')}
          aria-label={t('header.reset_session')}
        >
          {t('header.reset_btn')}
        </button>
      </div>
    </header>
  );
};

export default ChatHeader;
