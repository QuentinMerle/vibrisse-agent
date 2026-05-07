import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Cpu, Zap, RotateCcw } from 'lucide-react';

const SystemTab = ({ onResetOnboarding }) => {
  const { t } = useTranslation();
  const [discovery, setDiscovery] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDiscovery();
  }, []);

  const fetchDiscovery = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/system/discovery');
      const data = await res.json();
      setDiscovery(data);
    } catch (e) {
      console.error("Discovery error", e);
    } finally {
      setLoading(false);
    }
  };

  const resetOnboarding = () => {
    if (onResetOnboarding) {
      onResetOnboarding();
    }
  };

  if (loading) return <div className="tab-loading"><div className="spinner-mini" /> {t('settings.status_verifying')}</div>;

  return (
    <div className="settings-tab-content step-fade-in" role="tabpanel" aria-label={t('system_tab.title')}>
      <div className="system-overview">
        <div className="hw-card-mini" role="region" aria-label="RAM">
          <Cpu size={18} className="hw-icon-mini" aria-hidden="true" />
          <div className="hw-details">
            <span className="hw-label">{t('system_tab.ram_label')}</span>
            <span className="hw-value">{discovery?.available_ram_gb} <small>GB FREE</small></span>
            <span className="hw-sub">Total: {discovery?.ram_gb} GB</span>
          </div>
        </div>
        
        <div className="hw-card-mini" role="region" aria-label="GPU">
          <Zap size={18} className="hw-icon-mini" aria-hidden="true" />
          <div className="hw-details">
            <span className="hw-label">{t('system_tab.gpu_label')}</span>
            <span className="hw-value">{discovery?.gpu.vram_gb} GB</span>
            <span className="hw-sub">{discovery?.gpu.type}</span>
          </div>
        </div>
      </div>

      <div className="tier-section">
         <span className="tier-label">{t('system_tab.diagnostic')}</span>
         <div className={`tier-indicator tier-${discovery?.recommendations?.tier}`}>
            {discovery?.recommendations?.tier ? discovery.recommendations.tier.toUpperCase() : '...'} CONFIGURATION
         </div>
         <p className="tier-desc">
            {t('system_tab.tier_desc', { tier: discovery?.recommendations.tier })}
         </p>
      </div>

      <div className="danger-zone-settings">
        <button className="btn-reset-onboarding" onClick={resetOnboarding} aria-label={t('system_tab.reset_btn')}>
          <RotateCcw size={14} aria-hidden="true" /> {t('system_tab.reset_btn')}
        </button>
      </div>
    </div>
  );
};

export default SystemTab;
