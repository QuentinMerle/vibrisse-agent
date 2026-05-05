import React from 'react';

const SystemPulse = ({ healthStatus, contextUsage, contextLimit, llmSettings, isCollapsed }) => {
  const ramPercent = healthStatus?.ram?.percent || 0;
  const contextPercent = contextLimit > 0 ? (contextUsage / contextLimit) * 100 : 0;
  const isOllamaConnected = healthStatus?.ollama === 'connected';

  const formatValue = (val) => {
    if (val >= 1000) return (val / 1000).toFixed(1) + 'k';
    return val;
  };

  const getProviderColor = () => {
    const provider = llmSettings?.provider?.toLowerCase();
    if (provider === 'groq') return '#f97316'; // Orange
    if (provider === 'openrouter') return '#4f46e5'; // Indigo
    if (provider === 'ollama') return isOllamaConnected ? '#10b981' : '#ef4444';
    return '#3b82f6'; // Blue default for others
  };

  const statusColor = getProviderColor();

  if (isCollapsed) {
    return (
      <div className="sidebar-pulse collapsed" title={llmSettings?.provider || 'System Status'}>
        <div className="status-dot-pulse" style={{ 
          backgroundColor: statusColor, 
          boxShadow: `0 0 10px ${statusColor}` 
        }}></div>
      </div>
    );
  }

  return (
    <div className="sidebar-pulse">
      <div className="pulse-header">
        <span className="pulse-title">System Pulse</span>
        <div className="ollama-status" style={{ color: statusColor }}>
          <div className="status-dot-pulse" style={{ 
            backgroundColor: statusColor, 
            boxShadow: `0 0 10px ${statusColor}` 
          }}></div>
          <span>{llmSettings?.provider ? llmSettings.provider.charAt(0).toUpperCase() + llmSettings.provider.slice(1) : 'Ollama'}</span>
        </div>
      </div>

      <div className="pulse-metrics">
        <div 
          className="metric-item" 
          data-tooltip={`Plus la mémoire est pleine, plus l'agent risque d'oublier les premiers détails de la conversation.`}
        >
          <div className="metric-label">
            <span>Context Usage</span>
            <span className="metric-value">{formatValue(contextUsage)} / {formatValue(contextLimit)}</span>
          </div>
          <div className="metric-bar-bg">
            <div 
              className={`metric-bar-fill ${contextPercent > 90 ? 'critical' : contextPercent > 70 ? 'warning' : ''}`} 
              style={{ width: `${Math.min(contextPercent, 100)}%` }}
            ></div>
          </div>
        </div>

        {llmSettings?.provider?.toLowerCase() === 'ollama' && (
          <>
            <div 
              className="metric-item"
              data-tooltip={healthStatus?.ram ? `Détail : ${healthStatus.ram.used} GB utilisés sur ${healthStatus.ram.total} GB au total.` : "Chargement..."}
            >
              <div className="metric-label">
                <span>(V)RAM Usage</span>
                <span className="metric-value">{healthStatus?.ram?.used || 0} / {healthStatus?.ram?.total || 0} GB</span>
              </div>
              <div className="metric-bar-bg">
                <div 
                  className={`metric-bar-fill ${ramPercent > 90 ? 'critical' : ramPercent > 75 ? 'warning' : ''}`} 
                  style={{ width: `${ramPercent}%` }}
                ></div>
              </div>
            </div>

            {healthStatus?.ram?.swap_used > 0.1 && (
              <div 
                className="metric-item"
                data-tooltip={`Attention : Ton Mac utilise le disque (Swap) car la RAM est saturée. Performance réduite.`}
              >
                <div className="metric-label">
                  <span style={{ color: '#fb7185' }}>⚠️ Swap Usage</span>
                  <span className="metric-value" style={{ color: '#fb7185' }}>{healthStatus.ram.swap_used} GB</span>
                </div>
                <div className="metric-bar-bg" style={{ height: '2px' }}>
                  <div 
                    className="metric-bar-fill critical" 
                    style={{ width: `${healthStatus.ram.swap_percent}%` }}
                  ></div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};


export default SystemPulse;
