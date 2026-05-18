import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import VibrisseAvatar from '../chat/VibrisseAvatar';
import PersonaCard from './PersonaCard';
import { Zap } from 'lucide-react';
import { api } from '../../services/api';
import './OnboardingWizard.css';

const OnboardingWizard = ({ isOpen, onClose, onComplete, updateSettings, updateTargetPath, updateSelectedModel }) => {
  const { t } = useTranslation();
  const [step, setStep] = useState(1);
  const [discovery, setDiscovery] = useState(null);
  const [selectedPersona, setSelectedPersona] = useState('generalist');
  const [targetPath, setTargetPath] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pullingModels, setPullingModels] = useState({}); // {modelName: true/false}
  const [isSuccess, setIsSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchDiscovery();
    }
  }, [isOpen]);

  const fetchDiscovery = async () => {
    try {
      const res = await fetch('/api/system/discovery');
      const data = await res.json();
      setDiscovery(data);
      
      // Si on a un profil 'hero' (modèle déjà installé), on le sélectionne par défaut
      if (data.recommendations?.profiles?.some(p => p.id === 'hero')) {
        setSelectedPersona('hero');
      }
    } catch (err) {
      console.error("Discovery failed", err);
    }
  };

  // Polling pendant le téléchargement des modèles
  useEffect(() => {
    let interval;
    const isAnyPulling = Object.values(pullingModels).some(v => v === true);
    
    if (isOpen && isAnyPulling) {
      interval = setInterval(fetchDiscovery, 5000);
    }
    return () => clearInterval(interval);
  }, [isOpen, pullingModels]);

  if (!isOpen) return null;

  // Sécurité : on attend que la discovery soit chargée pour éviter les crashs au changement d'étape
  if (!discovery && step > 1) {
    return (
      <div className="onboarding-overlay">
        <div className="onboarding-modal obsidian-glass" style={{ alignItems: 'center', justifyContent: 'center' }}>
          <div className="spinner-mini" />
          <p style={{ marginTop: '10px', color: 'var(--text-muted)' }}>{t('settings.status_verifying')}</p>
        </div>
      </div>
    );
  }

  const handleNext = () => setStep(s => s + 1);
  const handleBack = () => setStep(s => s - 1);

  const handlePull = async (modelName, e) => {
    e.stopPropagation();
    setPullingModels(prev => ({ ...prev, [modelName]: true }));
    try {
      const res = await fetch('/api/system/models/pull', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelName })
      });
      const data = await res.json();
      if (data.status === 'success') {
        // Optionnel : on pourrait rafraîchir la liste après un délai ou via un intervalle
      }
    } catch (err) {
      console.error("Pull failed", err);
    }
  };

  const handleFinish = async () => {
    setIsLoading(true);
    try {
      const profile = discovery.recommendations.profiles.find(p => p.id === selectedPersona);
      
      // Sauvegarder les paramètres côté frontend et backend
      await api.updateGlobalModel({
        model: profile.model,
        provider: 'ollama',
        active_persona: selectedPersona
      });

      await updateSettings({ 
        model: profile.model,
        provider: 'ollama'
      });

      if (updateSelectedModel) {
        await updateSelectedModel(profile.model);
      }

      if (targetPath) {
        await updateTargetPath(targetPath);
      }

      // Marquer comme terminé côté Backend (Source de vérité)
      await fetch('/api/system/onboarding/complete', { method: 'POST' });

      localStorage.setItem('vibrisse_onboarded', 'true');
      
      setIsSuccess(true);
      
      // Petit délai pour savourer le succès avant le reload
      setTimeout(() => {
        if (onComplete) onComplete();
        if (onClose) onClose();
        window.location.reload();
      }, 2000);
      
    } catch (err) {
      console.error("Finish failed", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBrowse = async () => {
    try {
      const res = await fetch('/api/system/pick-directory');
      const data = await res.json();
      if (data.status === 'success') {
        setTargetPath(data.path);
      }
    } catch (err) {
      console.error("Browse failed", err);
    }
  };

  const isModelInstalled = (modelName) => {
    if (!discovery?.installed_models) return false;
    return discovery.installed_models.includes(modelName);
  };

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="wizard-title">
      <div className="onboarding-modal obsidian-glass">
        <div className="onboarding-header">
          <div className="step-indicator">{t('onboarding.step_of', { current: step, total: 4 })}</div>
          <div className="progress-bar" role="progressbar" aria-valuenow={step} aria-valuemin="1" aria-valuemax="4">
            <div className="progress-fill" style={{ width: `${(step/4)*100}%` }}></div>
          </div>
        </div>

        <div className="onboarding-content">
          {isSuccess ? (
            <div className="step-fade-in success-step">
              <div className="success-icon">✨</div>
              <h2 className="display-font">Vibrisse is Ready!</h2>
              <p className="text-muted">Your surgical engineering studio is now fully configured. Prepare for takeoff...</p>
            </div>
          ) : step === 1 && (
            <div className="step-fade-in welcome-step">
              <h1 id="wizard-title" className="display-font">{t('onboarding.welcome_title')}</h1>
              <p className="text-muted">{t('onboarding.welcome_subtitle')}</p>
              <div className="welcome-hero">
                 <div className="hero-glow"></div>
                 <VibrisseAvatar size={120} containerSize={180} variant="transparent" />
              </div>
              <button 
                className="btn-primary-large" 
                onClick={handleNext} 
                disabled={!discovery}
                aria-label={t('onboarding.welcome_btn')}
              >
                {!discovery ? (
                  <div className="btn-loader-container">
                    <div className="spinner-mini white" />
                    <span>{t('settings.status_verifying')}</span>
                  </div>
                ) : (
                  t('onboarding.welcome_btn')
                )}
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="step-fade-in">
              <h2 id="wizard-title" className="display-font">{t('onboarding.hw_title')}</h2>
              <p className="text-muted">{t('onboarding.hw_subtitle')}</p>
              
              <div className="hardware-grid">
                <div className="hw-card" role="region" aria-label="RAM info">
                  <span className="hw-icon" aria-hidden="true">🧠</span>
                  <div className="hw-info">
                    <label>{t('onboarding.hw_ram')}</label>
                    <div className="hw-value">{discovery?.available_ram_gb} <small>GB FREE</small></div>
                    <div className="hw-sub">Total: {discovery?.ram_gb} GB</div>
                  </div>
                </div>
                <div className="hw-card" role="region" aria-label="GPU info">
                  <span className="hw-icon" aria-hidden="true">⚡</span>
                  <div className="hw-info">
                    <label>{t('onboarding.hw_gpu')}</label>
                    <div className="hw-value">{discovery?.gpu.vram_gb} GB</div>
                    <div className="hw-type">{discovery?.gpu.type}</div>
                  </div>
                </div>
              </div>

              <div className="tier-badge">
                {t('onboarding.tier_detected')} <span className={`tier-${discovery?.recommendations?.tier}`}>
                  {discovery?.recommendations?.tier ? discovery.recommendations.tier.toUpperCase() : '...'}
                </span>
              </div>

              <div className="step-actions">
                <button className="btn-ghost" onClick={handleBack}>{t('onboarding.back')}</button>
                <button className="btn-primary" onClick={handleNext}>{t('onboarding.next')}</button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="step-fade-in">
              <h2 id="wizard-title" className="display-font">{t('onboarding.persona_title')}</h2>
              <p className="text-muted">{t('onboarding.persona_subtitle')}</p>
              
              <div className="persona-carousel-wrapper">
                {!discovery?.ollama_installed && (
                  <div className="ollama-warning obsidian-glass">
                    <Zap size={20} className="warning-icon" />
                    <div className="warning-text">
                      <strong>Ollama not detected!</strong>
                      <p>Please install Ollama to download and run models locally.</p>
                      <a href="https://ollama.com/download" target="_blank" rel="noreferrer" className="btn-ollama-download">
                        Download Ollama
                      </a>
                    </div>
                  </div>
                )}
                <div className="persona-grid horizontal" role="radiogroup" aria-label="Select persona">
                  {discovery?.recommendations.profiles.map(p => (
                    <PersonaCard 
                      key={p.id}
                      profile={p}
                      isActive={selectedPersona === p.id}
                      isInstalled={isModelInstalled(p.model)}
                      isPulling={pullingModels[p.model]}
                      onSelect={setSelectedPersona}
                      onPull={handlePull}
                    />
                  ))}
                </div>
              </div>

              <div className="step-actions">
                <button className="btn-ghost" onClick={handleBack}>{t('onboarding.back')}</button>
                <button className="btn-primary" onClick={handleNext}>{t('onboarding.next')}</button>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="step-fade-in">
              <h2 id="wizard-title" className="display-font">{t('onboarding.workspace_title')}</h2>
              <p className="text-muted">{t('onboarding.workspace_subtitle')}</p>
              
              <div className="path-input-group">
                <input 
                  type="text" 
                  value={targetPath} 
                  onChange={(e) => setTargetPath(e.target.value)}
                  placeholder={t('onboarding.path_placeholder')}
                  className="obsidian-input"
                  aria-label={t('onboarding.workspace_title')}
                />
                <button className="btn-secondary" onClick={handleBrowse}>{t('onboarding.browse_btn')}</button>
              </div>

              <div className="final-notice">
                <p>{t('onboarding.final_notice')}</p>
              </div>

              <div className="step-actions">
                <button className="btn-ghost" onClick={handleBack}>{t('onboarding.back')}</button>
                <button className="btn-primary" onClick={handleFinish} disabled={isLoading}>
                  {isLoading ? t('onboarding.initializing') : t('onboarding.finish_btn')}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;
